# Схема Базы Данных

## Обзор

Проект использует SQLite для постоянного хранения напоминаний.

## Файл Базы Данных

- **Файл**: `reminders.db`
- **Расположение**: Корень проекта
- **Тип**: SQLite 3

## Схема

### Таблица: reminders

```sql
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    period TEXT NOT NULL,
    reminder_time TEXT NOT NULL,
    day TEXT,
    active INTEGER DEFAULT 1
);
```

### Поля

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Автоинкрементный первичный ключ |
| user_id | TEXT | ID пользователя Telegram (строка) |
| name | TEXT | Имя напоминания |
| period | TEXT | Тип периода: daily, weekly, monthly, yearly |
| reminder_time | TEXT | Время в формате ЧЧ:ММ |
| day | TEXT | Спецификация дня (NULL для daily) |
| active | INTEGER | 1=активно, 0=неактивно |

## Форматы Периодов

### daily
- `day`: NULL
- Пример: Напоминание каждый день в указанное время

### weekly
- `day`: "1" до "7" (1=Понедельник, 7=Воскресенье)
- Пример: "1" = каждый понедельник

### monthly
- `day`: "1" до "31" (день месяца)
- Пример: "15" = 15-го каждого месяца

### yearly
- `day`: "ДД.ММ" формат
- Пример: "25.12" = 25 декабря каждого года

## Операции

### Добавить Напоминание
```python
INSERT INTO reminders (user_id, name, period, reminder_time, day, active)
VALUES (?, ?, ?, ?, ?, 1)
```

### Получить Напоминания Пользователя
```python
SELECT name, period, reminder_time, day, active
FROM reminders
WHERE user_id = ?
```

### Деактивировать Напоминание
```python
UPDATE reminders SET active = 0
WHERE user_id = ? AND name = ?
```

### Проверить Просроченные Напоминания
```python
SELECT user_id, name, period, reminder_time, day
FROM reminders
WHERE active = 1
```

## Обслуживание

- База данных создается автоматически при первом использовании
- Миграции не нужны (простая схема)
- Файл игнорируется в .gitignore
- Конкурентный доступ обрабатывается блокировкой SQLite