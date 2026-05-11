import sqlite3
import asyncio
from datetime import datetime, time
from typing import List, Tuple, Optional
import logging

from services.logger import log_db_operation

logging.basicConfig(level=logging.INFO)

class ReminderEngine:
    def __init__(self, db_path: str = "reminders.db", bot=None):
        """Initialize the reminder engine and database. / Инициализирует движок напоминаний и базу данных."""
        self.db_path = db_path
        self.bot = bot
        self._init_db()
        self._running = False
        self._sent_reminder_ids = set()
        self._last_sent_minute = None

    def _init_db(self):
        """Create the reminders table and add missing columns. / Создает таблицу напоминаний и добавляет отсутствующие столбцы."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    period TEXT NOT NULL,
                    reminder_time TEXT NOT NULL,
                    day TEXT,
                    comment TEXT,
                    active INTEGER DEFAULT 1
                )
            ''')
            conn.commit()
            cursor = conn.execute("PRAGMA table_info(reminders)")
            columns = [row[1] for row in cursor.fetchall()]
            if "comment" not in columns:
                conn.execute("ALTER TABLE reminders ADD COLUMN comment TEXT")
                conn.commit()
            if "due_at" not in columns:
                conn.execute("ALTER TABLE reminders ADD COLUMN due_at TEXT")
                conn.commit()

    def add_reminder(
        self,
        user_id: str,
        name: str,
        period: str,
        reminder_time: str,
        day: Optional[str] = None,
        comment: Optional[str] = None,
        due_at: Optional[str] = None,
    ) -> bool:
        """Store a new reminder for a user. / Сохраняет новое напоминание для пользователя."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO reminders (user_id, name, period, reminder_time, day, comment, active, due_at) VALUES (?, ?, ?, ?, ?, ?, 1, ?)",
                    (user_id, name, period, reminder_time, day, comment, due_at),
                )
                conn.commit()
                
                new_record = {
                    "user_id": user_id,
                    "name": name,
                    "period": period,
                    "reminder_time": reminder_time,
                    "day": day,
                    "comment": comment,
                    "active": 1,
                    "due_at": due_at
                }
                log_db_operation("reminders", "add", old_record=None, new_record=new_record)
                
            return True
        except Exception as e:
            logging.error(f"Error adding reminder: {e}")
            return False

    def get_reminders(self, user_id: str) -> List[Tuple]:
        """Return all reminders for a user. / Возвращает все напоминания пользователя."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT name, comment, period, reminder_time, day, due_at, active FROM reminders WHERE user_id = ?",
                (user_id,)
            )
            return cursor.fetchall()

    def deactivate_reminder(self, user_id: str, name: str) -> bool:
        """Mark a reminder as inactive for a user. / Помечает напоминание пользователя как неактивное."""
        with sqlite3.connect(self.db_path) as conn:
            # Get old record
            cursor = conn.execute(
                "SELECT user_id, name, period, reminder_time, day, comment, active, due_at FROM reminders WHERE user_id = ? AND name = ?",
                (user_id, name)
            )
            old_record = cursor.fetchone()
            
            cursor = conn.execute(
                "UPDATE reminders SET active = 0 WHERE user_id = ? AND name = ?",
                (user_id, name)
            )
            conn.commit()
            
            if cursor.rowcount > 0 and old_record:
                old_dict = {
                    "user_id": old_record[0],
                    "name": old_record[1],
                    "period": old_record[2],
                    "reminder_time": old_record[3],
                    "day": old_record[4],
                    "comment": old_record[5],
                    "active": old_record[6],
                    "due_at": old_record[7]
                }
                new_dict = old_dict.copy()
                new_dict["active"] = 0
                log_db_operation("reminders", "edit", old_record=old_dict, new_record=new_dict)
            
            return cursor.rowcount > 0

    def delete_reminder(self, user_id: str, name: str) -> bool:
        """Delete a reminder by name for a user. / Удаляет напоминание по имени для пользователя."""
        with sqlite3.connect(self.db_path) as conn:
            # Get old record
            cursor = conn.execute(
                "SELECT user_id, name, period, reminder_time, day, comment, active, due_at FROM reminders WHERE user_id = ? AND name = ?",
                (user_id, name)
            )
            old_record = cursor.fetchone()
            
            cursor = conn.execute(
                "DELETE FROM reminders WHERE user_id = ? AND name = ?",
                (user_id, name)
            )
            conn.commit()
            
            if cursor.rowcount > 0 and old_record:
                old_dict = {
                    "user_id": old_record[0],
                    "name": old_record[1],
                    "period": old_record[2],
                    "reminder_time": old_record[3],
                    "day": old_record[4],
                    "comment": old_record[5],
                    "active": old_record[6],
                    "due_at": old_record[7]
                }
                log_db_operation("reminders", "delete", old_record=old_dict)
            
            return cursor.rowcount > 0

    async def start(self):
        """Run the background reminder loop. / Запускает фоновый цикл проверки напоминаний."""
        self._running = True
        while self._running:
            await self._check_reminders()
            await asyncio.sleep(10)  # Check more frequently so new reminders are handled quickly

    async def refresh(self):
        """Immediately check for due reminders after a new reminder is added. / Немедленно проверяет сработавшие напоминания после добавления нового."""
        await self._check_reminders()

    def stop(self):
        """Stop the reminder worker loop. / Останавливает рабочий цикл напоминаний."""
        self._running = False

    async def _check_reminders(self):
        """Check active reminders and send notifications when they are due. / Проверяет активные напоминания и отправляет уведомления, когда они выполняются."""
        now = datetime.now()
        current_minute = now.strftime("%Y-%m-%d %H:%M")
        current_time = now.strftime("%H:%M")
        current_weekday = now.weekday() + 1  # 1=Monday, 7=Sunday
        current_day = now.day
        current_date = now.strftime("%d.%m")

        if self._last_sent_minute != current_minute:
            self._sent_reminder_ids.clear()
            self._last_sent_minute = current_minute

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, user_id, name, comment, period, reminder_time, day, due_at FROM reminders WHERE active = 1")
            reminders = cursor.fetchall()

        for reminder_id, user_id, name, comment, period, reminder_time, day, due_at in reminders:
            if period == "once":
                if not due_at:
                    continue
                try:
                    due_datetime = datetime.fromisoformat(due_at)
                except ValueError:
                    continue

                if due_datetime > now:
                    continue

                if reminder_id in self._sent_reminder_ids:
                    continue

                should_remind = True
            else:
                if reminder_time != current_time:
                    continue

                if reminder_id in self._sent_reminder_ids:
                    continue

                should_remind = False
                if period == "daily":
                    should_remind = True
                elif period == "weekly" and day and int(day) == current_weekday:
                    should_remind = True
                elif period == "monthly" and day and int(day) == current_day:
                    should_remind = True
                elif period == "yearly" and day == current_date:
                    should_remind = True

            if should_remind and self.bot:
                try:
                    message_text = f"Напоминание: {name}"
                    if comment:
                        message_text = f"Напоминание: {name}: {comment}"
                    await self.bot.send_message(chat_id=int(user_id), text=message_text)
                    self._sent_reminder_ids.add(reminder_id)
                    if period == "once":
                        with sqlite3.connect(self.db_path) as conn:
                            # Get old record before deletion
                            old_cursor = conn.execute("SELECT user_id, name, period, reminder_time, day, comment, active, due_at FROM reminders WHERE id = ?", (reminder_id,))
                            old_row = old_cursor.fetchone()
                            if old_row:
                                old_dict = {
                                    "user_id": old_row[0],
                                    "name": old_row[1],
                                    "period": old_row[2],
                                    "reminder_time": old_row[3],
                                    "day": old_row[4],
                                    "comment": old_row[5],
                                    "active": old_row[6],
                                    "due_at": old_row[7]
                                }
                                log_db_operation("reminders", "delete", old_record=old_dict)
                            conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
                            conn.commit()
                except Exception as e:
                    logging.error(f"Error sending reminder to {user_id}: {e}")
