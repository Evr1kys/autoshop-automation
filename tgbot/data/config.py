import os

from tgbot.data.texts.ru import Language as RU
from tgbot.data.texts.en import Language as EN
from tgbot.data.texts.ua import Language as UA

from tgbot.keyboards import users, admins


class BotConfig:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    ADMINS = [int(x) for x in os.getenv("BOT_ADMINS", "").split(",") if x.strip()]
    CHANNELS_FOR_SUBSCRIBE = [int(x) for x in os.getenv("REQUIRED_CHANNELS", "").split(",") if x.strip()]
    
    # При необходимости данные каналов можно добавить локально.
    CHANNELS_INFO = {}
    LOGS_CHANNEL = int(os.getenv("LOGS_CHANNEL", "0"))
    BOT_VERSION = "3.0"
    CURRENCIES = {
        "rub": {
            'txt': 'rub',
            "text": 'RUB',
            'sign': '₽'
        },
        "eur": {
            'txt': 'eur',
            "text": "EUR",
            'sign': "€"
        },
        "usd": {
            'txt': 'usd',
            'text': "USD",
            "sign": "$"
        }
    }
    LANGUAGES = [
        {
            "language": "ru",
            "name": "🇷🇺 Русский",
        },
        {
            "language": "en",
            "name": "🇺🇸 English",
        },
        {
            "language": "ua",
            "name": "🇺🇦 Український",
        },
    ]
    ######
    ######
    ######
    DATABASE_USERNAME = ""
    DATABASE_PASSWORD = ""
    DATABASE_NAME = ""


class BotTexts:
    class Ru:
        ADMIN_TEXTS = RU.AdminTexts()
        TEXTS = RU.Texts()
        BUTTONS = RU.Buttons()
    
    
    class En:
        ADMIN_TEXTS = EN.AdminTexts()
        TEXTS = EN.Texts()
        BUTTONS = EN.Buttons()
        
        
    class Ua:
        ADMIN_TEXTS = UA.AdminTexts()
        TEXTS = UA.Texts()
        BUTTONS = UA.Buttons()


class BotButtons:
    USERS_REPLY = users.ReplyButtons()
    USERS_INLINE = users.InlineButtons()
    ADMIN_INLINE = admins.InlineButtons()


class BotImages:
    # Пути к изображениям из папки img
    START_PHOTO = "img/start.png"  # Главное меню
    PROFILE_PHOTO = "img/Profile.png"  # Профиль пользователя
    TOPUP_BALANCE_PHOTO = "img/balance.png"  # Пополнение баланса
    SUPPORT_PHOTO = "img/support.png"  # Поддержка
    BUY_PHOTO = "img/buy.png"  # Покупки/магазин
    FAQ_PHOTO = "img/FAQ.png"  # Часто задаваемые вопросы
    DOCUMENTS_PHOTO = "img/documents.png"  # Документы/правила
    STEAM_PHOTO = "img/steam.png"  # Steam Points
    CONTEST_PHOTO = ""  # Конкурсы (файл отсутствует, оставляем пустым)


def main_db():
    from tgbot.utils.db import DataBase
    return DataBase()

DB = main_db()
