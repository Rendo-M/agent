from typing import List, Dict, Any, Optional


class ReminderRepository:
    def __init__(self, db):
        """
        Репозиторий над ReminderDB.
        Handles aggregation and time conversion.

        Repository layer over ReminderDB.
        Responsible for aggregation and time conversion.
        """
        self.db = db

   # ---------------- INTERNAL MAP ----------------

    def _build(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Агрегация плоских JOIN строк в структуру напоминаний.

        Aggregate flat JOIN rows into structured reminders.
        """

        grouped = {}

        for r in rows:
            rid = r["reminder_id"]

            if rid not in grouped:
                grouped[rid] = {
                    "id": rid,
                    "title": r["title"],
                    "comment": r["comment"],
                    "timezone": r["timezone"],
                    "enabled": r["enabled"],
                    "created_at": r["created_at"],
                    "triggers": []
                }

            grouped[rid]["triggers"].append({
                "id": r["trigger_id"],
                "kind": r["kind"],
                "day": r["day"],
                "month": r["month"],
                "time": r["time"],
                "year": r["year"]
            })

        return list(grouped.values())

    # ---------------- SEARCH ----------------

    def textsearch_reminders(
        self,
        text: Optional[str] = None,
        enabled: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Поиск напоминаний по тексту (title/comment).

        Search reminders by text (title/comment).
        """

        rows = self.db.textsearch_reminders(text=text, enabled=enabled)
        return self._build(rows)

    def timesearch_reminders(
        self,
        kind: str,
        day: int,
        month: int,
        time_start: str,
        time_end: str,
        only_active: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Поиск напоминаний по параметрам триггера времени.

        Search reminders by trigger time parameters.
        """

        rows = self.db.search_triggers(
            kind=kind,
            day=day,
            month=month,
            time_start=time_start,
            time_end=time_end,
            only_active=only_active
        )

        return self._build(rows)

    def get_reminders(
        self,
        enabled: Optional[int] = 1
    ) -> List[Dict[str, Any]]:
        """
        Получение всех напоминаний с триггерами.

        Get all reminders with triggers.
        """

        rows = self.db.get_reminders(enabled=enabled)
        return self._build(rows)

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

        prepared = []

        for t in triggers:
            prepared.append({
                "kind": t.get("kind"),
                "day": t.get("day"),
                "month": t.get("month"),
                "time": t.get("time"),
                "year": t.get("year")
            })

        return self.db.add_reminder(
            title=title,
            comment=comment,
            timezone=timezone,
            triggers=prepared
        )

    # ---------------- DELETE ----------------

    def delete_reminder(self, reminder_id: int):
        """
        Удаление напоминания.

        Delete reminder.
        """
        self.db.delete_reminder(reminder_id)

    # ---------------- DISABLE ----------------

    def disable_reminder(self, reminder_id: int):
        """
        Отключение напоминания.

        Disable reminder.
        """
        self.db.disable_reminder(reminder_id)

    # ---------------- CLOSE ----------------

    def close(self):
        """
        Закрытие соединения с базой данных.

        Close database connection.
        """
        self.db.close()