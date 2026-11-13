#!/usr/bin/env python3
"""Glossary + per-user term frequency for plain-speak.

Terms come from references/*.tsv (human glossaries).
Counts come from local chat transcripts, stored in SQLite outside git.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REF = SKILL_DIR / "references"
DEFAULT_DB = Path.home() / ".claude" / "plain-speak" / "glossary.sqlite"
EXPLAIN_BELOW = 5

SKIP_USER = (
    "<local-command",
    "<command-",
    "Caveat:",
    "<system-reminder",
    "<task-notification",
)


def db_path() -> Path:
    return Path(os.environ.get("PLAIN_SPEAK_DB") or DEFAULT_DB)


def connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS terms (
            slug TEXT PRIMARY KEY,
            en TEXT NOT NULL,
            zh TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT '',
            one_liner TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS aliases (
            alias TEXT PRIMARY KEY,
            slug TEXT NOT NULL,
            FOREIGN KEY (slug) REFERENCES terms(slug)
        );
        CREATE TABLE IF NOT EXISTS term_freq (
            slug TEXT PRIMARY KEY,
            seen_count INTEGER NOT NULL DEFAULT 0,
            session_count INTEGER NOT NULL DEFAULT 0,
            first_seen TEXT,
            last_seen TEXT,
            source TEXT NOT NULL DEFAULT 'live',
            FOREIGN KEY (slug) REFERENCES terms(slug)
        );
        """
    )
    return con


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    rows = []
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return []
    header = lines[0].split("\t")
    for line in lines[1:]:
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        row = {header[i]: parts[i] if i < len(parts) else "" for i in range(len(header))}
        rows.append(row)
    return rows


def load_term_files() -> list[dict[str, str]]:
    """Priority: computerese, then cjk (overwrites), then overrides (overwrites)."""
    by_slug: dict[str, dict[str, str]] = {}
    for name, src_default in (
        ("computerese.tsv", "computerese"),
        ("cjk.tsv", "cjk"),
        ("overrides.tsv", "override"),
    ):
        for row in read_tsv(REF / name):
            slug = (row.get("slug") or "").strip()
            en = (row.get("en") or "").strip()
            zh = (row.get("zh") or "").strip()
            if not slug or not en or not zh:
                continue
            src = (row.get("source") or src_default).strip()
            note = (row.get("note") or "").strip()
            by_slug[slug] = {
                "slug": slug,
                "en": en,
                "zh": zh,
                "source": src,
                "one_liner": note,
            }
    return list(by_slug.values())


# Everyday English that also appears as glossary headwords. Matching them
# against chat inflates counts and attaches the wrong Chinese.
STOP_EN = {
    "access",
    "action",
    "application",
    "box",
    "channel",
    "cli",
    "code",
    "command",
    "content",
    "cursor",
    "data",
    "debug",
    "documentation",
    "error",
    "event",
    "file",
    "form",
    "image",
    "index",
    "item",
    "job",
    "key",
    "line",
    "list",
    "log",
    "loop",
    "map",
    "menu",
    "model",
    "name",
    "page",
    "path",
    "pattern",
    "probe",
    "quota",
    "schema",
    "session",
    "state",
    "table",
    "test",
    "text",
    "time",
    "type",
    "user",
    "value",
    "view",
    "web",
}

STOP_ZH = {
    "内容",
    "数据",
    "文档",
    "模式",
    "模型",
    "命令",
    "会话",
    "作业",
    "同步",
    "循环",
    "文件",
    "用户",
    "列表",
    "测试",
    "错误",
    "事件",
    "名称",
    "时间",
    "类型",
    "页面",
    "路径",
    "表格",
    "状态",
    "视图",
    "菜单",
    "日志",
    "镜像",
    "映像",
}


def extra_aliases() -> list[tuple[str, str]]:
    """alias text -> slug. Used when matching user messages."""
    return [
        ("api", "api"),
        ("应用程序编程接口", "api"),
        ("pr", "pull_request"),
        ("prs", "pull_request"),
        ("缓存", "cache"),
        ("提交", "commit"),
        ("线程", "thread"),
        ("进程", "process"),
        ("并发", "concurrency"),
        ("协议", "protocol"),
        ("中间件", "middleware"),
        ("异常", "exception"),
        ("函数", "function"),
        ("变量", "variable"),
        ("源代码", "source_code"),
        ("源码", "source_code"),
        ("递归", "recursion"),
        ("垃圾回收", "garbage_collection"),
        ("仓库", "repository"),
        ("存储库", "repository"),
        ("延迟", "latency"),
        ("算法", "algorithm"),
        ("接口", "interface"),
        ("编译器", "compiler"),
        ("数据库", "database"),
        ("分支", "branch"),
        ("合并", "merge"),
        ("抓取", "fetch"),
        ("拉取请求", "pull_request"),
        ("pull request", "pull_request"),
        ("变基", "rebase"),
        ("工作树", "worktree"),
        ("令牌", "token"),
        ("智能体", "agent"),
        ("技能", "skill"),
        ("提示词", "prompt"),
        ("编排器", "orchestrator"),
        ("上游", "upstream"),
        ("差异", "diff"),
        ("嵌入", "embedding"),
        ("沙箱", "sandbox"),
        ("检索增强生成", "rag"),
        ("模型上下文协议", "mcp"),
        ("钩子", "hook"),
    ]


