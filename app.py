"""
utils/db_manager.py - v19.0
- تتبع تاريخ الأسعار (يحدث السعر إذا تغير)
- حفظ نقاط استئناف للمعالجة الخلفية
- قرارات لكل منتج (موافق/تأجيل/إزالة)
- سجل كامل بالتاريخ والوقت
- hidden_products: حفظ المنتجات المحذوفة/المرسلة بشكل دائم
"""
import sqlite3, json
from datetime import datetime

DB_PATH = "pricing_v18.db"


def _ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _date():
    return datetime.now().strftime("%Y-%m-%d")


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT, page TEXT,
        event_type TEXT, details TEXT,
        product_name TEXT, action_taken TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT, product_name TEXT,
        our_price REAL, comp_price REAL,
        diff REAL, competitor TEXT,
        old_status TEXT, new_status TEXT,
        reason TEXT, decided_by TEXT DEFAULT 'user'
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT, product_name TEXT,
        competitor TEXT, price REAL,
        our_price REAL, diff REAL,
        match_score REAL, decision TEXT,
        product_id TEXT DEFAULT ''
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS job_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT UNIQUE,
        started_at TEXT, updated_at TEXT,
        status TEXT DEFAULT 'running',
        total INTEGER DEFAULT 0,
        processed INTEGER DEFAULT 0,
        results_json TEXT DEFAULT '[]',
        missing_json TEXT DEFAULT '[]',
        our_file TEXT, comp_files TEXT
    )""")

    try:
        c.execute("ALTER TABLE job_progress ADD COLUMN missing_json TEXT DEFAULT '[]'")
    except:
        pass

    c.execute("""CREATE TABLE IF NOT EXISTS analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT, our_file TEXT,
        comp_file TEXT, total_products INTEGER,
        matched INTEGER, missing INTEGER, summary TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS ai_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT, prompt_hash TEXT UNIQUE,
        response TEXT, source TEXT
    )""")

    # ── جدول المنتجات المخفية (محذوفة أو مرسلة لـ Make) ──────────────
    c.execute("""CREATE TABLE IF NOT EXISTS hidden_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        hide_key TEXT UNIQUE,
        product_name TEXT,
        section TEXT,
        reason TEXT DEFAULT 'deleted'
    )""")

    conn.commit()
    conn.close()


# ─── أحداث ────────────────────────────────
def log_event(page, event_type, details="", product_name="", action=""):
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO events (timestamp,page,event_type,details,product_name,action_taken) VALUES (?,?,?,?,?,?)",
            (_ts(), page, event_type, details, product_name, action)
        )
        conn.commit(); conn.close()
    except: pass


# ─── قرارات ────────────────────────────────
def log_decision(product_name, old_status, new_status, reason="",
                 our_price=0, comp_price=0, diff=0, competitor=""):
    try:
        conn = get_db()
        conn.execute(
            """INSERT INTO decisions
               (timestamp,product_name,our_price,comp_price,diff,competitor,
                old_status,new_status,reason)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (_ts(), product_name, our_price, comp_price, diff,
             competitor, old_status, new_status, reason)
        )
        conn.commit(); conn.close()
    except: pass


