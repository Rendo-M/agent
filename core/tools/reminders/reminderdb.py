import sqlite3
from typing import List, Dict, Any, Optional


class ReminderDB:
    def __init__(self, db_path: str):
        """
        Инициализация SQLite подключения.
        Initializes SQLite connection.
        """
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

        self._init_db()

    # ---------------- INIT ----------------

    def _init_db(self):
        """
        Создание таблиц.
        Creates tables if not exist.
        """

        self.cur.executescript("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            comment TEXT,
            enabled INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            timezone TEXT
        );

        CREATE TABLE IF NOT EXISTS triggers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reminder_id INTEGER,
            kind TEXT,
            day INTEGER,
            month INTEGER,
            time INTEGER,
            year INTEGER
        );
        """)

        self.conn.commit()

    

    # ---------------- CREATE ----------------

    def add_reminder(
        self,
        title: str,
        comment: str,
        timezone: str,
        triggers: List[Dict[str, Any]]
    ) -> int:
        """
        Создание напоминания с триггерами.
        Create reminder with triggers.
        """

        self.cur.execute("""
            INSERT INTO reminders (
                title,
                comment,
                enabled,
                timezone
            )
            VALUES (?, ?, 1, ?)
        """, (
            title,
            comment,
            timezone
        ))

        reminder_id = self.cur.lastrowid

        for t in triggers:
            self.cur.execute("""
                INSERT INTO triggers (
                    reminder_id,
                    kind,
                    day,
                    month,
                    time,
                    year
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                reminder_id,
                t.get("kind"),
                t.get("day"),
                t.get("month"),
                t.get("time"),
                t.get("year"),
            ))

        self.conn.commit()

        return reminder_id

    # ---------------- READ ----------------

    def textsearch_reminders(
        self,
        text: Optional[str] = None,
        enabled: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Поиск напоминаний по тексту.
        Text search reminders.
        """

        q = """
        SELECT
            r.id as reminder_id,
            r.title,
            r.comment,
            r.enabled,
            r.created_at,
            r.timezone,

            t.id as trigger_id,
            t.kind,
            t.day,
            t.month,
            t.time,
            t.year

        FROM reminders r
        JOIN triggers t
            ON r.id = t.reminder_id

        WHERE 1=1
        """

        params = []

        if text:
            q += """
            AND (
                r.title LIKE ?
                OR r.comment LIKE ?
            )
            """

            params += [
                f"%{text}%",
                f"%{text}%"
            ]

        if enabled is not None:
            q += " AND r.enabled = ?"
            params.append(enabled)

        self.cur.execute(q, params)

        return [dict(r) for r in self.cur.fetchall()]


    def timesearch_reminders(
        self,
        kind: str,
        day: int,
        month: int,
        time_start: int,
        time_end: int,
        only_active: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Поиск reminders по параметрам trigger.
        Search reminders by trigger params.
        """

        q = """
        SELECT
            r.id as reminder_id,
            r.title,
            r.comment,
            r.enabled,
            r.created_at,
            r.timezone,

            t.id as trigger_id,
            t.kind,
            t.day,
            t.month,
            t.time,
            t.year

        FROM reminders r
        JOIN triggers t
            ON r.id = t.reminder_id

        WHERE
            t.kind = ?
            AND t.day = ?
            AND t.month = ?
            AND t.time BETWEEN ? AND ?
        """

        params = [
            kind,
            day,
            month,
            time_start,
            time_end
        ]

        if only_active:
            q += " AND r.enabled = 1"

        self.cur.execute(q, params)

        return [dict(r) for r in self.cur.fetchall()]


    def get_reminders(
        self,
        enabled: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Получение напоминаний с JOIN triggers.
        Get reminders with joined triggers.
        """

        q = """
        SELECT
            r.id as reminder_id,
            r.title,
            r.comment,
            r.enabled,
            r.created_at,
            r.timezone,

            t.id as trigger_id,
            t.kind,
            t.day,
            t.month,
            t.time,
            t.year

        FROM reminders r
        JOIN triggers t
            ON r.id = t.reminder_id
        """

        params = []

        if enabled is not None:
            q += " WHERE r.enabled = ?"
            params.append(enabled)

        self.cur.execute(q, params)

        return [dict(r) for r in self.cur.fetchall()]

    # ---------------- UPDATE ----------------

    def disable_reminder(self, reminder_id: int):
        """
        Отключение напоминания.
        Disable reminder.
        """

        self.cur.execute("""
            UPDATE reminders
            SET enabled = 0
            WHERE id = ?
        """, (reminder_id,))

        self.conn.commit()

    # ---------------- DELETE ----------------

    def delete_reminder(self, reminder_id: int):
        """
        Удаление напоминания и триггеров.
        Delete reminder and triggers.
        """

        self.cur.execute("""
            DELETE FROM triggers
            WHERE reminder_id = ?
        """, (reminder_id,))

        self.cur.execute("""
            DELETE FROM reminders
            WHERE id = ?
        """, (reminder_id,))

        self.conn.commit()

    # ---------------- UTIL ----------------

    def close(self):
        """
        Закрытие соединения.
        Close DB connection.
        """

        self.conn.close()