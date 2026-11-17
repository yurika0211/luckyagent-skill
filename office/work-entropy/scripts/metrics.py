"""Deterministic model entropy, evidence load, interval accounting and rates."""
from common import stamp, clock, entropy, personal_remaining, union, subtract, seconds


def scope_items(state, project_id=None, task_id=None):
    if bool(project_id) == bool(task_id):
        raise ValueError("select exactly one project or task")
    if task_id:
        if task_id not in state["tasks"]:
            raise ValueError("unknown task")
        project_id = state["tasks"][task_id]["project_id"]
        tasks = {task_id}
    else:
        if project_id not in state["projects"]:
            raise ValueError("unknown project")
        tasks = {k for k, t in state["tasks"].items() if t["project_id"] == project_id}
    atoms = {k: a for k, a in state["atoms"].items() if a["project_id"] == project_id
             and (not task_id or task_id in a["task_ids"])}
    return project_id, tasks, atoms


def entropy_view(atoms):
    relevant = [a for a in atoms.values() if a["kind"] != "competency"]
    return dict(model_bit_upper_sum=sum(entropy(a["remaining"]) or 0 for a in relevant),
                unquantified=[a["id"] for a in relevant if a["remaining"] is None],
                awaiting_verification=[a["id"] for a in relevant if not a["resolved"]],
                dependent_atoms=[a["id"] for a in relevant if a["dependencies"]],
                additive_approximation=True)


def focus_window(state, tasks, start, end):
    """Union duplicates; subtract contradictory topic/task/phase overlaps globally."""
    all_rows = [f for f in state["focus"] if not f["invalid"]]
    conflicts, active = [], []
    for f in sorted(all_rows, key=lambda x: stamp(x["start"])):
        a, b = stamp(f["start"]), stamp(f["end"])
        active = [g for g in active if stamp(g["end"]) > a]
        key = (f["task_id"], f["topic"], f["phase"])
        for g in active:
            if key != (g["task_id"], g["topic"], g["phase"]):
                conflicts.append((max(a, stamp(g["start"])), min(b, stamp(g["end"]))))
        active.append(f)
    good, uncertain, waiting, learning, selected = [], [], [], [], []
    for f in all_rows:
        if f["task_id"] not in tasks:
            continue
        a, b = max(start, stamp(f["start"])), min(end, stamp(f["end"]))
        if b <= a:
            continue
        selected.append(f)
        if f["phase"] == "wait":
            waiting.append((a, b))
        elif f["confirmed"] and f["precision"] == "second":
            good.append((a, b))
            if f["phase"] in ("understand", "verify", "rework"):
                learning.append((a, b))
        else:
            uncertain.append((a, b))
    all_selected = good + uncertain + waiting
    scoped_conflicts = [(max(a, c), min(b, d)) for a, b in conflicts
                        for c, d in all_selected if max(a, c) < min(b, d)]
    return dict(seconds=seconds(subtract(good, conflicts)),
                learning_seconds=seconds(subtract(learning, conflicts)),
                uncertain_seconds=seconds(subtract(uncertain, good)),
                wait_seconds=seconds(waiting), conflict_seconds=seconds(scoped_conflicts),
                rows=selected,
                open_intervals=[f for f in state["active"].values() if f["task_id"] in tasks])


