import asyncio
import time
from typing import List, Dict, Any, Optional


class Scheduler:
    def __init__(self, repository, on_alarm):
        """
        Инициализация Scheduler.
        Initializes Scheduler.

        repository: слой доступа к данным
        on_alarm: callback обработки сработавшего напоминания
        """
        self.repository = repository
        self.on_alarm = on_alarm

        self.running = False
        self.muted = False

        # очередь сработавших напоминаний при mute
        self.queue: Dict[int, Dict[str, Any]] = {}

    # ---------------- TIME ----------------

    def time_to_minutes(self, time_str: str) -> int:
        """
        Конвертация HH:MM -> minutes.
        Convert HH:MM to minutes.
        """
        h, m = map(int, time_str.split(":"))
        return h * 60 + m

    def minutes_to_time(self, minutes: int) -> str:
        """
        Конвертация minutes -> HH:MM.
        Convert minutes to HH:MM.
        """
        h = minutes // 60
        m = minutes % 60
        return f"{h:02d}:{m:02d}"

    def get_now_minutes(self) -> int:
        """
        Текущее время в минутах от полуночи.
        Current time in minutes from midnight.
        """
        t = time.localtime()
        return t.tm_hour * 60 + t.tm_min

    # ---------------- CORE LOGIC ----------------

    def check_alarms(self, now: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Проверка сработавших напоминаний.
        Returns reminders that should fire now.
        """

        if now is None:
            now = self.get_now_minutes()

        return self.repository.timesearch_reminders(
            kind="*",          # временно универсально (можно убрать при доработке)
            day=0,
            month=0,
            time_start=now,
            time_end=now
        )

    async def wait_next_minute(self):
        """
        Ждёт смены минуты (без drift).
        Wait until next minute boundary.
        """

        min1 = self.get_now_minutes()

        while True:
            await asyncio.sleep(0.2)
            min2 = self.get_now_minutes()

            if min1 != min2:
                break

    # ---------------- MUTE LOGIC ----------------

    def mute(self):
        """
        Включить заглушение уведомлений.
        Enable mute mode.
        """
        self.muted = True

    def unmute(self):
        """
        Выключить заглушение и отправить накопленные уведомления.
        Disable mute and flush queue.
        """

        self.muted = False

        for reminder in list(self.queue.values()):
            try:
                asyncio.create_task(self.on_alarm(reminder))
            except Exception as e:
                print(e)

        self.queue.clear()

    # ---------------- RUN LOOP ----------------

    async def run(self):
        """
        Главный цикл Scheduler.
        Main scheduler loop.
        """

        self.running = True

        # синхронизация на границе минуты
        await self.wait_next_minute()

        while self.running:

            reminders = self.check_alarms()

            for r in reminders:
                rid = r["reminder_id"]

                if self.muted:
                    self.queue[rid] = r
                    continue

                try:
                    await self.on_alarm(r)
                except Exception as e:
                    print(e)

            await self.wait_next_minute()

    def stop(self):
        """
        Остановка Scheduler.
        Stop scheduler loop.
        """
        self.running = False