"""
مهووس v22 — مدير قاعدة البيانات الذكية
"""

import sqlite3, json, os
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path="data/mahwous.db"):
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else "data", exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._create_tables()

    # ─────────────────────────────────────────────
    # إنشاء الجداول
    # ─────────────────────────────────────────────
    def _create_tables(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS master_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint TEXT UNIQUE NOT NULL,
            brand TEXT,
            product_name TEXT NOT NULL,
            product_name_ar TEXT,
            concentration TEXT,
            size_ml REAL,
            gender TEXT,
            category TEXT DEFAULT 'perfume',
            image_url TEXT,
            fragrantica_url TEXT,
            notes_top TEXT,
            notes_heart TEXT,
            notes_base TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS product_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            master_id INTEGER NOT NULL,
            alias_name TEXT NOT NULL,
            source TEXT DEFAULT 'auto',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (master_id) REFERENCES master_products(id),
            UNIQUE(master_id, alias_name)
        );

        CREATE TABLE IF NOT EXISTS my_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_no TEXT,
            master_id INTEGER,
            raw_name TEXT NOT NULL,
            current_price REAL,
            brand TEXT,
            fingerprint TEXT UNIQUE,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (master_id) REFERENCES master_products(id)
        );

        CREATE TABLE IF NOT EXISTS competitor_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            master_id INTEGER,
            competitor_name TEXT NOT NULL,
            raw_name TEXT NOT NULL,
            price REAL NOT NULL,
            fingerprint TEXT,
            session_id TEXT,
            source_file TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (master_id) REFERENCES master_products(id)
        );

        CREATE TABLE IF NOT EXISTS competitor_latest (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            master_id INTEGER,
            competitor_name TEXT NOT NULL,
            raw_name TEXT NOT NULL,
            price REAL NOT NULL,
            previous_price REAL,
            fingerprint TEXT,
            price_changed INTEGER DEFAULT 0,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (master_id) REFERENCES master_products(id),
            UNIQUE(fingerprint, competitor_name)
        );

        CREATE TABLE IF NOT EXISTS missing_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint TEXT NOT NULL UNIQUE,
            raw_name TEXT NOT NULL,
            competitor_name TEXT NOT NULL,
            competitor_price REAL,
            brand TEXT,
            importance_score REAL DEFAULT 0,
            competitors_count INTEGER DEFAULT 1,
            competitors_list TEXT DEFAULT '[]',
            status TEXT DEFAULT 'new',
            possible_match_fp TEXT,
            possible_match_name TEXT,
            possible_match_score REAL DEFAULT 0,
            verified_by TEXT,
            verified_at TIMESTAMP,
            added_to_store_at TIMESTAMP,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS analysis_sessions (
            id TEXT PRIMARY KEY,
            my_file TEXT,
            competitor_files TEXT,
            total_my_products INTEGER,
            total_matched INTEGER,
            total_higher INTEGER,
            total_lower INTEGER,
            total_equal INTEGER,
            total_missing INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS match_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            my_product_id INTEGER,
            competitor_name TEXT,
            competitor_raw_name TEXT,
            my_price REAL,
            competitor_price REAL,
            price_diff REAL,
            match_confidence REAL,
            match_type TEXT,
            price_status TEXT,
            action_taken TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS action_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id INTEGER,
            target_fp TEXT,
            details TEXT,
            old_value TEXT,
            new_value TEXT,
            session_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS price_modifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            my_product_id INTEGER,
            my_product_no TEXT,
            my_product_name TEXT,
            old_price REAL,
            new_price REAL,
            price_diff REAL,
            reason TEXT,
            competitor_name TEXT,
            competitor_price REAL,
            status TEXT DEFAULT 'pending',
            sent_at TIMESTAMP,
            confirmed_at TIMESTAMP,
            session_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS missing_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            missing_id INTEGER,
            fingerprint TEXT,
            product_name TEXT,
            suggested_price REAL,
            brand TEXT,
            competitors_list TEXT,
            status TEXT DEFAULT 'pending',
            sent_at TIMESTAMP,
            added_at TIMESTAMP,
            new_product_no TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_master_fp ON master_products(fingerprint);
        CREATE INDEX IF NOT EXISTS idx_alias_name ON product_aliases(alias_name);
        CREATE INDEX IF NOT EXISTS idx_my_fp ON my_products(fingerprint);
        CREATE INDEX IF NOT EXISTS idx_comp_latest_fp ON competitor_latest(fingerprint, competitor_name);
        CREATE INDEX IF NOT EXISTS idx_missing_fp ON missing_products(fingerprint);
        CREATE INDEX IF NOT EXISTS idx_missing_status ON missing_products(status);
        CREATE INDEX IF NOT EXISTS idx_action_fp ON action_log(action, target_fp);
        """)
        self.conn.commit()

    # ─────────────────────────────────────────────
    # دوال عامة
    # ─────────────────────────────────────────────
    def insert(self, table, data: dict):
        keys = ",".join(data.keys())
        qmarks = ",".join(["?"] * len(data))
        values = list(data.values())
        sql = f"INSERT INTO {table} ({keys}) VALUES ({qmarks})"
        cur = self.conn.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid

    def update(self, table, data: dict, where: str, params: tuple):
        sets = ",".join([f"{k}=?" for k in data.keys()])
        sql = f"UPDATE {table} SET {sets}, updated_at=CURRENT_TIMESTAMP WHERE {where}"
        self.conn.execute(sql, list(data.values()) + list(params))
        self.conn.commit()

    def fetchone(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None

    def fetchall(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def delete(self, table, where, params=()):
        sql = f"DELETE FROM {table} WHERE {where}"
        self.conn.execute(sql, params)
        self.conn.commit()

    # ─────────────────────────────────────────────
    # Master Products
    # ─────────────────────────────────────────────
    def upsert_master_product(self, fingerprint, data):
        existing = self.conn.execute("SELECT id FROM master_products WHERE fingerprint=?", (fingerprint,)).fetchone()
        if existing:
            self.conn.execute("""
                UPDATE master_products 
                SET product_name=COALESCE(?,product_name),
                    brand=COALESCE(?,brand),
                    concentration=COALESCE(?,concentration),
                    size_ml=COALESCE(?,size_ml),
                    updated_at=CURRENT_TIMESTAMP
                WHERE fingerprint=?
            """, (
                data.get("product_name"),
                data.get("brand"),
                data.get("concentration"),
                data.get("size_ml"),
                fingerprint
            ))
            self.conn.commit()
            return existing["id"]

        cur = self.conn.execute("""
            INSERT INTO master_products 
            (fingerprint,brand,product_name,product_name_ar,concentration,size_ml,gender,category)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            fingerprint,
            data.get("brand"),
            data.get("product_name", ""),
            data.get("product_name_ar"),
            data.get("concentration"),
            data.get("size_ml"),
            data.get("gender"),
            data.get("category", "perfume")
        ))
        self.conn.commit()
        return cur.lastrowid

    def add_alias(self, master_id, alias_name, source="auto"):
        try:
            self.conn.execute(
                "INSERT OR IGNORE INTO product_aliases (master_id,alias_name,source) VALUES (?,?,?)",
                (master_id, alias_name.strip().lower(), source)
            )
            self.conn.commit()
        except:
            pass

    def find_by_alias(self, name):
        row = self.conn.execute("""
            SELECT m.* FROM master_products m 
            JOIN product_aliases a ON m.id=a.master_id 
            WHERE a.alias_name=?
        """, (name.strip().lower(),)).fetchone()
        return dict(row) if row else None

    # ─────────────────────────────────────────────
    # My Products
    # ─────────────────────────────────────────────
    def upsert_my_product(self, fingerprint, data):
        existing = self.conn.execute(
            "SELECT id, current_price FROM my_products WHERE fingerprint=?", 
            (fingerprint,)
        ).fetchone()

        if existing:
            if data.get("price") and data["price"] != existing["current_price"]:
                self.conn.execute("""
                    UPDATE my_products 
                    SET current_price=?, updated_at=CURRENT_TIMESTAMP 
                    WHERE fingerprint=?
                """, (data["price"], fingerprint))
            self.conn.commit()
            return existing["id"], False

        cur = self.conn.execute("""
            INSERT INTO my_products 
            (product_no,raw_name,current_price,brand,fingerprint)
            VALUES (?,?,?,?,?)
        """, (
            data.get("product_no"),
            data.get("raw_name"),
            data.get("price"),
            data.get("brand"),
            fingerprint
        ))
        self.conn.commit()
        return cur.lastrowid, True

    def get_all_my_fingerprints(self):
        rows = self.conn.execute("""
            SELECT fingerprint, raw_name, brand, current_price, product_no 
            FROM my_products 
            WHERE is_active=1
        """).fetchall()
        return {r["fingerprint"]: dict(r) for r in rows}

    # ─────────────────────────────────────────────
    # Competitor Prices
    # ─────────────────────────────────────────────
    def record_competitor_price(self, fingerprint, competitor_name, raw_name, price, master_id=None, session_id=None, source_file=None):
        self.conn.execute("""
            INSERT INTO competitor_prices 
            (master_id,competitor_name,raw_name,price,fingerprint,session_id,source_file)
            VALUES (?,?,?,?,?,?,?)
        """, (master_id, competitor_name, raw_name, price, fingerprint, session_id, source_file))

        existing = self.conn.execute("""
            SELECT id, price FROM competitor_latest 
            WHERE fingerprint=? AND competitor_name=?
        """, (fingerprint, competitor_name)).fetchone()

        price_changed, previous_price = False, None

        if existing:
            previous_price = existing["price"]
            if abs(price - previous_price) > 0.01:
                price_changed = True
                self.conn.execute("""
                    UPDATE competitor_latest 
                    SET price=?, previous_price=?, raw_name=?, price_changed=1, last_updated=CURRENT_TIMESTAMP 
                    WHERE fingerprint=? AND competitor_name=?
                """, (price, previous_price, raw_name, fingerprint, competitor_name))
            else:
                self.conn.execute("""
                    UPDATE competitor_latest 
                    SET last_updated=CURRENT_TIMESTAMP, price_changed=0 
                    WHERE fingerprint=? AND competitor_name=?
                """, (fingerprint, competitor_name))
        else:
            self.conn.execute("""
                INSERT INTO competitor_latest 
                (master_id,competitor_name,raw_name,price,fingerprint)
                VALUES (?,?,?,?,?)
            """, (master_id, competitor_name, raw_name, price, fingerprint))

        self.conn.commit()
        return price_changed, previous_price

    # ─────────────────────────────────────────────
    # Missing Products
    # ─────────────────────────────────────────────
    def record_missing_product(self, fingerprint, raw_name, competitor_name, competitor_price=None, brand=None, possible_match_fp=None, possible_match_name=None, possible_match_score=0):
        existing = self.conn.execute("""
            SELECT id, competitors_count, competitors_list, status 
            FROM missing_products 
            WHERE fingerprint=?
        """, (fingerprint,)).fetchone()

        if existing:
            if existing["status"] in ("is_duplicate", "added_to_store", "ignored"):
                return existing["id"], False

            try:
                comp_list = json.loads(existing["competitors_list"] or "[]")
            except:
                comp_list = []

            if competitor_name not in comp_list:
                comp_list.append(competitor_name)

            new_count = len(comp_list)
            importance = min(100, new_count * 20 + (30 if competitor_price and competitor_price > 100 else 0))

            self.conn.execute("""
                UPDATE missing_products 
                SET competitors_count=?, competitors_list=?, importance_score=?,
                    competitor_price=COALESCE(?,competitor_price),
                    possible_match_fp=COALESCE(?,possible_match_fp),
                    possible_match_name=COALESCE(?,possible_match_name),
                    possible_match_score=CASE WHEN ?>possible_match_score THEN ? ELSE possible_match_score END,
                    updated_at=CURRENT_TIMESTAMP
                WHERE fingerprint=?
            """, (
                new_count,
                json.dumps(comp_list, ensure_ascii=False),
                importance,
                competitor_price,
                possible_match_fp,
                possible_match_name,
                possible_match_score,
                possible_match_score,
                fingerprint
            ))
            self.conn.commit()
            return existing["id"], False

        importance = 20 + (30 if competitor_price and competitor_price > 100 else 0)
        status = "needs_review" if possible_match_score >= 50 else "new"

        cur = self.conn.execute("""
            INSERT INTO missing_products 
            (fingerprint,raw_name,competitor_name,competitor_price,brand,importance_score,competitors_list,status,possible_match_fp,possible_match_name,possible_match_score)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            fingerprint,
            raw_name,
            competitor_name,
            competitor_price,
            brand,
            importance,
            json.dumps([competitor_name], ensure_ascii=False),
            status,
            possible_match_fp,
            possible_match_name,
            possible_match_score
        ))
        self.conn.commit()
        return cur.lastrowid, True

    # ─────────────────────────────────────────────
    # Missing Verification
    # ─────────────────────────────────────────────
    def verify_missing_is_duplicate(self, missing_id, my_fingerprint):
        missing = self.conn.execute("SELECT * FROM missing_products WHERE id=?", (missing_id,)).fetchone()
        if not missing:
            return False

        self.conn.execute("""
            UPDATE missing_products 
            SET status='is_duplicate', verified_by='user', verified_at=CURRENT_TIMESTAMP, possible_match_fp=? 
            WHERE id=?
        """, (my_fingerprint, missing_id))

        master = self.conn.execute("SELECT id FROM master_products WHERE fingerprint=?", (my_fingerprint,)).fetchone()
        if master:
            self.add_alias(master["id"], missing["raw_name"].strip().lower(), "user_verified")

        self.log_action("missing_is_duplicate", "missing", missing_id, missing["fingerprint"], f"'{missing['raw_name']}' = منتج موجود")
        self.conn.commit()
        return True

    def verify_missing_confirmed(self, missing_id):
        self.conn.execute("""
            UPDATE missing_products 
            SET status='verified_missing', verified_by='user', verified_at=CURRENT_TIMESTAMP 
            WHERE id=?
        """, (missing_id,))
        self.log_action("missing_verified", "missing", missing_id)
        self.conn.commit()

    def mark_missing_added_to_store(self, missing_id, product_no=None, notes=None):
        missing = self.conn.execute("SELECT * FROM missing_products WHERE id=?", (missing_id,)).fetchone()
        if not missing:
            return None

        self.conn.execute("""
            UPDATE missing_products 
            SET status='added_to_store', added_to_store_at=CURRENT_TIMESTAMP 
            WHERE id=?
        """, (missing_id,))

        cur = self.conn.execute("""
            INSERT INTO missing_migrations 
            (missing_id,fingerprint,product_name,suggested_price,brand,competitors_list,status,added_at,new_product_no,notes)
            VALUES (?,?,?,?,?,?,'added',CURRENT_TIMESTAMP,?,?)
        """, (
            missing_id,
            missing["fingerprint"],
            missing["raw_name"],
            missing["competitor_price"],
            missing["brand"],
            missing["competitors_list"],
            product_no,
            notes
        ))

        self.log_action("missing_added_to_store", "missing", missing_id, missing["fingerprint"], f"أُضيف '{missing['raw_name']}' للمتجر")
        self.conn.commit()
        return cur.lastrowid

    def mark_missing_ignored(self, missing_id, reason=""):
        self.conn.execute("""
            UPDATE missing_products 
            SET status='ignored', notes=?, verified_at=CURRENT_TIMESTAMP 
            WHERE id=?
        """, (reason, missing_id))
        self.log_action("missing_ignored", "missing", missing_id, details=reason)
        self.conn.commit()

    # ─────────────────────────────────────────────
    # Price Modifications
    # ─────────────────────────────────────────────
    def create_price_modification(self, my_product_id, product_no, product_name, old_price, new_price, reason="", competitor_name="", competitor_price=0, session_id=None):
        existing = self.conn.execute("""
            SELECT id FROM price_modifications 
            WHERE my_product_id=? AND status='pending'
        """, (my_product_id,)).fetchone()

        if existing:
            self.conn.execute("""
               