def alias_usable(alias: str) -> bool:
    """Drop 1-2 letter English, stopwords, and single-character Chinese."""
    a = alias.strip()
    if not a:
        return False
    if re.search(r"[一-鿿]", a):
        return len(a) >= 2 and a not in STOP_ZH
    low = a.lower()
    if low in STOP_EN:
        return False
    return len(a) >= 3


def cmd_init(_: argparse.Namespace) -> None:
    con = connect()
    terms = load_term_files()
    con.executemany(
        "INSERT INTO terms(slug, en, zh, source, one_liner) VALUES (?,?,?,?,?) "
        "ON CONFLICT(slug) DO UPDATE SET en=excluded.en, zh=excluded.zh, "
        "source=excluded.source, one_liner=excluded.one_liner",
        [(t["slug"], t["en"], t["zh"], t["source"], t["one_liner"]) for t in terms],
    )
    for t in terms:
        con.execute(
            "INSERT OR IGNORE INTO term_freq(slug, seen_count, session_count, source) "
            "VALUES (?, 0, 0, 'unset')",
            (t["slug"],),
        )
        # alias: slug, en, zh
        for alias in {t["slug"], t["en"].lower(), t["zh"]}:
            if alias_usable(alias):
                con.execute(
                    "INSERT OR REPLACE INTO aliases(alias, slug) VALUES (?, ?)",
                    (alias.lower(), t["slug"]),
                )
    for alias, slug in extra_aliases():
        exists = con.execute("SELECT 1 FROM terms WHERE slug=?", (slug,)).fetchone()
        if exists and alias.strip():
            con.execute(
                "INSERT OR REPLACE INTO aliases(alias, slug) VALUES (?, ?)",
                (alias.lower(), slug),
            )
    con.commit()
    n_terms = con.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
    n_alias = con.execute("SELECT COUNT(*) FROM aliases").fetchone()[0]
    print(f"ok terms={n_terms} aliases={n_alias} db={db_path()}")


def band_of(n: int, threshold: int, slug: str = "", en: str = "") -> str:
    if slug in STOP_EN or en.strip().lower() in STOP_EN:
        return "bare"
    if n <= 0:
        return "first"
    if n < threshold:
        return "explain"
    return "bare"


def cmd_lookup(args: argparse.Namespace) -> None:
    con = connect()
    threshold = int(args.threshold)
    slugs = [s.strip() for s in (args.slugs or "").split(",") if s.strip()]
    if slugs:
        q = ",".join("?" * len(slugs))
        rows = con.execute(
            f"SELECT t.slug, t.en, t.zh, t.source, t.one_liner, "
            f"COALESCE(f.seen_count, 0) AS seen_count "
            f"FROM terms t LEFT JOIN term_freq f ON t.slug = f.slug "
            f"WHERE t.slug IN ({q}) ORDER BY t.slug",
            slugs,
        ).fetchall()
    else:
        rows = con.execute(
            "SELECT t.slug, t.en, t.zh, t.source, t.one_liner, "
            "COALESCE(f.seen_count, 0) AS seen_count "
            "FROM terms t LEFT JOIN term_freq f ON t.slug = f.slug "
            "ORDER BY seen_count ASC, t.slug"
        ).fetchall()
        if not args.all:
            kept = []
            for r in rows:
                n = int(r["seen_count"])
                b = band_of(n, threshold, r["slug"], r["en"])
                if b == "explain":
                    kept.append(r)
            rows = kept
    print(f"# db={db_path()}")
    print(f"# band: first (0) | explain (<{threshold}) | bare (>={threshold})")
    if not slugs and not args.all:
        print("# default: only explain. pass --slugs for this turn, --all for every term.")
    print("slug\tband\tseen\tzh\ten\tsource")
    for r in rows:
        n = int(r["seen_count"])
        print(
            f"{r['slug']}\t{band_of(n, threshold, r['slug'], r['en'])}\t{n}\t{r['zh']}\t{r['en']}\t{r['source']}"
        )


