"""Conditional scenarios, empirical resampling and auditable forecast outcomes."""
import math
import random
from statistics import median
from common import number, clock, stamp
from metrics import summary, focus_window

MIN_SAMPLES = 10  # Engineering gate, not a statistical guarantee.


def percentile(values, fraction):
    values = sorted(values)
    x = (len(values) - 1) * fraction
    lo = math.floor(x)
    hi = math.ceil(x)
    return values[lo] + (values[hi] - values[lo]) * (x - lo)


def valid_samples(state, task):
    result = []
    for sample in state["samples"]:
        if sample["project_id"] != task["project_id"] or sample["work_type"] != task["work_type"]:
            continue
        if sample["task_id"] == task["id"]:
            continue
        historical = state["tasks"][sample["task_id"]]
        if not historical["completed_at"]:
            continue
        current = summary(state, task_id=historical["id"])
        signature = {a["id"]: a["grade"] for a in state["atoms"].values()
                     if historical["id"] in a["task_ids"]}
        if (current["rate_blockers"] or current["baseline_id"] != sample["baseline_id"]
                or signature != sample["grade_signature"]
                or not math.isclose(current["confirmed_focus_hours"], sample["focus_hours"], abs_tol=1e-9)):
            continue
        result.append(sample)
    return result


def forecast(state, task_id, mode="decomposed", known_execution_hours=0,
             daily_focus_hours=None, rate_range=None, seed=17, simulations=2000, now=None):
    if task_id not in state["tasks"]:
        raise ValueError("unknown task")
    task = state["tasks"][task_id]
    if task["completed_at"]:
        raise ValueError("task is already completed")
    if mode not in ("decomposed", "whole"):
        raise ValueError("mode must be decomposed or whole")
    number(known_execution_hours, "known_execution_hours")
    if daily_focus_hours is not None:
        number(daily_focus_hours, "daily_focus_hours", positive=True)
        if daily_focus_hours > 24:
            raise ValueError("daily focus cannot exceed 24 hours")
    if type(seed) is not int or type(simulations) is not int or not 100 <= simulations <= 100000:
        raise ValueError("seed must be integer; simulations must be between 100 and 100000")
    if mode == "whole" and (known_execution_hours or rate_range is not None):
        raise ValueError("whole-package mode cannot add execution hours or entropy-rate assumptions")
    report = summary(state, task_id=task_id, now=now)
    result = dict(task_id=task_id, mode=mode, model_version="0.2", stage="data_insufficient",
        remaining_load=report["personal_remaining_load"], baseline_id=report["baseline_id"],
        known_execution_hours=known_execution_hours, daily_focus_hours=daily_focus_hours,
        sample_count=0, sample_ids=[], focus_hours=None, calendar_days=None,
        calibrated=False, assumptions=["conditional on current scope and measurement model",
            "dependencies, external blocking and future scope growth are not simulated",
            "no universal information-points-to-hours conversion"])
    if report["baseline_id"] is None:
        result["reason"] = "需要先建立带证据的任务基线。"
        return result
    if rate_range is not None:
        if not isinstance(rate_range, (list, tuple)) or len(rate_range) != 2:
            raise ValueError("rate_range needs [low, high]")
        low, high = rate_range
        number(low, "rate low", positive=True)
        number(high, "rate high", positive=True)
        if low > high:
            raise ValueError("rate range is reversed")
        result.update(stage="explicit_scenario", rate_range=[low, high],
            focus_hours=dict(optimistic=result["remaining_load"] / high + known_execution_hours,
                             conservative=result["remaining_load"] / low + known_execution_hours),
            reason="调用者显式给定速率的情景演算，不是已校准概率预测。")
    elif mode == "decomposed" and result["remaining_load"] == 0:
        result.update(stage="known_execution_only", focus_hours=dict(estimate=known_execution_hours),
                      reason="信息负荷已验证，执行工时仍为调用者明确给定的估计。")
    else:
        samples = valid_samples(state, task)
        if mode == "decomposed":
            samples = [s for s in samples if s["learning_rate"] is not None and s["learning_rate"] > 0]
        else:
            if (not task["coverage"] or report["open_focus_intervals"] or report["conflict_hours"]
                    or report["uncertain_focus_hours"]):
                result["reason"] = "整包预测需要确认目标任务已投入工时；先结束计时并核对覆盖范围。"
                return result
            # Target is unfinished: completed packages shorter than current age cannot
            # represent its conditional remaining duration.
            samples = [s for s in samples if s["focus_hours"] > report["confirmed_focus_hours"]]
        result.update(sample_count=len(samples), sample_ids=[s["task_id"] for s in samples])
        if len(samples) < MIN_SAMPLES:
            result["reason"] = f"同类有效闭环样本 {len(samples)} 个，低于工程门槛 {MIN_SAMPLES}；不生成 P50/P85。"
            return result
        rng = random.Random(seed)
        values = []
        for _ in range(simulations):
            sample = rng.choice(samples)
            if mode == "decomposed":
                value = result["remaining_load"] / sample["learning_rate"] + known_execution_hours
            else:
                # Whole mode represents one comparable work package, never arbitrary project size.
                value = sample["focus_hours"] - report["confirmed_focus_hours"]
            values.append(value)
        result.update(stage="empirical_uncalibrated", seed=seed, simulations=simulations,
            focus_hours=dict(p50=percentile(values, .5), p85=percentile(values, .85)),
            reason="同项目、同工作类型的历史重采样；经验分位数尚非可靠概率承诺。")
        if mode == "whole":
            result["assumptions"].append("whole mode assumes target is one similarly sized package; age beyond history needs review")
    if daily_focus_hours is not None and result["focus_hours"]:
        result["calendar_days"] = {k: v / daily_focus_hours for k, v in result["focus_hours"].items()}
        result["assumptions"].append("calendar days assume the supplied constant daily capacity, without additional waiting")
    return result


def calibration(state, task_id=None):
    rows, excluded = [], []
    for item in state.get("forecasts", []):
        if task_id and item["task_id"] != task_id:
            continue
        f = item["result"]
        task = state["tasks"][item["task_id"]]
        if not task["completed_at"] or not f.get("focus_hours") or "p85" not in f["focus_hours"]:
            continue
        report = summary(state, task_id=task["id"])
        atom_ids = sorted(a["id"] for a in state["atoms"].values() if task["id"] in a["task_ids"])
        if report["rate_blockers"] or atom_ids != item["atom_ids"] or report["baseline_id"] != f["baseline_id"]:
            excluded.append(dict(id=item["id"], reason="scope/baseline changed or final time evidence incomplete"))
            continue
        start, end = stamp(item["at"]), stamp(task["completed_at"])
        if end < start:
            excluded.append(dict(id=item["id"], reason="completion precedes forecast"))
            continue
        actual = focus_window(state, {task["id"]}, start, end)["seconds"] / 3600
        p50, p85 = f["focus_hours"]["p50"], f["focus_hours"]["p85"]
        rows.append(dict(forecast_id=item["id"], task_id=task["id"], actual_hours=actual,
                         p50=p50, p85=p85, within_p85=actual <= p85,
                         abs_error=abs(actual - p50)))
    n = len(rows)
    return dict(n=n, rows=rows, excluded=excluded,
        p85_coverage=sum(r["within_p85"] for r in rows) / n if n else None,
        median_absolute_error_hours=median(r["abs_error"] for r in rows) if n else None,
        brier_at_p85=sum((.85 - int(r["within_p85"])) ** 2 for r in rows) / n if n else None,
        interpretation="观察样本的诊断值；少量样本或同任务重复预测不能证明概率已校准。")
