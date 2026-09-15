
import logging
from datetime import datetime
import os
from logging.handlers import RotatingFileHandler

# Настройка общей системы логирования
def setup_logging():
    """Настраивает полную систему логирования"""
    
    # Создаем папку для логов если не существует
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Общий формат для всех логгеров
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # === ЛОГГЕР ОШИБОК TELEGRAM ===
    telegram_logger = logging.getLogger("telegram_errors")
    telegram_logger.setLevel(logging.ERROR)
    
    # Ротационный обработчик для ошибок (макс 10MB, 5 файлов)
    telegram_handler = RotatingFileHandler(
        f"logs/telegram_errors.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    telegram_handler.setLevel(logging.ERROR)
    telegram_handler.setFormatter(formatter)
    telegram_logger.addHandler(telegram_handler)
    
    # === ЛОГГЕР ОБЩЕЙ СИСТЕМЫ ===
    system_logger = logging.getLogger("system")
    system_logger.setLevel(logging.INFO)
    
    # Ротационный обработчик для системы (макс 20MB, 10 файлов)
    system_handler = RotatingFileHandler(
        f"logs/system.log",
        maxBytes=20*1024*1024,  # 20MB
        backupCount=10,
        encoding='utf-8'
    )
    system_handler.setLevel(logging.INFO)
    system_handler.setFormatter(formatter)
    system_logger.addHandler(system_handler)
    
    # === ЛОГГЕР STEAM API (отдельно) ===
    steam_logger = logging.getLogger("steam_api")
    steam_logger.setLevel(logging.INFO)
    
    # Ротационный обработчик для Steam API (макс 5MB, 3 файла)
    steam_handler = RotatingFileHandler(
        f"logs/steam_api.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    steam_handler.setLevel(logging.INFO)
    steam_handler.setFormatter(formatter)
    steam_logger.addHandler(steam_handler)
    
    # === ЛОГГЕР ОПЕРАЦИЙ ПОЛЬЗОВАТЕЛЕЙ ===
    user_operations_logger = logging.getLogger("user_operations")
    user_operations_logger.setLevel(logging.INFO)
    
    # Ротационный обработчик для операций пользователей (макс 15MB, 7 файлов)
    user_operations_handler = RotatingFileHandler(
        f"logs/user_operations.log",
        maxBytes=15*1024*1024,  # 15MB
        backupCount=7,
        encoding='utf-8'
    )
    user_operations_handler.setLevel(logging.INFO)
    user_operations_handler.setFormatter(formatter)
    user_operations_logger.addHandler(user_operations_handler)
    
    return telegram_logger, system_logger, steam_logger, user_operations_logger

# Глобальные логгеры
telegram_error_logger, system_logger, steam_api_logger, user_operations_logger = setup_logging()

def log_telegram_error(error_type, user_id, error_message):
    """Логирует ошибки Telegram"""
    telegram_error_logger.error(
        f"Type: {error_type}, User: {user_id}, Error: {error_message}"
    )

def log_mailing_stats(total_users, success_count, failed_count):
    """Логирует статистику рассылки"""
    system_logger.info(
        f"Mailing completed: Total={total_users}, Success={success_count}, Failed={failed_count}"
    )

def log_system_event(message):
    """Логирует системные события"""
    system_logger.info(message)

def log_steam_api_event(message, level="info"):
    """Логирует события Steam API"""
    if level.lower() == "error":
        steam_api_logger.error(message)
    elif level.lower() == "warning":
        steam_api_logger.warning(message)
    else:
        steam_api_logger.info(message)

def log_user_operation(user_id, operation, details=""):
    """Логирует операции пользователей"""
    user_operations_logger.info(
        f"User: {user_id}, Operation: {operation}, Details: {details}"
    )

def get_all_log_files():
    """Возвращает список всех лог-файлов"""
    log_files = []
    logs_dir = "logs"
    
    if os.path.exists(logs_dir):
        for filename in os.listdir(logs_dir):
            if filename.endswith('.log'):
                filepath = os.path.join(logs_dir, filename)
                file_size = os.path.getsize(filepath)
                file_time = os.path.getmtime(filepath)
                log_files.append({
                    'name': filename,
                    'path': filepath,
                    'size': file_size,
                    'modified': datetime.fromtimestamp(file_time)
                })
    
    # Сортируем по дате модификации (новые первые)
    log_files.sort(key=lambda x: x['modified'], reverse=True)
    return log_files