def cmd_bump(args: argparse.Namespace) -> None:
    slugs = [s.strip() for s in (args.slugs or "").split(",") if s.strip()]
    if not slugs:
        raise SystemExit("bump needs --slugs")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    con = connect()
    kept = []
    for slug in slugs:
        exists = con.execute("SELECT 1 FROM terms WHERE slug=?", (slug,)).fetchone()
        if not exists:
            print(f"skip unknown slug={slug}")
            continue
        con.execute(
            "INSERT INTO term_freq(slug, seen_count, session_count, first_seen, last_seen, source) "
            "VALUES (?, 1, 1, ?, ?, 'live') "
            "ON CONFLICT(slug) DO UPDATE SET "
            "seen_count = seen_count + 1, "
            "last_seen = excluded.last_seen, "
            "source = 'live'",
            (slug, now, now),
        )
        kept.append(slug)
    con.commit()
    print("bumped", ",".join(kept))


def user_messages(projects: Path):
    for p in glob.glob(str(projects / "*/*.jsonl")):
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if o.get("type") != "user":
                    continue
                msg = o.get("message") or {}
                if not isinstance(msg, dict) or msg.get("role") != "user":
                    continue
                c = msg.get("content")
                texts = []
                if isinstance(c, str):
                    texts = [c]
                elif isinstance(c, list):
                    texts = [
                        t.get("text") or ""
                        for t in c
                        if isinstance(t, dict) and t.get("type") == "text"
                    ]
                body = "\n".join(texts)
                s = body.strip()
                if not s or s.startswith(SKIP_USER) or "command-name" in s[:80]:
                    continue
                if "This session is being continued from a previous conversation" in s[:120]:
                    continue
                yield o.get("sessionId") or p, body


TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9_+/-]{2,}")


def load_alias_index(
    con: sqlite3.Connection,
) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """word/phrase -> slug, plus CJK/multiword needles."""
    word_map: dict[str, str] = {}
    needles: list[tuple[str, str]] = []
    for r in con.execute("SELECT alias, slug FROM aliases"):
        a = r["alias"].strip()
        if not alias_usable(a):
            continue
        slug = r["slug"]
        if re.search(r"[一-鿿]", a) or (" " in a) or ("/" in a):
            needles.append((a, slug))
        else:
            word_map[a.lower()] = slug
    needles.sort(key=lambda x: len(x[0]), reverse=True)
    return word_map, needles


def slugs_in_text(
    body: str, word_map: dict[str, str], needles: list[tuple[str, str]]
) -> set[str]:
    found: set[str] = set()
    lower = body.lower()
    for tok in TOKEN.findall(body):
        slug = word_map.get(tok.lower())
        if slug:
            found.add(slug)
    for needle, slug in needles:
        if needle in body or needle.lower() in lower:
            found.add(slug)
    return found


def cmd_seed_transcripts(args: argparse.Namespace) -> None:
    con = connect()
    n_terms = con.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
    if n_terms == 0:
        raise SystemExit("no terms; run init first")
    projects = Path(args.projects)
    word_map, needles = load_alias_index(con)
    from collections import Counter, defaultdict

    counts: Counter[str] = Counter()
    sessions: dict[str, set[str]] = defaultdict(set)
    n = 0
    for sid, body in user_messages(projects):
        n += 1
        for slug in slugs_in_text(body, word_map, needles):
            counts[slug] += 1
            sessions[slug].add(sid)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    updated = 0
    for slug, seen in counts.items():
        con.execute(
            "INSERT INTO term_freq(slug, seen_count, session_count, first_seen, last_seen, source) "
            "VALUES (?, ?, ?, ?, ?, 'transcript-seed') "
            "ON CONFLICT(slug) DO UPDATE SET "
            "seen_count = excluded.seen_count, "
            "session_count = excluded.session_count, "
            "source = 'transcript-seed', "
            "last_seen = excluded.last_seen",
            (slug, seen, len(sessions[slug]), now, now),
        )
        updated += 1
    con.commit()
    print(f"scanned {n} user messages; wrote freq for {updated} slugs; db={db_path()}")


