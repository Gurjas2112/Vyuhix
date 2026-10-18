"""Level-1 authentication: scrypt password hashes, short-lived HS256 JWTs, role checks, login throttling.

Level 2 replaces this module with Supabase Auth (email confirmation, TOTP MFA, ES256/JWKS);
the role names and route guards stay the same.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import re
import secrets
import time
from collections import defaultdict

import jwt
from fastapi import Depends, HTTPException, Request

from . import store
from .settings import DEMO_PASSWORD, JWT_SECRET, JWT_TTL_HOURS

ROLES = ("org_admin", "analyst", "viewer", "broker", "platform_admin")
DEMO_USERS = [
    ("ananya@acme.demo", "Ananya Rao (CISO)", "org_admin", "acme-fintech"),
    ("rohit@acme.demo", "Rohit Mehta (CFO)", "viewer", "acme-fintech"),
    ("karan@broker.demo", "Karan Shah (Broker)", "broker", "acme-fintech"),
    ("divya@platform.demo", "Divya Iyer (Platform ops)", "platform_admin", None),
]
PASSWORD_RULE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{10,128}$")
_failures: dict[str, list[float]] = defaultdict(list)


def hash_pw(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    h = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1).hex()
    return salt, h


def seed_users() -> None:
    for email, name, role, org in DEMO_USERS:
        if store.scalar("select count(*) from users where email=?", (email,)):
            continue
        salt, h = hash_pw(DEMO_PASSWORD)
        with store.raw() as c:
            c.execute("insert into users(email,name,role,org_id,pw_salt,pw_hash,created_at) values(?,?,?,?,?,?,?)",
                      (email, name, role, org, salt, h, store.now()))


def _throttled(key: str) -> bool:
    window = [t for t in _failures[key] if time.time() - t < 300]
    _failures[key] = window
    return len(window) >= 5


def login(email: str, password: str, ip: str) -> dict:
    key = f"{ip}:{email.lower()}"
    if _throttled(key):
        store.audit(email, "login_throttled", detail={"ip": ip})
        raise HTTPException(429, "Too many failed attempts. Try again in a few minutes.")
    users = store.rows("select * from users where email=?", (email.lower(),))
    ok = False
    if users:
        u = users[0]
        _, h = hash_pw(password, u["pw_salt"])
        ok = hmac.compare_digest(h, u["pw_hash"])
    if not ok:
        _failures[key].append(time.time())
        store.audit(email, "login_failed", detail={"ip": ip})
        raise HTTPException(401, "Email or password is incorrect.")
    store.audit(u["email"], "login", detail={"ip": ip})
    return issue(u)


def signup(email: str, name: str, password: str) -> dict:
    email = email.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(422, "Enter a valid email address.")
    if not PASSWORD_RULE.match(password):
        raise HTTPException(422, "Password needs 10+ characters with upper, lower, digit and symbol.")
    if store.scalar("select count(*) from users where email=?", (email,)):
        raise HTTPException(409, "An account with this email already exists.")
    salt, h = hash_pw(password)
    with store.raw() as c:
        c.execute("insert into users(email,name,role,org_id,pw_salt,pw_hash,created_at) values(?,?,?,?,?,?,?)",
                  (email, name.strip()[:80] or email, "analyst", "acme-fintech", salt, h, store.now()))
    store.audit(email, "signup", detail={"role": "analyst", "org": "acme-fintech"})
    return issue(store.rows("select * from users where email=?", (email,))[0])


def issue(u: dict) -> dict:
    exp = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=JWT_TTL_HOURS)
    claims = {"sub": u["email"], "name": u["name"], "role": u["role"], "org": u["org_id"], "exp": exp}
    return {"token": jwt.encode(claims, JWT_SECRET, algorithm="HS256"),
            "user": {"email": u["email"], "name": u["name"], "role": u["role"], "org": u["org_id"]}}


def current(request: Request) -> dict:
    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(401, "Sign in required.")
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Session expired. Sign in again.")


def require(*roles: str):
    def dep(user: dict = Depends(current)) -> dict:
        if roles and user["role"] not in roles:
            raise HTTPException(403, f"This view needs one of: {', '.join(roles)}.")
        return user
    return dep


ORG_READ = ("org_admin", "analyst", "viewer")
ORG_ALL = ("org_admin", "analyst", "viewer", "broker")
ORG_WRITE = ("org_admin", "analyst")
