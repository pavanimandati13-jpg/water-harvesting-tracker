"""Water Harvesting Tracker - rainwater harvesting sites, rainfall, usage and tank levels.

Harvested litres = roof area (m2) x rainfall (mm) x runoff coefficient.
The tank is simulated chronologically: rain fills it (excess overflows),
usage drains it (anything beyond what is stored is counted as a shortfall).
"""
import os
import random
import sqlite3
from datetime import date, datetime, timedelta

from flask import Flask, g, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "harvest.db"))
PURPOSES = ["Gardening", "Cleaning", "Toilets", "Laundry", "Drinking (treated)", "Other"]

app = Flask(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT DEFAULT '',
    roof_area REAL NOT NULL,
    runoff_coeff REAL NOT NULL DEFAULT 0.8,
    tank_capacity REAL NOT NULL,
    initial_level REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS rainfall (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    mm REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    litres REAL NOT NULL,
    purpose TEXT DEFAULT 'Other'
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    if db.execute("SELECT COUNT(*) FROM sites").fetchone()[0] == 0:
        rnd = random.Random(7)
        db.execute("INSERT INTO sites(name,location,roof_area,runoff_coeff,tank_capacity) VALUES (?,?,?,?,?)",
                   ("Hostel Block Roof", "Main Campus", 250, 0.8, 20000))
        db.execute("INSERT INTO sites(name,location,roof_area,runoff_coeff,tank_capacity) VALUES (?,?,?,?,?)",
                   ("Library Terrace", "Main Campus", 120, 0.85, 10000))
        today = date.today()
        for sid in (1, 2):
            for _ in range(22):
                d = today - timedelta(days=rnd.randint(1, 120))
                db.execute("INSERT INTO rainfall(site_id,date,mm) VALUES (?,?,?)",
                           (sid, d.isoformat(), round(rnd.uniform(4, 55), 1)))
            for k in range(0, 120, 3):
                d = today - timedelta(days=k)
                db.execute("INSERT INTO usage(site_id,date,litres,purpose) VALUES (?,?,?,?)",
                           (sid, d.isoformat(), rnd.randint(300, 1500) // (1 if sid == 1 else 2), rnd.choice(PURPOSES[:4])))
    db.commit()
    db.close()


def err(msg, code=400):
    return jsonify(error=msg), code


def valid_date(s):
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False


def positive(v):
    try:
        return float(v) > 0
    except (TypeError, ValueError):
        return False


def harvest_litres(area, mm, coeff):
    return area * mm * coeff


def simulate(db, site):
    """Replay rain and usage in date order; return totals, level and monthly stats."""
    cap = site["tank_capacity"]
    events = []
    for r in db.execute("SELECT date, mm FROM rainfall WHERE site_id=?", (site["id"],)):
        events.append((r["date"], 0, harvest_litres(site["roof_area"], r["mm"], site["runoff_coeff"]), r["mm"]))
    for u in db.execute("SELECT date, litres FROM usage WHERE site_id=?", (site["id"],)):
        events.append((u["date"], 1, u["litres"], 0))
    events.sort(key=lambda e: (e[0], e[1]))

    level = min(site["initial_level"], cap)
    t = dict(rain_mm=0.0, potential=0.0, stored=0.0, overflow=0.0, used=0.0, shortfall=0.0)
    months = {}
    for d, kind, litres, mm in events:
        m = months.setdefault(d[:7], dict(month=d[:7], rain_mm=0.0, harvested=0.0, used=0.0))
        if kind == 0:
            stored = min(litres, cap - level)
            level += stored
            t["rain_mm"] += mm
            t["potential"] += litres
            t["stored"] += stored
            t["overflow"] += litres - stored
            m["rain_mm"] += mm
            m["harvested"] += stored
        else:
            take = min(level, litres)
            level -= take
            t["used"] += take
            t["shortfall"] += litres - take
            m["used"] += take
    return level, t, [dict(v) for _, v in sorted(months.items())]


# ---------- pages ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(status="ok")


# ---------- sites ----------
@app.route("/api/sites", methods=["GET", "POST"])
def sites():
    db = get_db()
    if request.method == "GET":
        return jsonify([dict(r) for r in db.execute("SELECT * FROM sites ORDER BY name")])
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    coeff = d.get("runoff_coeff", 0.8)
    if not name or not positive(d.get("roof_area")) or not positive(d.get("tank_capacity")):
        return err("name, roof_area and tank_capacity are required (positive numbers)")
    if not positive(coeff) or float(coeff) > 1:
        return err("runoff_coeff must be between 0 and 1")
    cur = db.execute("INSERT INTO sites(name,location,roof_area,runoff_coeff,tank_capacity,initial_level) VALUES (?,?,?,?,?,?)",
                     (name, d.get("location", ""), float(d["roof_area"]), float(coeff), float(d["tank_capacity"]),
                      max(float(d.get("initial_level") or 0), 0)))
    db.commit()
    return jsonify(id=cur.lastrowid), 201


@app.route("/api/sites/<int:sid>", methods=["DELETE"])
def delete_site(sid):
    db = get_db()
    cur = db.execute("DELETE FROM sites WHERE id=?", (sid,))
    db.commit()
    return (jsonify(message="Deleted"), 200) if cur.rowcount else err("Site not found", 404)


def get_site(db, sid):
    return db.execute("SELECT * FROM sites WHERE id=?", (sid,)).fetchone()


# ---------- rainfall & usage ----------
@app.route("/api/sites/<int:sid>/rainfall", methods=["GET", "POST"])
def rainfall(sid):
    db = get_db()
    site = get_site(db, sid)
    if not site:
        return err("Site not found", 404)
    if request.method == "GET":
        rows = db.execute("SELECT * FROM rainfall WHERE site_id=? ORDER BY date DESC, id DESC LIMIT 50", (sid,))
        return jsonify([{**dict(r), "litres": round(harvest_litres(site["roof_area"], r["mm"], site["runoff_coeff"]))} for r in rows])
    d = request.get_json(silent=True) or {}
    if not valid_date(d.get("date")) or not positive(d.get("mm")):
        return err("date (YYYY-MM-DD) and mm (> 0) are required")
    cur = db.execute("INSERT INTO rainfall(site_id,date,mm) VALUES (?,?,?)", (sid, d["date"], float(d["mm"])))
    db.commit()
    return jsonify(id=cur.lastrowid), 201


@app.route("/api/sites/<int:sid>/usage", methods=["GET", "POST"])
def usage(sid):
    db = get_db()
    if not get_site(db, sid):
        return err("Site not found", 404)
    if request.method == "GET":
        rows = db.execute("SELECT * FROM usage WHERE site_id=? ORDER BY date DESC, id DESC LIMIT 50", (sid,))
        return jsonify([dict(r) for r in rows])
    d = request.get_json(silent=True) or {}
    if not valid_date(d.get("date")) or not positive(d.get("litres")):
        return err("date (YYYY-MM-DD) and litres (> 0) are required")
    cur = db.execute("INSERT INTO usage(site_id,date,litres,purpose) VALUES (?,?,?,?)",
                     (sid, d["date"], float(d["litres"]), d.get("purpose") or "Other"))
    db.commit()
    return jsonify(id=cur.lastrowid), 201


@app.route("/api/rainfall/<int:rid>", methods=["DELETE"])
def delete_rain(rid):
    db = get_db()
    cur = db.execute("DELETE FROM rainfall WHERE id=?", (rid,))
    db.commit()
    return (jsonify(message="Deleted"), 200) if cur.rowcount else err("Not found", 404)


@app.route("/api/usage/<int:uid>", methods=["DELETE"])
def delete_usage(uid):
    db = get_db()
    cur = db.execute("DELETE FROM usage WHERE id=?", (uid,))
    db.commit()
    return (jsonify(message="Deleted"), 200) if cur.rowcount else err("Not found", 404)


# ---------- summary & estimator ----------
@app.route("/api/sites/<int:sid>/summary")
def summary(sid):
    db = get_db()
    site = get_site(db, sid)
    if not site:
        return err("Site not found", 404)
    level, t, months = simulate(db, site)
    since = (date.today() - timedelta(days=30)).isoformat()
    last30 = db.execute("SELECT COALESCE(SUM(litres),0) FROM usage WHERE site_id=? AND date>=?", (sid, since)).fetchone()[0]
    avg_daily = last30 / 30
    return jsonify(
        site=dict(site),
        current_level=round(level),
        percent_full=round(100 * level / site["tank_capacity"], 1),
        total_rain_mm=round(t["rain_mm"], 1),
        potential_harvest=round(t["potential"]),
        stored=round(t["stored"]),
        overflow_wasted=round(t["overflow"]),
        total_used=round(t["used"]),
        shortfall=round(t["shortfall"]),
        avg_daily_use_30d=round(avg_daily),
        days_remaining=round(level / avg_daily, 1) if avg_daily > 0 else None,
        monthly=[{**m, "rain_mm": round(m["rain_mm"], 1), "harvested": round(m["harvested"]), "used": round(m["used"])} for m in months],
    )


@app.route("/api/estimate")
def estimate():
    """Quick what-if: potential yearly harvest for a roof."""
    try:
        area, rain = float(request.args["area"]), float(request.args["rainfall"])
        coeff = float(request.args.get("coeff", 0.8))
    except (KeyError, ValueError):
        return err("area (m2), rainfall (mm/year) and optional coeff are required numbers")
    if area <= 0 or rain <= 0 or not 0 < coeff <= 1:
        return err("area and rainfall must be positive and coeff between 0 and 1")
    litres = harvest_litres(area, rain, coeff)
    return jsonify(litres_per_year=round(litres), kilolitres_per_year=round(litres / 1000, 1),
                   avg_litres_per_day=round(litres / 365), suggested_tank_litres=round(litres / 12))


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