def slugify(en: str) -> str:
    s = en.strip().lower()
    s = re.sub(r"[’'`]", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")[:80]


def insert_term_if_new(
    con: sqlite3.Connection, slug: str, en: str, zh: str, source: str
) -> bool:
    if not slug or not en or not zh:
        return False
    if con.execute("SELECT 1 FROM terms WHERE slug=?", (slug,)).fetchone():
        return False
    con.execute(
        "INSERT INTO terms(slug, en, zh, source, one_liner) VALUES (?,?,?,?,?)",
        (slug, en, zh, source, ""),
    )
    con.execute(
        "INSERT OR IGNORE INTO term_freq(slug, seen_count, session_count, source) "
        "VALUES (?, 0, 0, 'unset')",
        (slug,),
    )
    for alias in {slug, en.lower(), zh}:
        if alias_usable(alias):
            con.execute(
                "INSERT OR IGNORE INTO aliases(alias, slug) VALUES (?, ?)",
                (alias.lower(), slug),
            )
    return True


def cmd_import_juanito(_: argparse.Namespace) -> None:
    """Fetch Juanito glossary into local SQLite only. Do not copy into git."""
    import urllib.request

    url = "https://raw.githubusercontent.com/JuanitoFatas/Computer-Science-Glossary/master/dict.textile"
    text = urllib.request.urlopen(url, timeout=30).read().decode("utf-8", "replace")
    con = connect()
    n = 0
    for ln in text.splitlines():
        if not ln.startswith("|") or "*英文*" in ln or ln.startswith('|"'):
            continue
        cols = [c.strip() for c in ln.strip("|").split("|")]
        if len(cols) < 2:
            continue
        en, zh = cols[0], cols[1]
        if not en or not zh or en.startswith("*"):
            continue
        slug = slugify(en)
        if insert_term_if_new(con, slug, en, zh, "juanito"):
            n += 1
    con.commit()
    print(f"imported {n} new juanito terms into {db_path()} (not in git)")


def cmd_import_jiqizhixin(_: argparse.Namespace) -> None:
    """Fetch 机器之心 AI terms into local SQLite only. CC BY-NC-SA; not in git."""
    import urllib.request

    url = (
        "https://raw.githubusercontent.com/jiqizhixin/"
        "Artificial-Intelligence-Terminology-Database/master/data/All.md"
    )
    text = urllib.request.urlopen(url, timeout=60).read().decode("utf-8", "replace")
    con = connect()
    n = 0
    for ln in text.splitlines():
        if not ln.startswith("AITD-"):
            continue
        cols = [c.strip() for c in ln.split("|")]
        if len(cols) < 3:
            continue
        en, zh = cols[1], cols[2]
        zh = zh.split("/")[0].strip()
        if not en or not zh:
            continue
        slug = slugify(en)
        if insert_term_if_new(con, slug, en, zh, "jiqizhixin"):
            n += 1
    con.commit()
    print(f"imported {n} new jiqizhixin terms into {db_path()} (not in git)")


def cmd_stats(_: argparse.Namespace) -> None:
    con = connect()
    n_terms = con.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
    n_freq = con.execute(
        "SELECT COUNT(*) FROM term_freq WHERE seen_count > 0"
    ).fetchone()[0]
    print(f"db={db_path()}")
    print(f"terms={n_terms} with_hits={n_freq}")
    print("band\tcount")
    for band, q in (
        ("first", "seen_count = 0"),
        ("explain", "seen_count > 0 AND seen_count < 5"),
        ("bare", "seen_count >= 5"),
    ):
        c = con.execute(f"SELECT COUNT(*) FROM term_freq WHERE {q}").fetchone()[0]
        print(f"{band}\t{c}")
    print("top")
    for r in con.execute(
        "SELECT t.slug, t.zh, f.seen_count FROM term_freq f "
        "JOIN terms t ON t.slug = f.slug ORDER BY f.seen_count DESC LIMIT 15"
    ):
        print(f"  {r['seen_count']:5}  {r['zh']} ({r['slug']})")


def main() -> None:
    p = argparse.ArgumentParser(prog="glossary.py")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="load TSV glossaries into SQLite").set_defaults(
        func=cmd_init
    )

    lu = sub.add_parser("lookup", help="print zh/en and explain-band")
    lu.add_argument("--slugs", default="")
    lu.add_argument("--threshold", type=int, default=EXPLAIN_BELOW)
    lu.add_argument(
        "--all",
        action="store_true",
        help="dump every term, including already-familiar ones",
    )
    lu.set_defaults(func=cmd_lookup)

    bu = sub.add_parser("bump", help="increment seen_count for slugs used this turn")
    bu.add_argument("--slugs", required=True)
    bu.set_defaults(func=cmd_bump)

    se = sub.add_parser(
        "seed-transcripts", help="recount seen_count from local Claude jsonl"
    )
    se.add_argument(
        "--projects",
        default=str(Path.home() / ".claude" / "projects"),
    )
    se.set_defaults(func=cmd_seed_transcripts)

    sub.add_parser("stats").set_defaults(func=cmd_stats)
    sub.add_parser(
        "import-juanito",
        help="fetch Juanito CS glossary into local SQLite (not git)",
    ).set_defaults(func=cmd_import_juanito)
    sub.add_parser(
        "import-jiqizhixin",
        help="fetch 机器之心 AI terms into local SQLite (not git; NC license)",
    ).set_defaults(func=cmd_import_jiqizhixin)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        try:
            import sys

            sys.stdout.close()
        except Exception:
            pass
