"""Locked, hash-chained append-only JSONL ledger with idempotent commands."""
from pathlib import Path
import copy
import fcntl
import hashlib
import json
import os
import uuid
from common import ACTORS, SOURCES, MODEL_VERSION, clock, iso, stamp, text
from domain import initial, reduce_one


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def default_store():
    return Path.home() / ".local/share/work-entropy"


class Store:
    def __init__(self, directory=None):
        self.directory = Path(directory or default_store()).expanduser()
        self.path = self.directory / "events.jsonl"

    def _load(self):
        state, events, prev, keys = initial(), [], "0" * 64, set()
        if not self.path.exists():
            return state, events
        raw = self.path.read_bytes()
        if raw and not raw.endswith(b"\n"):
            raise ValueError("ledger has a partial final line; restore from backup, do not truncate silently")
        for seq, line in enumerate(raw.decode().splitlines(), 1):
            e = json.loads(line)
            required = {"schema_version", "model_version", "seq", "event_id", "key", "intent_hash",
                        "type", "data", "actor", "source", "occurred_at", "recorded_at", "prev_hash", "hash"}
            if set(e) != required or e["schema_version"] != 1 or e["model_version"] != MODEL_VERSION:
                raise ValueError(f"unsupported event schema at line {seq}")
            if e["seq"] != seq or e["prev_hash"] != prev:
                raise ValueError(f"broken ledger sequence/hash chain at line {seq}")
            value = {k: v for k, v in e.items() if k != "hash"}
            if digest(value) != e["hash"]:
                raise ValueError(f"ledger hash mismatch at line {seq}")
            if e["key"] in keys:
                raise ValueError("duplicate idempotency key in ledger")
            keys.add(e["key"])
            self._validate_envelope(e)
            reduce_one(state, copy.deepcopy(e))
            events.append(e)
            prev = e["hash"]
        return state, events

    @staticmethod
    def _validate_envelope(e):
        if e["actor"] not in ACTORS:
            raise ValueError("invalid actor")
        if not isinstance(e["source"], dict) or set(e["source"]) != {"kind", "ref"}:
            raise ValueError("source needs kind and ref")
        if e["source"]["kind"] not in SOURCES:
            raise ValueError("invalid source kind")
        text(e["source"]["ref"], "source reference")
        text(e["key"], "idempotency key")
        text(e["type"], "event type")
        if stamp(e["occurred_at"]) > stamp(e["recorded_at"]):
            raise ValueError("observed event cannot be dated in the future")
        if e["type"] == "forecast.record" and e["occurred_at"] != e["recorded_at"]:
            raise ValueError("forecast snapshots cannot be backdated")

    def read(self):
        if not self.path.exists():
            raise ValueError("ledger not initialized")
        with (self.directory / "ledger.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_SH)
            return self._load()

    def append(self, event_type, data, source, actor="assistant", at=None, key=None):
        intent = digest(dict(type=event_type, data=data, source=source, actor=actor, at=at))
        if not self.directory.exists() and event_type != "ledger.init":
            raise ValueError("initialize the ledger first")
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory / "ledger.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            state, events = self._load()
            key = key or str(uuid.uuid4())
            existing = next((e for e in events if e["key"] == key), None)
            if existing:
                if existing["intent_hash"] != intent:
                    raise ValueError("idempotency key was already used for a different command")
                return existing, False
            recorded = clock()
            e = dict(schema_version=1, model_version=MODEL_VERSION, seq=len(events) + 1,
                event_id=str(uuid.uuid4()), key=key, intent_hash=intent, type=event_type,
                data=copy.deepcopy(data), actor=actor, source=source,
                occurred_at=iso(at) if at else recorded, recorded_at=recorded,
                prev_hash=events[-1]["hash"] if events else "0" * 64)
            self._validate_envelope(e)
            reduce_one(copy.deepcopy(state), copy.deepcopy(e))
            e["hash"] = digest(e)
            blob = (canonical(e) + "\n").encode()
            with self.path.open("ab") as stream:
                stream.write(blob)
                stream.flush()
                os.fsync(stream.fileno())
            return e, True
