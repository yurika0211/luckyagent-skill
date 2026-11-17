#!/usr/bin/env python3
"""CLI for the work-entropy event ledger and explicit focus controls."""
import argparse
import json
import sys
from common import ACTORS, SOURCES, PHASES
from store import Store, canonical


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--store", help="Personal ledger directory; defaults to ~/.local/share/work-entropy")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("audit")
    event = sub.add_parser("event", help="Append a schema-validated event")
    event.add_argument("type")
    payload = event.add_mutually_exclusive_group(required=True)
    payload.add_argument("--data-file", help="UTF-8 JSON object; preferred for multiline content")
    payload.add_argument("--data-json", help="JSON object")
    focus = sub.add_parser("focus", help="Explicit human timer; never reconstruct silence as focus")
    focus.add_argument("action", choices=("start", "pause", "switch", "import", "invalidate"))
    focus.add_argument("--task")
    focus.add_argument("--topic")
    focus.add_argument("--phase", choices=PHASES, default="understand")
    focus.add_argument("--atom", action="append", default=[])
    focus.add_argument("--start")
    focus.add_argument("--end")
    focus.add_argument("--estimated", action="store_true")
    focus.add_argument("--unconfirmed", action="store_true")
    focus.add_argument("--id")
    focus.add_argument("--reason", default="explicit focus control")
    for command in (event, focus):
        command.add_argument("--at", help="Known event time with timezone; omitted means now")
        command.add_argument("--key", help="Stable source-event key for safe reprocessing")
        command.add_argument("--source-kind", choices=SOURCES,
                             default="user_message" if command is event else "explicit_timer")
        command.add_argument("--source-ref", required=True, help="Message/artifact/timer reference")
        command.add_argument("--actor", choices=ACTORS,
                             default="assistant" if command is event else "user")
    return p


def main():
    p = parser()
    a = p.parse_args()
    store = Store(a.store)
    try:
        if a.command == "audit":
            state, events = store.read()
            print(canonical(dict(valid=True, events=len(events), projects=len(state["projects"]),
                                 tasks=len(state["tasks"]), atoms=len(state["atoms"]))))
            return
        if a.command == "init":
            state, events = store.read() if store.path.exists() else (None, [])
            if state and state["initialized"]:
                e, created = events[0], False
            else:
                e, created = store.append("ledger.init", {}, {"kind": "system", "ref": "ledger initializer"},
                                          key="ledger.init")
        else:
            if a.command == "event":
                if a.data_file:
                    with open(a.data_file, encoding="utf-8") as stream:
                        data = json.load(stream)
                else:
                    data = json.loads(a.data_json)
                event_type = a.type
            elif a.action in ("start", "switch", "import"):
                if not a.task or not a.topic:
                    raise ValueError("focus needs --task and --topic")
                data = dict(task_id=a.task, topic=a.topic, phase=a.phase, atom_ids=a.atom,
                            confirmed=not a.unconfirmed,
                            precision="estimated" if a.estimated else "second")
                event_type = "focus.add" if a.action == "import" else "focus." + a.action
                if a.action == "import":
                    if not a.start or not a.end:
                        raise ValueError("import needs --start and --end")
                    data.update(start=a.start, end=a.end)
            elif a.action == "pause":
                data, event_type = {"reason": a.reason}, "focus.stop"
            else:
                if not a.id:
                    raise ValueError("invalidate needs --id")
                data, event_type = dict(id=a.id, reason=a.reason), "focus.invalidate"
            e, created = store.append(event_type, data,
                {"kind": a.source_kind, "ref": a.source_ref}, actor=a.actor, at=a.at, key=a.key)
        print(canonical(dict(created=created, event_id=e["event_id"], seq=e["seq"],
                             type=e["type"], occurred_at=e["occurred_at"])))
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f"work-entropy: {error}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
