"""Deterministic event reducer. No time reads, network calls, or inferred assessments."""
import copy
import math
from common import (GRADES, PHASES, fields, text, strings, number, stamp, iso,
                    require_evidence)

PROOF = {"artifact", "test", "user_message", "observed_action"}
PERSONAL_PROOF = {"user_message", "observed_action"}


def initial():
    return dict(initialized=False, projects={}, tasks={}, atoms={}, works={},
                baselines={}, focus=[], active={}, samples=[])


def found(state, collection, key):
    text(key, collection + " id")
    if key not in state[collection]:
        raise ValueError(f"unknown {collection}: {key}")
    return state[collection][key]


def new_id(state, collection, key):
    text(key, "id")
    if key in state[collection]:
        raise ValueError(f"{collection} id already exists: {key}")


def validate_links(state, task, topic, atom_ids):
    found(state, "tasks", task)
    text(topic, "topic")
    strings(atom_ids, "atom_ids")
    for aid in atom_ids:
        a = found(state, "atoms", aid)
        if task not in a["task_ids"] or a["topic"] != topic:
            raise ValueError("focus atom must belong to this task and topic")


def make_focus(state, d, event, start, end=None):
    fields(d, ("task_id", "topic", "phase", "atom_ids", "confirmed", "precision"),
           ("start", "end"))
    validate_links(state, d["task_id"], d["topic"], d["atom_ids"])
    completed = state["tasks"][d["task_id"]]["completed_at"]
    if completed and (end is None or stamp(end) > stamp(completed)):
        raise ValueError("reopen the task before recording work after its completion")
    if d["phase"] not in PHASES or d["precision"] not in ("second", "estimated"):
        raise ValueError("invalid phase or precision")
    if type(d["confirmed"]) is not bool:
        raise ValueError("confirmed must be boolean")
    if event["actor"] != "user":
        raise ValueError("human focus must use actor=user; automation is not human time")
    if d["confirmed"]:
        require_evidence(event, {"explicit_timer", "manual_report", "user_message", "observed_action"})
    if end and stamp(end) <= stamp(start):
        raise ValueError("focus end must be later than start")
    return dict(id=event["event_id"], task_id=d["task_id"], topic=d["topic"],
                phase=d["phase"], atom_ids=d["atom_ids"], start=iso(start),
                end=iso(end) if end else None, confirmed=d["confirmed"],
                precision=d["precision"], actor="user", source=event["source"], invalid=False)


def close_focus(state, event):
    actor = event["actor"]
    if actor not in state["active"]:
        raise ValueError("there is no active focus interval for this actor")
    active = state["active"][actor]
    if stamp(event["occurred_at"]) <= stamp(active["start"]):
        raise ValueError("stop/switch must be later than focus start")
    require_evidence(event, {"explicit_timer", "manual_report", "user_message", "observed_action"})
    active["end"] = event["occurred_at"]
    state["focus"].append(active)
    del state["active"][actor]


