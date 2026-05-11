import logging
from datetime import datetime
from typing import Optional


# Настройка журнала сообщений
msg_logger = logging.getLogger("messages")
msg_logger.setLevel(logging.INFO)
msg_handler = logging.FileHandler("messages.log", encoding="utf-8", mode="a")
msg_formatter = logging.Formatter("%(message)s")
msg_handler.setFormatter(msg_formatter)
msg_logger.addHandler(msg_handler)

# Настройка журнала базы данных
db_logger = logging.getLogger("database")
db_logger.setLevel(logging.INFO)
db_handler = logging.FileHandler("database.log", encoding="utf-8", mode="a")
db_formatter = logging.Formatter("%(message)s")
db_handler.setFormatter(db_formatter)
db_logger.addHandler(db_handler)


def log_message(username: str, user_id: str, direction: str, text: str) -> None:
    """Log a message exchange with user.
    direction: 'snd' (sent) or 'rsv' (received)
    Format: time date;Имя пользователя;user ID;[snd/rsv];msg text
    """
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
    
    log_entry = f"{time_str} {date_str};{username};{user_id};[{direction}];{text}"
    msg_logger.info(log_entry)


def log_db_operation(
    table_name: str,
    operation: str,
    old_record: Optional[dict] = None,
    new_record: Optional[dict] = None
) -> None:
    """Log a database operation.
    operation: 'add', 'edit', or 'delete'
    Format: time date;table name;[delete/edit/add];old record fields(if exists)
    / Логирует операцию в базе данных.
    operation: 'add', 'edit' или 'delete'
    Формат: time date;table name;[delete/edit/add];old record fields(if exists)
    """
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
    
    old_fields = ""
    if old_record:
        old_fields = ";".join([f"{k}={v}" for k, v in old_record.items()])
    
    log_entry = f"{time_str} {date_str};{table_name};[{operation}];{old_fields}"
    
    try:
        db_logger.info(log_entry)
    except Exception as e:
        print(f"Error writing to log file: {e}")