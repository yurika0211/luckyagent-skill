"""Shared validation and interval operations; Python standard library only."""
from datetime import datetime, timezone
import math

MODEL_VERSION = "0.2"
GRADES = (0, 0.25, 0.5, 0.75, 1)
PHASES = ("understand", "execute", "verify", "rework", "wait", "mixed")
ACTORS = ("user", "assistant", "automation", "external")
SOURCES = ("user_message", "assistant_message", "artifact", "test", "observed_action",
           "explicit_timer", "manual_report", "chat_inference", "system")


def stamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO8601 string with timezone")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp needs an explicit timezone")
    return dt.astimezone(timezone.utc)


def iso(value):
    return stamp(value).isoformat().replace("+00:00", "Z")


def clock():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def text(value, name):
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{name} must be a nonempty, trimmed string")
    if any(ord(c) < 32 for c in value):
        raise ValueError(f"{name} contains control characters")
    return value


def number(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < 0 or (positive and value == 0):
        raise ValueError(f"{name} must be {'positive' if positive else 'nonnegative'}")
    return value


def strings(values, name, empty=True):
    if not isinstance(values, list) or (not empty and not values):
        raise ValueError(f"{name} must be a {'nonempty ' if not empty else ''}list")
    for v in values:
        text(v, name)
    if len(set(values)) != len(values):
        raise ValueError(f"{name} contains duplicates")
    return values


def fields(data, required=(), optional=()):
    if not isinstance(data, dict):
        raise ValueError("event data must be an object")
    missing, extra = set(required) - data.keys(), data.keys() - set(required) - set(optional)
    if missing or extra:
        raise ValueError(f"event fields: missing={sorted(missing)}, extra={sorted(extra)}")


def require_evidence(event, kinds):
    if event["source"]["kind"] not in kinds:
        raise ValueError(f"this action needs evidence from {sorted(kinds)}")


def union(intervals):
    merged = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def subtract(intervals, excluded):
    result = []
    for start, end in union(intervals):
        parts = [(start, end)]
        for a, b in union(excluded):
            next_parts = []
            for x, y in parts:
                if b <= x or a >= y:
                    next_parts.append((x, y))
                else:
                    if x < a:
                        next_parts.append((x, a))
                    if b < y:
                        next_parts.append((b, y))
            parts = next_parts
        result.extend(parts)
    return result


def seconds(intervals):
    return sum((b - a).total_seconds() for a, b in union(intervals))


def entropy(candidates):
    return None if candidates is None else math.log2(len(candidates))


def personal_remaining(atom, budget=None):
    return (atom["budget"] if budget is None else budget) * (1 - atom["grade"])
