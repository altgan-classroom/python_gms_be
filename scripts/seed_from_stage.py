"""Seed our gms DB (schema already loaded from gms-stage-2 structure) with a
sample slice of gms-stage-2 data.

- Full reference data (_ref_*).
- One sample gym + its location(s), staff/owner + capped members, their
  profiles, plans, and memberships.
- Every seeded user's password -> Test@1234, verified + active.
  Login: owner@demo.gym / Test@1234
- scripts/anonymize_seed.sql then replaces all personal and customer data with fictional values.

Run in a service container:
  docker compose run --rm --no-deps -v $PWD/scripts:/app/scripts \
    auth-admin-service python scripts/seed_from_stage.py
"""
from pathlib import Path

import mysql.connector
from flask_bcrypt import Bcrypt

SRC_DB = "gms-stage-2"
GYM_ID = 43
MEMBER_LIMIT = 40
MSHIP_LIMIT = 60
PW_HASH = Bcrypt().generate_password_hash("Test@1234", 12).decode("utf-8")

src = mysql.connector.connect(host="host.docker.internal", port=3306, user="root", password="admin", database=SRC_DB)
tgt = mysql.connector.connect(host="db", port=3306, user="gms", password="gms", database="gms")


def cols(conn, schema, table):
    c = conn.cursor()
    c.execute(
        "SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema=%s AND table_name=%s ORDER BY ordinal_position",
        (schema, table),
    )
    return [r[0] for r in c.fetchall()]


def copy(table, where="", limit=None, transform=None):
    scols = cols(src, SRC_DB, table)
    tcols = set(cols(tgt, "gms", table))
    if not scols or not tcols:
        print(f"  skip {table} (missing in src/tgt)")
        return 0
    use = [c for c in scols if c in tcols]
    sel = ", ".join(f"`{c}`" for c in use)
    q = f"SELECT {sel} FROM `{SRC_DB}`.`{table}` {where}" + (f" LIMIT {limit}" if limit else "")
    sc = src.cursor()
    sc.execute(q)
    rows = sc.fetchall()
    if not rows:
        return 0
    tc = tgt.cursor()
    ins = f"INSERT INTO `{table}` ({sel}) VALUES ({', '.join(['%s'] * len(use))})"
    n = 0
    for row in rows:
        d = dict(zip(use, row))
        if transform and transform(d) is False:
            continue
        try:
            tc.execute(ins, tuple(d[c] for c in use))
            n += 1
        except Exception as e:
            print(f"    rowskip {table}: {str(e)[:80]}")
    tgt.commit()
    return n


tc = tgt.cursor()
tc.execute("SET FOREIGN_KEY_CHECKS=0")
tgt.commit()

# 1) reference data — every _ref_* table that exists in our schema
tc.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='gms' AND table_name LIKE '\\_ref%'")
refs = [r[0] for r in tc.fetchall()]
nref = sum(copy(t) for t in refs)
print(f"reference rows: {nref} across {len(refs)} tables")

# 2) gym + location(s)
copy("gym", where=f"WHERE id={GYM_ID}")
nloc = copy("location", where=f"WHERE gym_id={GYM_ID}")
sc = src.cursor()
sc.execute(f"SELECT id FROM `{SRC_DB}`.location WHERE gym_id={GYM_ID}")
loc_list = ",".join(str(r[0]) for r in sc.fetchall()) or "0"
print(f"gym {GYM_ID}: {nloc} location(s) [{loc_list}]")

# 3) users on those locations: all staff/owner (role<=5) + capped members
sc.execute(
    f"SELECT DISTINCT u.id,u.role_type_id FROM `{SRC_DB}`.user u "
    f"JOIN `{SRC_DB}`.user_location ul ON u.id=ul.user_id WHERE ul.location_id IN ({loc_list})"
)
allu = sc.fetchall()
staff = [u for u, r in allu if r and r <= 5]
members = [u for u, r in allu if r == 6][:MEMBER_LIMIT]
uids = staff + members
uid_list = ",".join(map(str, uids)) or "0"
print(f"users: {len(staff)} staff/owner + {len(members)} members")


def u_tf(d):
    d["password_hash"] = PW_HASH
    d["verified"] = 1
    d["active"] = 1
    d["email"] = "owner@demo.gym" if d.get("role_type_id") == 1 else f"u{d['id']}@demo.gym"


def ph_tf(d):
    if "phone_number" in d:
        d["phone_number"] = "+10000000000"


copy("user", where=f"WHERE id IN ({uid_list})", transform=u_tf)
copy("user_profile", where=f"WHERE user_id IN ({uid_list})", transform=ph_tf)
copy("member_profile", where=f"WHERE user_id IN ({uid_list})")
copy("user_location", where=f"WHERE user_id IN ({uid_list}) AND location_id IN ({loc_list})")
np = copy("plan", where=f"WHERE location_id IN ({loc_list})")
nm = copy("membership", where=f"WHERE user_id IN ({uid_list}) AND location_id IN ({loc_list})", limit=MSHIP_LIMIT)
print(f"plans: {np}, memberships: {nm}")

for statement in (Path(__file__).parent / "anonymize_seed.sql").read_text().split(";\n"):
    if statement.strip() and not all(line.startswith("--") for line in statement.strip().splitlines()):
        tc.execute(statement)
tgt.commit()
print("personal data anonymized")

tc.execute("SET FOREIGN_KEY_CHECKS=1")
tgt.commit()
print("SEED DONE — login: owner@demo.gym / Test@1234")
