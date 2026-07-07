import sqlite3
import threading
from datetime import datetime
from bdb_server.auth import hash_password


class Database:
    def __init__(self, path):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id    TEXT PRIMARY KEY,
                username      TEXT UNIQUE NOT NULL,
                pwhash        TEXT NOT NULL,
                balance_cents INTEGER NOT NULL DEFAULT 0
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transfers (
                transfer_id  TEXT PRIMARY KEY,
                sender_id    TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                fee_cents    INTEGER NOT NULL,
                status       TEXT NOT NULL,
                reference    TEXT,
                created_at   TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def seed(self):
        users = [
            ("1", "user1", hash_password("password1"), 500000),   # $5,000
            ("2", "user2", hash_password("password2"), 1000),     # $10
            ("3", "user3", hash_password("password3"), 99900000), # $999,000
            ("4", "user4", hash_password("password4"), 4000000),  # 40,000
            ("5", "user5", hash_password("password5"), 15000000), # $150,000
            ("6", "user6", hash_password("password6"), 0),        # $0
       ]
        with self.lock:
            self.conn.executemany("INSERT OR IGNORE INTO accounts (account_id, username, pwhash, balance_cents) VALUES (?, ?, ?, ?)", users)
            self.conn.commit()

    def get_user(self, username):
        row = self.conn.execute("SELECT * FROM accounts WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None

    def balance(self, account_id):
        row = self.conn.execute("SELECT balance_cents FROM accounts WHERE account_id = ?", (account_id,)).fetchone()
        return row["balance_cents"] if row else None

    def status(self, transfer_id):
        row = self.conn.execute("SELECT * FROM transfers WHERE transfer_id = ?", (transfer_id,)).fetchone()
        return dict(row) if row else None

    def transfer(self, transfer_id, sender_id, recipient_id, amount_cents, fee_cents, reference=None):
        with self.lock:
            existing = self.status(transfer_id)
            if existing:
                return existing

            total = amount_cents + fee_cents
            sender = self.balance(sender_id)
            recipient = self.balance(recipient_id)

            # Account doesnt exist, or not enough money
            if sender is None or recipient is None:
                status = "FAILED: Invalid recipient"
            elif sender < total:
                status = "FAILED: Insufficient funds"
            else:
                status = "COMPLETED"
                self.conn.execute("UPDATE accounts SET balance_cents = balance_cents - ? WHERE account_id = ?", (total, sender_id))
                self.conn.execute("UPDATE accounts SET balance_cents = balance_cents + ? WHERE account_id = ?", (amount_cents, recipient_id))

            self.conn.execute(
                "INSERT INTO transfers (transfer_id, sender_id, recipient_id, amount_cents, fee_cents, status, reference, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (transfer_id, sender_id, recipient_id, amount_cents, fee_cents, status, reference, datetime.now().isoformat()),
            )

            self.conn.commit()

            return self.status(transfer_id)
