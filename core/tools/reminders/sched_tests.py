import asyncio

from core.tools.reminders.scheduler import Scheduler



class MockRepository:
    def __init__(self):
        self.called = False

    def timesearch_reminders(
        self,
        kind,
        day,
        month,
        time_start,
        time_end
    ):
        self.called = True

        return [
            {
                "reminder_id": 1,
                "title": "Wake up",
                "comment": "Time to work"
            }
        ]


async def mock_callback(reminder):
    print("ALARM FIRED:")
    print(reminder)


async def main():
    repo = MockRepository()

    scheduler = Scheduler(
        repository=repo,
        on_alarm=mock_callback
    )

    calls = 0

    async def fake_wait():
        nonlocal calls

        calls += 1

        # первый wait — старт цикла
        # второй wait — остановка после 1 прохода
        if calls >= 2:
            scheduler.running = False

    scheduler.wait_next_minute = fake_wait

    await scheduler.run()

    print()
    print("Repository called:", repo.called)
    print("Scheduler stopped:", not scheduler.running)


if __name__ == "__main__":
    asyncio.run(main())