def summary(state, project_id=None, task_id=None, now=None, baseline_id=None):
    now = stamp(now or clock())
    project_id, tasks, atoms = scope_items(state, project_id, task_id)
    scope = "task:" + task_id if task_id else "project:" + project_id
    baselines = state["baselines"].get(scope, [])
    baseline = (next((b for b in baselines if b["id"] == baseline_id), None)
                if baseline_id else (baselines[-1] if baselines else None))
    if baseline_id and baseline is None:
        raise ValueError("baseline does not exist in this scope")
    task_rows = [state["tasks"][tid] for tid in tasks]
    end = min(now, max(stamp(t["completed_at"]) for t in task_rows)) if (
        task_rows and all(t["completed_at"] for t in task_rows)) else now
    receipts = [stamp(t["received_at"]) for t in task_rows if t.get("received_at")]
    dates_complete = bool(task_rows) and len(receipts) == len(task_rows)
    start = min(receipts) if dates_complete else (stamp(baseline["at"]) if baseline else end)
    if start > end:
        raise ValueError("observation endpoint precedes scope start")
    focus = focus_window(state, tasks, start, end)
    budget = sum(a["budget"] for a in atoms.values())
    remaining = sum(personal_remaining(a) for a in atoms.values())
    initial_load = old_remaining = gain = baseline_bits = None
    old_ids = set(baseline["atoms"]) if baseline else set()
    new_ids = sorted(atoms.keys() - old_ids) if baseline else []
    work = {k: w for k, w in state["works"].items() if w["task_id"] in tasks}
    work_weights = baseline["works"] if baseline else {k: w["weight"] for k, w in work.items()}
    total_weight = sum(work_weights.values())
    completed_weight = sum(weight for k, weight in work_weights.items() if work[k]["verified"])
    new_work = sorted(work.keys() - work_weights.keys())
    if baseline:
        baseline_bits = sum(entropy(b["remaining"]) or 0 for aid, b in baseline["atoms"].items()
                            if atoms[aid]["kind"] != "competency")
        initial_load = sum(a["budget"] * (1 - a["grade"]) for a in baseline["atoms"].values())
        old_remaining = sum(personal_remaining(atoms[k], b["budget"]) for k, b in baseline["atoms"].items())
        gain = initial_load - old_remaining
    reasons = []
    if not baseline:
        reasons.append("no_baseline")
    if task_rows and not all(t["coverage"] for t in task_rows):
        reasons.append("time_coverage_not_confirmed")
    if focus["open_intervals"]:
        reasons.append("open_focus_interval_not_counted")
    if focus["uncertain_seconds"]:
        reasons.append("estimated_or_unconfirmed_time")
    if focus["conflict_seconds"]:
        reasons.append("conflicting_topic_or_phase_intervals")
    if not focus["seconds"]:
        reasons.append("no_confirmed_focus_time")
    if baseline:
        for aid, b in baseline["atoms"].items():
            a = atoms[aid]
            if a["grade"] <= b["grade"]:
                continue
            assessment = a.get("assessment") or {}
            if stamp(a["assessed_at"]) > end:
                reasons.append("assessment_outside_task_window:" + aid)
            matched = any(aid in f["atom_ids"] and f["confirmed"] and
                f["precision"] == "second" and f["phase"] != "wait" and
                stamp(f["start"]) <= stamp(a["assessed_at"]) for f in focus["rows"])
            if not matched:
                reasons.append("unpaired_gain:" + aid)
            if assessment.get("task_id") not in tasks:
                reasons.append("transferred_or_unattributed_gain:" + aid)
    reasons = sorted(set(reasons))
    hours = focus["seconds"] / 3600
    narrow = gain / hours if gain is not None and hours and not reasons else None
    calendar_days = (end - min(receipts)).total_seconds() / 86400 if dates_complete else None
    broad = gain / calendar_days if gain is not None and calendar_days and not reasons else None
    mixed_execution = any(f["phase"] in ("execute", "mixed") for f in focus["rows"])
    all_project_atoms = {k: a for k, a in state["atoms"].items() if a["project_id"] == project_id}
    return dict(model_version="0.2", scope=scope, observed_at=now.isoformat(),
        project_model_entropy=entropy_view(all_project_atoms), scope_model_entropy=entropy_view(atoms),
        unmodeled_modules=state["projects"][project_id]["unmodeled"],
        baseline_id=baseline["id"] if baseline else None,
        baseline_scope_model_bits=baseline_bits,
        baseline_personal_load=initial_load, personal_remaining_load=remaining,
        baseline_scope_remaining=old_remaining, personal_net_gain=gain,
        personal_budget=budget, verified_fraction=(budget - remaining) / budget if budget else None,
        unassessed_atoms=[k for k, a in atoms.items() if not a["assessed"]],
        new_atoms_since_baseline=new_ids, new_work_since_baseline=new_work,
        baseline_delivery_fraction=completed_weight / total_weight if total_weight else None,
        required_work_open=[k for k, w in work.items() if w["required"] and not w["verified"]],
        completed_tasks=[t["id"] for t in task_rows if t["completed_at"]],
        calendar_days=calendar_days, confirmed_focus_hours=hours,
        uncertain_focus_hours=focus["uncertain_seconds"] / 3600,
        wait_hours=focus["wait_seconds"] / 3600, conflict_hours=focus["conflict_seconds"] / 3600,
        open_focus_intervals=len(focus["open_intervals"]), rate_blockers=reasons,
        narrow_rate=narrow, broad_rate=broad,
        learning_rate=narrow if not mixed_execution else None,
        atoms=[dict(id=k, question=a["question"], kind=a["kind"], topic=a["topic"],
            budget=a["budget"], model_bits=entropy(a["remaining"]), grade=a["grade"],
            assessed=a["assessed"], resolved=a["resolved"], closure=a["closure"],
            resolution=a["resolution"], assessment=a["assessment"],
            unmet_dependencies=[d for d in a["dependencies"] if not state["atoms"][d]["resolved"]])
            for k, a in sorted(atoms.items())])
