# Database Documentation

## Overview

The project uses SQLite for persistent storage of reminders.

## Database File

- **File**: `reminders.db`
- **Location**: Project root
- **Type**: SQLite 3

## Schema

### Table: reminders

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

### Fields

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Auto-incrementing primary key |
| user_id | TEXT | Telegram user ID (string) |
| name | TEXT | Reminder name |
| period | TEXT | Period type: daily, weekly, monthly, yearly |
| reminder_time | TEXT | Time in HH:MM format |
| day | TEXT | Day specification (NULL for daily) |
| active | INTEGER | 1=active, 0=inactive |

## Period Formats

### daily
- `day`: NULL
- Example: Reminder every day at specified time

### weekly
- `day`: "1" to "7" (1=Monday, 7=Sunday)
- Example: "1" = every Monday

### monthly
- `day`: "1" to "31" (day of month)
- Example: "15" = 15th of every month

### yearly
- `day`: "DD.MM" format
- Example: "25.12" = December 25th every year

## Operations

### Add Reminder
```python
INSERT INTO reminders (user_id, name, period, reminder_time, day, active)
VALUES (?, ?, ?, ?, ?, 1)
```

### Get User Reminders
```python
SELECT name, period, reminder_time, day, active
FROM reminders
WHERE user_id = ?
```

### Deactivate Reminder
```python
UPDATE reminders SET active = 0
WHERE user_id = ? AND name = ?
```

### Check Due Reminders
```python
SELECT user_id, name, period, reminder_time, day
FROM reminders
WHERE active = 1
```

## Maintenance

- Database is created automatically on first use
- No migrations needed (simple schema)
- File is ignored in .gitignore
- Concurrent access handled by SQLite locking