#!/usr/bin/env python3
"""Render a reproducible status, conditional forecast, or calibration diagnostic."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from store import Store
from metrics import summary
from forecast import forecast, calibration

BLOCKERS = {
    "no_baseline": "未建立基线", "time_coverage_not_confirmed": "时间覆盖尚未核实",
    "open_focus_interval_not_counted": "仍有未结束计时，不推算静默期间",
    "estimated_or_unconfirmed_time": "存在估计或未确认区间",
    "conflicting_topic_or_phase_intervals": "不同主题、任务或活动类型的区间冲突",
    "no_confirmed_focus_time": "没有已确认的专注时间",
}


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def fmt(value, suffix=""):
    return "数据不足" if value is None else f"{value:.3g}{suffix}"


def markdown_status(r):
    lines = [f"# 工作熵报告：{cell(r['scope'])}", "",
        f"计量版本：{r['model_version']}；基线：{r['baseline_id'] or '未建立'}。", "",
        "| 指标 | 值 |", "|---|---|",
        f"| 项目模型熵（已建模项求和近似） | {fmt(r['project_model_entropy']['model_bit_upper_sum'], ' model_bit')} |",
        f"| 当前范围模型熵（基线 → 当前） | {fmt(r['baseline_scope_model_bits'])} → {fmt(r['scope_model_entropy']['model_bit_upper_sum'], ' model_bit')} |",
        f"| 个人剩余未验证负荷 | {fmt(r['personal_remaining_load'], ' 熵点')} |",
        f"| 相对基线的个人净进度 | {fmt(r['personal_net_gain'], ' 熵点')} |",
        f"| 基线交付验收率 | {fmt(None if r['baseline_delivery_fraction'] is None else 100*r['baseline_delivery_fraction'], '%')} |",
        "", "个人负荷是证据计分，不是脑内真实熵；未测不等于不会。理解与交付分别记录。", "",
        "| 时间与效率 | 值 |", "|---|---|",
        f"| 自然耗时 | {fmt(r['calendar_days'], ' 天')} |",
        f"| 已确认专注 | {fmt(r['confirmed_focus_hours'], ' 小时')} |",
        f"| 估计或未确认区间 | {fmt(r['uncertain_focus_hours'], ' 小时')} |",
        f"| 泛均消除率 | {fmt(r['broad_rate'], ' 熵点/天')} |",
        f"| 窄均消除率 | {fmt(r['narrow_rate'], ' 熵点/专注小时')} |", ""]
    if r["rate_blockers"]:
        lines.append("效率暂不计算：" + "；".join(
            BLOCKERS.get(x, x.replace("unpaired_gain:", "增益缺少配对工时：").replace(
                "transferred_or_unattributed_gain:", "增益来自其他任务或未归属："))
            for x in r["rate_blockers"]) + "。")
    lines += ["", f"未测原子点：{len(r['unassessed_atoms'])}；新增原子点：{len(r['new_atoms_since_baseline'])}；"
              f"新增工作包：{len(r['new_work_since_baseline'])}；未通过的必需工作包：{len(r['required_work_open'])}。"]
    if r["unmodeled_modules"]:
        lines.append("项目未覆盖：" + "、".join(cell(x) for x in r["unmodeled_modules"]) + "。")
    if r["scope_model_entropy"]["unquantified"]:
        lines.append("不可量化原子点：" + "、".join(r["scope_model_entropy"]["unquantified"]) + "；未按零未知处理。")
    lines += ["", "| 原子点 | 类型 | 模型熵 | 个人证据等级 | 项目状态 |", "|---|---|---|---|---|"]
    for a in r["atoms"][:5]:
        label = "未测" if not a["assessed"] else f"{a['grade']:g}（工程等级）"
        lines.append(f"| {cell(a['id'])}：{cell(a['question'])} | {a['kind']} | {fmt(a['model_bits'])} | {label} | {'已验证/决策关闭' if a['resolved'] else '待关闭'} |")
    if len(r["atoms"]) > 5:
        lines.append(f"\n共 {len(r['atoms'])} 个原子点，此处展示前 5 个；JSON 输出保留全部记录。")
    for a in r["atoms"][:5]:
        lines += ["", f"**{cell(a['id'])}** 验证条件：{cell(a['closure'])}。"]
        for label, evidence in [("项目证据", a["resolution"]), ("个人证据", a["assessment"])]:
            lines.append(f"{label}：" + (f"{cell(evidence['source']['ref'])}；{cell(evidence['reason'])}。" if evidence else "尚缺。"))
    return "\n".join(lines) + "\n"


def markdown_forecast(r):
    lines = [f"# 剩余时间估计：{cell(r['task_id'])}", "",
             f"阶段：{r['stage']}；同类样本：{r['sample_count']}；概率已校准：否。", "",
             r.get("reason", ""), ""]
    if r["focus_hours"]:
        lines += ["| 专注时间情景/经验分位数 | 小时 |", "|---|---|"]
        lines += [f"| {k} | {v:.3g} |" for k, v in r["focus_hours"].items()]
    else:
        lines.append("剩余专注时间：数据不足。")
    if r["calendar_days"]:
        lines += ["", f"按每日 {r['daily_focus_hours']:g} 小时投入的日历情景：" +
                  "，".join(f"{k}={v:.3g} 天" for k, v in r["calendar_days"].items()) + "。"]
    else:
        lines += ["", "日历时间：尚无明确每日投入假设，不生成日期。"]
    lines += ["", "条件：" + "；".join(r["assumptions"]) + "。"]
    return "\n".join(lines) + "\n"


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--store")
    sub = p.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status")
    scope = status.add_mutually_exclusive_group(required=True)
    scope.add_argument("--project")
    scope.add_argument("--task")
    status.add_argument("--baseline")
    f = sub.add_parser("forecast")
    f.add_argument("--task", required=True)
    f.add_argument("--mode", choices=("decomposed", "whole"), default="decomposed")
    f.add_argument("--known-execution-hours", type=float, default=0)
    f.add_argument("--daily-focus-hours", type=float)
    f.add_argument("--rate-range", nargs=2, type=float, metavar=("LOW", "HIGH"))
    f.add_argument("--seed", type=int, default=17)
    f.add_argument("--simulations", type=int, default=2000)
    f.add_argument("--record", action="store_true", help="Append a non-backdated forecast snapshot")
    f.add_argument("--source-ref", help="Required when recording a forecast")
    f.add_argument("--key", help="Idempotency key for forecast recording")
    c = sub.add_parser("calibration")
    c.add_argument("--task")
    for item in (status, f, c):
        item.add_argument("--format", choices=("markdown", "json"), default="markdown")
        item.add_argument("--output", help="Explicit destination; existing files require --replace")
        item.add_argument("--replace", action="store_true")
    return p


def main():
    p = parser()
    a = p.parse_args()
    try:
        store = Store(a.store)
        state, _ = store.read()
        if a.command == "status":
            result = summary(state, project_id=a.project, task_id=a.task, baseline_id=a.baseline)
            render = markdown_status
        elif a.command == "forecast":
            options = dict(mode=a.mode, known_execution_hours=a.known_execution_hours,
                daily_focus_hours=a.daily_focus_hours, rate_range=a.rate_range,
                seed=a.seed, simulations=a.simulations)
            if a.record:
                if not a.source_ref:
                    raise ValueError("--record requires --source-ref")
                event, _ = store.append("forecast.record", dict(task_id=a.task, options=options),
                    {"kind": "system", "ref": a.source_ref}, key=a.key)
                state, _ = store.read()
                result = next(f["result"] for f in state["forecasts"] if f["id"] == event["event_id"])
            else:
                result = forecast(state, a.task, **options)
            render = markdown_forecast
        else:
            result = calibration(state, a.task)
            render = lambda r: "# 预测回测\n\n```json\n" + json.dumps(r, ensure_ascii=False, indent=2) + "\n```\n"
        output = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n" if a.format == "json" else render(result)
        if a.output:
            dest = Path(a.output).expanduser()
            if dest.exists() and not a.replace:
                raise ValueError("output exists; use a new destination or explicitly pass --replace")
            dest.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=dest.parent, delete=False) as tmp:
                tmp.write(output)
                temp_path = tmp.name
            os.replace(temp_path, dest)
            print(str(dest))
        else:
            print(output, end="")
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f"work-entropy: {error}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
