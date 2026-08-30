#!/usr/bin/env python3
"""Export a project-scoped claude-mem slice for Grok web.

Grok in the browser cannot see ~/.claude-mem. This writes a filtered dump that
can be uploaded to Grok project artifacts, committed, or copied to Google Drive.

Never dumps user_prompts. Never binds the worker off localhost.
Episodic memory is not STATUS.md or authority.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = Path.home() / ".claude-mem" / "claude-mem.db"
DEFAULT_PROJECTS = ["K1-CORE-VAL-R0"]
DEFAULT_QUERIES = ["USB2422", "D-044", "D-049", "D-050", "D-051", "NFC I2C"]

OBS_FIELDS = (
    "id",
    "project",
    "created_at",
    "type",
    "title",
    "subtitle",
    "narrative",
    "facts",
    "concepts",
    "files_read",
    "files_modified",
)

SUM_FIELDS = (
    "id",
    "project",
    "created_at",
    "request",
    "investigated",
    "learned",
    "completed",
    "next_steps",
    "notes",
    "files_read",
    "files_edited",
)

SECRET = re.compile(
    r"(sk-ant-[A-Za-z0-9_-]+|"
    r"ghp_[A-Za-z0-9]+|"
    r"github_pat_[A-Za-z0-9_]+|"
    r"xox[baprs]-[A-Za-z0-9-]+|"
    r"Bearer\s+[A-Za-z0-9._\-]{20,})",
    re.I,
)


def fts_match(term: str) -> str:
    cleaned = term.strip().replace('"', "")
    if not cleaned:
        raise ValueError("empty query")
    if re.search(r"[^A-Za-z0-9]", cleaned):
        return f'"{cleaned}"'
    return cleaned


def redact(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, str):
        return SECRET.sub("[REDACTED]", value)
    return value


def row_dict(cursor: sqlite3.Cursor, row: sqlite3.Row, fields: tuple[str, ...]) -> dict:
    return {field: redact(row[field]) for field in fields}


def connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise SystemExit(f"claude-mem database missing: {db_path}")
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def fetch_project_observations(con: sqlite3.Connection, projects: list[str]) -> list[dict]:
    placeholders = ",".join("?" * len(projects))
    sql = (
        f"SELECT {', '.join(OBS_FIELDS)} FROM observations "
        f"WHERE project IN ({placeholders}) ORDER BY id ASC"
    )
    return [row_dict(con, row, OBS_FIELDS) for row in con.execute(sql, projects)]


def fetch_project_summaries(con: sqlite3.Connection, projects: list[str]) -> list[dict]:
    placeholders = ",".join("?" * len(projects))
    sql = (
        f"SELECT {', '.join(SUM_FIELDS)} FROM session_summaries "
        f"WHERE project IN ({placeholders}) ORDER BY id ASC"
    )
    return [row_dict(con, row, SUM_FIELDS) for row in con.execute(sql, projects)]


def fetch_query_observations(con: sqlite3.Connection, queries: list[str]) -> tuple[list[dict], dict[str, int]]:
    by_id: dict[int, dict] = {}
    hits: dict[str, int] = {}
    sql = (
        f"SELECT {', '.join('o.' + field for field in OBS_FIELDS)} "
        "FROM observations o JOIN observations_fts f ON f.rowid = o.id "
        "WHERE observations_fts MATCH ? ORDER BY o.id ASC"
    )
    for query in queries:
        match = fts_match(query)
        rows = [row_dict(con, row, OBS_FIELDS) for row in con.execute(sql, (match,))]
        hits[query] = len(rows)
        for row in rows:
            by_id[int(row["id"])] = row
    return [by_id[key] for key in sorted(by_id)], hits


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def md_block(label: str, value: object) -> str:
    if value is None or value == "":
        return ""
    text = str(value).strip()
    if not text:
        return ""
    return f"**{label}.** {text}\n\n"


def observations_markdown(title: str, rows: list[dict], disclaimer: str) -> str:
    lines = [
        f"# {title}",
        "",
        disclaimer,
        "",
        f"Count: {len(rows)}",
        "",
        "| ID | When | Project | Type | Title |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        title_cell = (row.get("title") or "").replace("|", "\\|")
        lines.append(
            f"| {row['id']} | {row['created_at']} | {row['project']} | "
            f"{row['type']} | {title_cell} |"
        )
    lines.extend(["", "---", ""])
    for row in rows:
        lines.append(f"## Observation {row['id']}: {row.get('title') or '(untitled)'}")
        lines.append("")
        lines.append(f"- Project: `{row['project']}`")
        lines.append(f"- Type: `{row['type']}`")
        lines.append(f"- When: {row['created_at']}")
        lines.append("")
        lines.append(md_block("Subtitle", row.get("subtitle")))
        lines.append(md_block("Narrative", row.get("narrative")))
        lines.append(md_block("Facts", row.get("facts")))
        lines.append(md_block("Concepts", row.get("concepts")))
        lines.append(md_block("Files read", row.get("files_read")))
        lines.append(md_block("Files modified", row.get("files_modified")))
    return "\n".join(line for line in lines if line is not None)


def summaries_markdown(rows: list[dict]) -> str:
    lines = [
        "# Session summaries",
        "",
        "Project-scoped session summaries only. User prompts are omitted.",
        "",
        f"Count: {len(rows)}",
        "",
    ]
    for row in rows:
        lines.append(f"## Summary {row['id']} ({row['project']}, {row['created_at']})")
        lines.append("")
        for label, key in (
            ("Request", "request"),
            ("Investigated", "investigated"),
            ("Learned", "learned"),
            ("Completed", "completed"),
            ("Next steps", "next_steps"),
            ("Notes", "notes"),
        ):
            lines.append(md_block(label, row.get(key)))
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--project", action="append", dest="projects")
    parser.add_argument("--query", action="append", dest="queries")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("_scratch/claude-mem-grok-export"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    projects = args.projects or DEFAULT_PROJECTS
    queries = args.queries or DEFAULT_QUERIES
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    con = connect(args.db)
    try:
        project_obs = fetch_project_observations(con, projects)
        summaries = fetch_project_summaries(con, projects)
        query_obs, query_hits = fetch_query_observations(con, queries)
    finally:
        con.close()

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    disclaimer = (
        "Episodic claude-mem export for Grok web. This is not STATUS.md, not "
        "authority, and not a live worker. User prompts are omitted. Secrets "
        "matching known token prefixes are redacted."
    )
    manifest = {
        "generated_at_utc": generated,
        "source_db": str(args.db),
        "projects": projects,
        "queries": queries,
        "query_hits": query_hits,
        "counts": {
            "project_observations": len(project_obs),
            "query_observations_deduped": len(query_obs),
            "session_summaries": len(summaries),
            "user_prompts_exported": 0,
        },
        "authority": "episodic-memory-not-status",
        "forbidden": [
            "do not bind CLAUDE_MEM_WORKER_HOST to 0.0.0.0",
            "do not tunnel :37777",
            "do not export user_prompts",
        ],
    }

    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (out / "PROJECT-OBSERVATIONS.md").write_text(
        observations_markdown("K1-CORE-VAL-R0 claude-mem observations", project_obs, disclaimer),
        encoding="utf-8",
    )
    (out / "QUERY-HITS.md").write_text(
        observations_markdown(
            "claude-mem query hits for Grok (USB / NFC / D-series)",
            query_obs,
            disclaimer + f" Queries: {', '.join(queries)}.",
        ),
        encoding="utf-8",
    )
    (out / "SESSION-SUMMARIES.md").write_text(summaries_markdown(summaries), encoding="utf-8")
    write_jsonl(out / "PROJECT-OBSERVATIONS.jsonl", project_obs)
    write_jsonl(out / "QUERY-HITS.jsonl", query_obs)
    write_jsonl(out / "SESSION-SUMMARIES.jsonl", summaries)

    print(json.dumps(manifest, indent=2))
    print(f"wrote {out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