def get_decisions(product_name=None, status=None, limit=100):
    try:
        conn = get_db()
        if product_name:
            rows = conn.execute(
                "SELECT * FROM decisions WHERE product_name LIKE ? ORDER BY id DESC LIMIT ?",
                (f"%{product_name}%", limit)
            ).fetchall()
        elif status:
            rows = conn.execute(
                "SELECT * FROM decisions WHERE new_status=? ORDER BY id DESC LIMIT ?",
                (status, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM decisions ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except: return []


# ─── تاريخ الأسعار ────────────────────────
def upsert_price_history(product_name, competitor, price,
                          our_price=0, diff=0, match_score=0,
                          decision="", product_id=""):
    conn = get_db()
    today = _date()

    last = conn.execute(
        """SELECT price, date FROM price_history
           WHERE product_name=? AND competitor=?
           ORDER BY id DESC LIMIT 1""",
        (product_name, competitor)
    ).fetchone()

    price_changed = False
    if last:
        last_price = last["price"]
        last_date  = last["date"]
        price_changed = abs(float(price) - float(last_price)) > 0.01

        if last_date == today:
            conn.execute(
                """UPDATE price_history SET price=?,our_price=?,diff=?,
                   match_score=?,decision=?,product_id=?
                   WHERE product_name=? AND competitor=? AND date=?""",
                (price, our_price, diff, match_score, decision,
                 product_id, product_name, competitor, today)
            )
        else:
            conn.execute(
                """INSERT INTO price_history
                   (date,product_name,competitor,price,our_price,diff,
                    match_score,decision,product_id)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (today, product_name, competitor, price, our_price,
                 diff, match_score, decision, product_id)
            )
    else:
        conn.execute(
            """INSERT INTO price_history
               (date,product_name,competitor,price,our_price,diff,
                match_score,decision,product_id)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (today, product_name, competitor, price, our_price,
             diff, match_score, decision, product_id)
        )

    conn.commit(); conn.close()
    return price_changed


def get_price_history(product_name, competitor="", limit=30):
    try:
        conn = get_db()
        if competitor:
            rows = conn.execute(
                """SELECT * FROM price_history
                   WHERE product_name=? AND competitor=?
                   ORDER BY date DESC LIMIT ?""",
                (product_name, competitor, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM price_history WHERE product_name=?
                   ORDER BY date DESC LIMIT ?""",
                (product_name, limit)
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except: return []


def get_price_changes(days=7):
    try:
        conn = get_db()
        rows = conn.execute(
            """SELECT p1.product_name, p1.competitor,
                      p1.price as new_price, p2.price as old_price,
                      p1.date as new_date, p2.date as old_date,
                      (p1.price - p2.price) as price_diff
               FROM price_history p1
               JOIN price_history p2
                 ON p1.product_name=p2.product_name
                AND p1.competitor=p2.competitor
                AND p1.id > p2.id
               WHERE p1.date >= date('now', ?)
                 AND abs(p1.price - p2.price) > 0.01
               ORDER BY abs(p1.price - p2.price) DESC
               LIMIT 100""",
            (f"-{days} days",)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except: return []


# ─── المنتجات المخفية (جديد) ─────────────
def save_hidden_product(hide_key: str, product_name: str, section: str, reason: str = "deleted"):
    """حفظ منتج مخفي (محذوف أو مرسل لـ Make) بشكل دائم في قاعدة البيانات"""
    try:
        conn = get_db()
        conn.execute(
            """INSERT OR IGNORE INTO hidden_products
               (timestamp, hide_key, product_name, section, reason)
               VALUES (?,?,?,?,?)""",
            (_ts(), hide_key, product_name, section, reason)
        )
        conn.commit(); conn.close()
    except: pass


def get_hidden_product_keys() -> set:
    """استرجاع كل مفاتيح المنتجات المخفية من قاعدة البيانات"""
    try:
        conn = get_db()
        rows = conn.execute("SELECT hide_key FROM hidden_products").fetchall()
        conn.close()
        return {r["hide_key"] for r in rows}
    except: return set()


# ─── المعالجة الخلفية ──────────────────────
def save_job_progress(job_id, total, processed, results, status="running",
                      our_file="", comp_files="", missing=None):
    conn = get_db()
    missing_data = json.dumps(missing if missing else [], ensure_ascii=False, default=str)
    conn.execute(
        """INSERT OR REPLACE INTO job_progress
           (job_id,started_at,updated_at,status,total,processed,
            results_json,missing_json,our_file,comp_files)
           VALUES (?,
               COALESCE((SELECT started_at FROM job_progress WHERE job_id=?), ?),
               ?, ?, ?, ?, ?, ?, ?, ?)""",
        (job_id, job_id, _ts(), _ts(), status, total, processed,
         json.dumps(results, ensure_ascii=False, default=str),
         missing_data,
         our_file, comp_files)
    )
    conn.commit(); conn.close()


def get_job_progress(job_id):
    try:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM job_progress WHERE job_id=?", (job_id,)
        ).fetchone()
        conn.close()
        if row:
            d = dict(row)
            try: d["results"] = json.loads(d.get("results_json", "[]"))
            except: d["results"] = []
            try: d["missing"] = json.loads(d.get("missing_json", "[]"))
            except: d["missing"] = []
            return d
    except: pass
    return None


def get_last_job():
    try:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM job_progress ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if row:
            d = dict(row)
            try: d["results"] = json.loads(d.get("results_json", "[]"))
            except: d["results"] = []
            try: d["missing"] = json.loads(d.get("missing_json", "[]"))
            except: d["missing"] = []
            return d
    except: pass
    return None


# ─── سجل التحليلات ─────────────────────────
def log_analysis(our_file, comp_file, total, matched, missing, summary=""):
    try:
        conn = get_db()
        conn.execute(
            """INSERT INTO analysis_history
               (timestamp,our_file,comp_file,total_products,matched,missing,summary)
               VALUES (?,?,?,?,?,?,?)""",
            (_ts(), our_file, comp_file, total, matched, missing, summary)
        )
        conn.commit(); conn.close()
    except: pass


def get_analysis_history(limit=20):
    try:
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM analysis_history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except: return []


def get_events(page=None, limit=50):
    try:
        conn = get_db()
        if page:
            rows = conn.execute(
                "SELECT * FROM events WHERE page=? ORDER BY id DESC LIMIT ?",
                (page, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except: return []


init_db()