def reduce_one(state, e):
    t, d, at = e["type"], e["data"], e["occurred_at"]
    if t == "ledger.init":
        fields(d)
        if state["initialized"]:
            raise ValueError("ledger already initialized")
        state["initialized"] = True
        return
    if not state["initialized"]:
        raise ValueError("initialize the ledger first")
    if t == "project.add":
        fields(d, ("id", "title"), ("unmodeled",))
        new_id(state, "projects", d["id"])
        text(d["title"], "title")
        strings(d.get("unmodeled", []), "unmodeled")
        state["projects"][d["id"]] = dict(d, unmodeled=d.get("unmodeled", []))
    elif t == "task.add":
        fields(d, ("id", "project_id", "title", "work_type"), ("received_at", "received_date"))
        new_id(state, "tasks", d["id"])
        found(state, "projects", d["project_id"])
        for key in ("title", "work_type"):
            text(d[key], key)
        received = d.get("received_at")
        if received:
            received = iso(received)
            if stamp(received) > stamp(at):
                raise ValueError("receipt cannot be later than task registration")
        if d.get("received_date"):
            from datetime import date
            date.fromisoformat(d["received_date"])
        state["tasks"][d["id"]] = dict(d, received_at=received, completed_at=None,
                                        coverage=False, coverage_source=None, created_at=at)
    elif t == "atom.add":
        fields(d, ("id", "project_id", "task_ids", "topic", "kind", "question", "closure"),
               ("candidates", "budget", "dependencies", "group"))
        new_id(state, "atoms", d["id"])
        found(state, "projects", d["project_id"])
        strings(d["task_ids"], "task_ids", empty=False)
        for task in d["task_ids"]:
            if found(state, "tasks", task)["project_id"] != d["project_id"]:
                raise ValueError("task and atom projects differ")
        if d["kind"] not in ("fact", "decision", "competency"):
            raise ValueError("atom kind must be fact, decision, or competency")
        for key in ("topic", "question", "closure"):
            text(d[key], key)
        question = " ".join(d["question"].casefold().split())
        if any(a["project_id"] == d["project_id"] and a["kind"] == d["kind"]
               and " ".join(a["question"].casefold().split()) == question for a in state["atoms"].values()):
            raise ValueError("same question already has an atom; link it to the task instead")
        candidates = d.get("candidates")
        if candidates is not None:
            strings(candidates, "candidates", empty=False)
        deps = strings(d.get("dependencies", []), "dependencies")
        for dep in deps:
            if found(state, "atoms", dep)["project_id"] != d["project_id"]:
                raise ValueError("dependency must belong to same project")
        budget = d.get("budget", max(1, math.log2(len(candidates))) if candidates else 1)
        number(budget, "budget", positive=True)
        state["atoms"][d["id"]] = dict(d, candidates=candidates, remaining=candidates,
            budget=budget, dependencies=deps, grade=0, assessed=False, assessed_at=None,
            resolved=False, resolution=None, assessment=None)
    elif t == "atom.link":
        fields(d, ("id", "task_id"))
        a = found(state, "atoms", d["id"])
        task = found(state, "tasks", d["task_id"])
        if task["project_id"] != a["project_id"]:
            raise ValueError("link cannot cross projects")
        if d["task_id"] not in a["task_ids"]:
            a["task_ids"].append(d["task_id"])
    elif t == "atom.resolve":
        fields(d, ("id", "remaining", "reason"))
        a = found(state, "atoms", d["id"])
        require_evidence(e, PROOF)
        text(d["reason"], "reason")
        strings(d["remaining"], "remaining", empty=False)
        if a["remaining"] is None or not set(d["remaining"]) <= set(a["remaining"]):
            raise ValueError("resolve only removes existing alternatives; reopen or add a scoped atom")
        a.update(remaining=d["remaining"], resolved=len(d["remaining"]) == 1,
                 resolution=dict(source=e["source"], reason=d["reason"], at=at))
    elif t == "atom.assess":
        fields(d, ("id", "grade", "reason"), ("task_id",))
        a = found(state, "atoms", d["id"])
        grade = number(d["grade"], "grade")
        if grade not in GRADES:
            raise ValueError(f"grade must be one of {GRADES}")
        require_evidence(e, PERSONAL_PROOF)
        text(d["reason"], "reason")
        task_id = d.get("task_id")
        if task_id is None and len(a["task_ids"]) == 1:
            task_id = a["task_ids"][0]
        if task_id not in a["task_ids"]:
            raise ValueError("assessment needs an owning task_id linked to the atom")
        a.update(grade=grade, assessed=True, assessed_at=at,
                 assessment=dict(source=e["source"], reason=d["reason"], at=at, task_id=task_id))
    elif t == "atom.reopen":
        fields(d, ("id", "reason"), ("reset_personal",))
        a = found(state, "atoms", d["id"])
        text(d["reason"], "reason")
        reset = d.get("reset_personal", True)
        if type(reset) is not bool:
            raise ValueError("reset_personal must be boolean")
        a.update(remaining=a["candidates"], resolved=False, resolution=None)
        if reset:
            a.update(grade=0, assessed=False, assessed_at=None, assessment=None)
    elif t == "work.add":
        fields(d, ("id", "task_id", "title", "acceptance"), ("weight", "required"))
        new_id(state, "works", d["id"])
        task = found(state, "tasks", d["task_id"])
        if task["completed_at"]:
            raise ValueError("reopen task before adding work")
        text(d["title"], "title")
        strings(d["acceptance"], "acceptance", empty=False)
        number(d.get("weight", 1), "weight", positive=True)
        if type(d.get("required", True)) is not bool:
            raise ValueError("required must be boolean")
        state["works"][d["id"]] = dict(d, weight=d.get("weight", 1),
                                        required=d.get("required", True), verified=False)
    elif t == "work.verify":
        fields(d, ("id", "verified", "reason"))
        work = found(state, "works", d["id"])
        if type(d["verified"]) is not bool:
            raise ValueError("verified must be boolean")
        require_evidence(e, PROOF)
        text(d["reason"], "reason")
        work.update(verified=d["verified"], verification=e["source"], reason=d["reason"])
        if not d["verified"]:
            state["tasks"][work["task_id"]]["completed_at"] = None
    elif t == "baseline.add":
        fields(d, ("scope", "id", "reason"))
        text(d["reason"], "reason")
        text(d["id"], "baseline id")
        kind, sep, key = d["scope"].partition(":")
        if not sep or kind not in ("project", "task"):
            raise ValueError("scope must be project:ID or task:ID")
        found(state, kind + "s", key)
        atoms = [a for a in state["atoms"].values() if
                 (a["project_id"] == key if kind == "project" else key in a["task_ids"])]
        if not atoms:
            raise ValueError("baseline needs at least one scoped atom")
        if any(b["id"] == d["id"] for bs in state["baselines"].values() for b in bs):
            raise ValueError("baseline id already exists")
        works = [w for w in state["works"].values() if
                 (state["tasks"][w["task_id"]]["project_id"] == key if kind == "project" else w["task_id"] == key)]
        snapshot = dict(id=d["id"], at=at, reason=d["reason"], atoms={a["id"]:
            dict(budget=a["budget"], grade=a["grade"], assessed=a["assessed"],
                 remaining=copy.deepcopy(a["remaining"])) for a in atoms},
            works={w["id"]: w["weight"] for w in works})
        state["baselines"].setdefault(d["scope"], []).append(snapshot)
    elif t in ("focus.start", "focus.switch", "focus.add"):
        if t == "focus.add":
            if "start" not in d or "end" not in d:
                raise ValueError("import needs start and end")
            if stamp(d["end"]) > stamp(at):
                raise ValueError("imported interval ends after event time")
            state["focus"].append(make_focus(state, d, e, d["start"], d["end"]))
        else:
            interval = make_focus(state, d, e, at)
            if t == "focus.switch":
                close_focus(state, e)
            elif e["actor"] in state["active"]:
                raise ValueError("focus already active; pause or switch first")
            state["active"][e["actor"]] = interval
    elif t == "focus.stop":
        fields(d, (), ("reason",))
        close_focus(state, e)
    elif t == "focus.invalidate":
        fields(d, ("id", "reason"))
        text(d["reason"], "reason")
        interval = next((x for x in state["focus"] if x["id"] == d["id"]), None)
        if interval is None:
            raise ValueError("unknown closed focus interval")
        interval.update(invalid=True, invalidation=d["reason"])
    elif t == "task.coverage":
        fields(d, ("id", "complete", "reason"))
        task = found(state, "tasks", d["id"])
        if type(d["complete"]) is not bool:
            raise ValueError("complete must be boolean")
        require_evidence(e, {"user_message", "manual_report", "observed_action"})
        text(d["reason"], "reason")
        task.update(coverage=d["complete"], coverage_source=e["source"])
    elif t == "task.complete":
        fields(d, ("id",))
        task = found(state, "tasks", d["id"])
        require_evidence(e, PROOF)
        works = [w for w in state["works"].values() if w["task_id"] == d["id"] and w["required"]]
        if not works or not all(w["verified"] for w in works):
            raise ValueError("task needs at least one required work package and all must be verified")
        if any(f["task_id"] == d["id"] for f in state["active"].values()):
            raise ValueError("stop the task's focus timer before completing it")
        if task.get("received_at") and stamp(at) < stamp(task["received_at"]):
            raise ValueError("completion precedes receipt")
        task["completed_at"] = at
    elif t == "task.reopen":
        fields(d, ("id", "reason"))
        text(d["reason"], "reason")
        found(state, "tasks", d["id"])["completed_at"] = None
    elif t == "task.sample":
        fields(d, ("id",))
        from metrics import summary
        task = found(state, "tasks", d["id"])
        if not task["completed_at"]:
            raise ValueError("only completed tasks may create history samples")
        report = summary(state, task_id=d["id"], now=at)
        if report["rate_blockers"] or report["confirmed_focus_hours"] <= 0:
            raise ValueError("sample needs fully paired and confirmed progress/time")
        signature = (d["id"], report["baseline_id"])
        if any((s["task_id"], s["baseline_id"]) == signature for s in state["samples"]):
            raise ValueError("task/baseline already sampled")
        state["samples"].append(dict(task_id=d["id"], project_id=task["project_id"],
            work_type=task["work_type"], baseline_id=report["baseline_id"],
            gain=report["personal_net_gain"], narrow_rate=report["narrow_rate"],
            learning_rate=report["learning_rate"], calendar_days=report["calendar_days"],
            focus_hours=report["confirmed_focus_hours"], at=at,
            grade_signature={a["id"]: a["grade"] for a in state["atoms"].values() if d["id"] in a["task_ids"]}))
    elif t == "forecast.record":
        fields(d, ("task_id", "options"))
        if found(state, "tasks", d["task_id"])["completed_at"]:
            raise ValueError("cannot forecast an already completed task")
        from forecast import forecast
        result = forecast(state, d["task_id"], now=e["recorded_at"], **d["options"])
        state.setdefault("forecasts", []).append(dict(id=e["event_id"], at=e["recorded_at"],
            task_id=d["task_id"], result=result,
            atom_ids=sorted(a["id"] for a in state["atoms"].values() if d["task_id"] in a["task_ids"])))
    else:
        raise ValueError(f"unknown event type: {t}")
