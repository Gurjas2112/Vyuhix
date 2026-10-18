"""SQLite store: users, tamper-evident audit log, guardrail events, jobs, alerts, copilot calls, feed state."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import sqlite3
import threading

from .settings import RUNTIME_DIR

DB_PATH = RUNTIME_DIR / "vyuhix.db"
_lock = threading.Lock()


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


SCHEMA = """
create table if not exists users (
  id integer primary key, email text unique not null, name text not null,
  role text not null check (role in ('org_admin','analyst','viewer','broker','platform_admin')),
  org_id text, pw_salt text not null, pw_hash text not null, created_at text not null);
create table if not exists audit_log (
  id integer primary key, at text not null, actor text, action text not null, target text,
  detail text, prev_hash text not null, row_hash text not null);
create trigger if not exists audit_no_update before update on audit_log
  begin select raise(abort, 'audit_log is append-only'); end;
create trigger if not exists audit_no_delete before delete on audit_log
  begin select raise(abort, 'audit_log is append-only'); end;
create table if not exists guardrail_events (
  id integer primary key, at text not null, type text not null, source text, detail text, status text default 'open');
create table if not exists jobs (
  id integer primary key, at text not null, kind text not null, status text not null, actor text, detail text);
create table if not exists alerts (
  id integer primary key, at text not null, severity text not null, message text not null, detail text);
create table if not exists copilot_calls (
  id integer primary key, at text not null, actor text, mode text, latency_ms integer, grounded integer, question text);
create table if not exists state (k text primary key, v text not null);
"""


def init() -> None:
    with _lock, _conn() as c:
        c.executescript(SCHEMA)


def get_state(k: str, default: str) -> str:
    with _conn() as c:
        r = c.execute("select v from state where k=?", (k,)).fetchone()
    return r["v"] if r else default


def set_state(k: str, v: str) -> None:
    with _lock, _conn() as c:
        c.execute("insert into state(k,v) values(?,?) on conflict(k) do update set v=excluded.v", (k, v))


def _row_hash(prev: str, at: str, actor, action, target, detail) -> str:
    return hashlib.sha256("|".join([prev, at, str(actor), action, str(target), detail]).encode()).hexdigest()


def audit(actor: str | None, action: str, target: str | None = None, detail: dict | None = None) -> None:
    d = json.dumps(detail or {}, sort_keys=True)
    with _lock, _conn() as c:
        r = c.execute("select row_hash from audit_log order by id desc limit 1").fetchone()
        prev = r["row_hash"] if r else "0" * 64
        at = now()
        h = _row_hash(prev, at, actor, action, target, d)
        c.execute("insert into audit_log(at,actor,action,target,detail,prev_hash,row_hash) values(?,?,?,?,?,?,?)",
                  (at, actor, action, target, d, prev, h))


def verify_audit() -> dict:
    with _conn() as c:
        rows = c.execute("select * from audit_log order by id").fetchall()
    prev = "0" * 64
    for r in rows:
        expect = _row_hash(prev, r["at"], r["actor"], r["action"], r["target"], r["detail"])
        if r["prev_hash"] != prev or r["row_hash"] != expect:
            return {"ok": False, "rows": len(rows), "first_broken_id": r["id"]}
        prev = r["row_hash"]
    return {"ok": True, "rows": len(rows), "head": prev}


def insert(table: str, **fields) -> int:
    assert table in {"guardrail_events", "jobs", "alerts", "copilot_calls"}
    fields.setdefault("at", now())
    for k, v in list(fields.items()):
        if isinstance(v, (dict, list)):
            fields[k] = json.dumps(v)
    cols = ",".join(fields)
    with _lock, _conn() as c:
        cur = c.execute(f"insert into {table}({cols}) values({','.join('?' * len(fields))})", tuple(fields.values()))
        return int(cur.lastrowid)


def update_job(job_id: int, status: str, detail: dict) -> None:
    with _lock, _conn() as c:
        c.execute("update jobs set status=?, detail=? where id=?", (status, json.dumps(detail), job_id))


def rows(sql: str, args: tuple = ()) -> list[dict]:
    with _conn() as c:
        out = [dict(r) for r in c.execute(sql, args).fetchall()]
    for r in out:
        for k in ("detail",):
            if isinstance(r.get(k), str) and r[k][:1] in "{[":
                r[k] = json.loads(r[k])
    return out


def scalar(sql: str, args: tuple = ()):
    with _conn() as c:
        r = c.execute(sql, args).fetchone()
    return r[0] if r else None


def raw():
    return _conn()


init()
