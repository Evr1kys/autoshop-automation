from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import BigInteger, String, Boolean, Integer, Enum, Float, Column, PrimaryKeyConstraint, Text
from sqlalchemy import select, insert

from tgbot.data.config import BotConfig

import enum
import time
import os

# Получаем путь к файлу базы данных
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'database.db')
db_url = f'sqlite+aiosqlite:///{db_path}'

# Инициализация асинхронного движка для SQLite
engine = create_async_engine(db_url)

# Создаем асинхронный фабричный метод для сессий
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Currencies(enum.Enum):
    rub = "rub"
    usd = "usd"
    eur = "eur"
    

class Languages(enum.Enum):
    ru = "ru"
    en = "en"
    ua = "ua"


class Keyboards(enum.Enum):
    Reply = "Reply"
    Inline = "Inline"


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    is_ban = Column(Boolean, default=False)
    user_name = Column(String)
    full_name = Column(String)
    balance_rub = Column(Float, default=0)
    balance_usd = Column(Float, default=0)
    balance_eur = Column(Float, default=0)
    language: Mapped[Languages] = Column(Enum(Languages), default=Languages.ru)
    total_refill = Column(Float, default=0)
    count_refills = Column(Integer, default=0)
    reg_date = Column(String)
    reg_date_unix = Column(BigInteger)
    ref_lvl = Column(Integer, default=1)
    ref_id = Column(BigInteger)
    ref_user_name = Column(String)
    ref_full_name = Column(String)
    ref_count = Column(Integer, default=0)
    ref_earn_rub = Column(Float, default=0)
    ref_earn_usd = Column(Float, default=0)
    ref_earn_eur = Column(Float, default=0)
    privacy_accepted = Column(Boolean, default=False)


class Settings(Base):
    __tablename__ = "settings"

    settings = Column(String, default="main", primary_key=True)
    is_work = Column(Boolean, default=True)
    is_refill = Column(Boolean, default=False)
    is_buy = Column(Boolean, default=False)
    is_ref = Column(Boolean, default=False)
    is_notify = Column(Boolean, default=True)
    is_sub = Column(Boolean, default=False)
    faq = Column(String)
    chat = Column(String)
    news = Column(String)
    support = Column(String)
    ref_percent_1 = Column(Float, default=0.0)
    ref_percent_2 = Column(Float, default=0.0)
    ref_percent_3 = Column(Float, default=0.0)
    ref_lvl_2 = Column(Integer, default=0)
    ref_lvl_3 = Column(Integer, default=0)
    profit_day = Column(Integer, default=0)
    profit_week = Column(Integer, default=0)
    currency: Mapped[Currencies] = Column(Enum(Currencies), default=Currencies.rub)
    keyboard: Mapped[Keyboards] = Column(Enum(Keyboards), default=Keyboards.Reply)
    multi_lang = Column(Boolean, default=True)
    default_lang: Mapped[Languages] = Column(Enum(Languages), default=Languages.ru)
    contests_is_on = Column(Boolean, default=True)
    custom_pay_method = Column(String, default="Custom Pay Method")
    custom_pay_method_text = Column(String, default="Transfer to card <code>123456789</code> to top up your balance.")
    custom_pay_method_min_amount = Column(Float, default=0.0)
    is_custom_pay_method_receipt_on = Column(Boolean, default=False)
    is_custom_pay_method_on = Column(Boolean, default=False)
    refill_commission_percent = Column(Float, default=6.0)  # Комиссия за пополнение в процентах


class Refill(Base):
    __tablename__ = "refills"

    user_id = Column(BigInteger)
    amount = Column(Float)
    receipt = Column(String, primary_key=True)
    way = Column(String)
    date = Column(String)
    date_unix = Column(BigInteger)
    pay_url = Column(String)
    second_amount = Column(Float)
    currency = Column(Enum(Currencies))
    is_finish = Column(Boolean, default=False)
    under_date = Column(BigInteger)
    external_id = Column(String)  # Для хранения настоящего transaction_id (Platega UUID)


class Rates(Base):
    __tablename__ = "rates"
    
    settings = Column(String, default="rates", primary_key=True)
    usd_rub = Column(Float, default=0.0)
    usd_eur = Column(Float, default=0.0)
    eur_rub = Column(Float, default=0.0)
    eur_usd = Column(Float, default=0.0)
    rub_usd = Column(Float, default=0.0)
    rub_eur = Column(Float, default=0.0)


class Purchase(Base):
    __tablename__ = "purchases"

    user_id = Column(BigInteger)
    receipt = Column(String, primary_key=True)
    count = Column(Integer)
    price_rub = Column(Float)
    price_usd = Column(Float)
    price_eur = Column(Float)
    pos_id = Column(Integer)
    item = Column(String)
    date = Column(String)
    unix = Column(BigInteger)
    file_id = Column(String)  # Добавленное поле для file_id


class AdButton(Base):
    __tablename__ = "ad_buttons"

    button_id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    text = Column(String)
    photo = Column(String)
    links = Column(String, default=None)


class Position(Base):
    __tablename__ = "positions"

    pos_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price_rub  = Column(Float)
    price_usd  = Column(Float)
    price_eur  = Column(Float)
    description = Column(String)
    photo = Column(String)
    cat_id = Column(Integer)
    sub_cat_id = Column(Integer)
    is_infinity = Column(Boolean)
    item_type = Column(String, default="text")


class SubCategory(Base):
    __tablename__ = "sub_categories"

    sub_cat_id = Column(Integer, primary_key=True, autoincrement=True)
    cat_id = Column(Integer)
    name = Column(String)


class Promocode(Base):
    __tablename__ = "promocodes"

    name = Column(String, primary_key=True)
    uses = Column(Integer)
    discount_rub = Column(Float)
    discount_usd = Column(Float)
    discount_eur = Column(Float)


class PaymentConfig(Base):
    __tablename__ = "payments_config"

    payment_id = Column(String, primary_key=True)
    text = Column(String)
    field = Column(String, primary_key=True)
    value = Column(String)


class Payment(Base):
    __tablename__ = "payments"

    settings = Column(String, default="payments", primary_key=True)
    crystalPay = Column(Boolean, default=False)
    cryptoBot = Column(Boolean, default=False)
    yoomoney = Column(Boolean, default=False)
    lolz = Column(Boolean, default=False)
    lava = Column(Boolean, default=False)
    payok = Column(Boolean, default=False)
    aaio = Column(Boolean, default=False)
    cryptomus = Column(Boolean, default=False)
    pal24 = Column(Boolean, default=False)
    platega = Column(Boolean, default=False)


class MailButton(Base):
    __tablename__ = "mail_buttons"

    button_id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    button_type = Column(String)
    

class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(String)
    pos_id = Column(Integer)
    cat_id = Column(Integer)
    date = Column(String)
    file_id = Column(String)


class ContestsSettings(Base):
    __tablename__ = "contests_settings"

    settings = Column(String, default="main", primary_key=True)
    winners_num = Column(Integer, default=1)
    prize = Column(Float, default=100)
    purchases_num = Column(Integer, default=0)
    refills_num = Column(Integer, default=0)
    channels_ids = Column(String)
    members_num = Column(Integer, default=10)
    end_time = Column(BigInteger)


class ContestMember(Base):
    __tablename__ = "contests_members"

    member_id = Column(Integer, primary_key=True, autoincrement=True)
    contest_id = Column(Integer)
    user_id = Column(BigInteger)


class Contest(Base):
    __tablename__ = "contests"

    contest_id = Column(Integer, autoincrement=True, primary_key=True)
    prize = Column(Float)
    currency: Mapped[Currencies] = Column(Enum(Currencies), default=Currencies.rub)
    members_num = Column(Integer)
    end_time = Column(BigInteger)
    winners_num = Column(Integer)
    channels_ids = Column(String)
    refills_num = Column(Integer, default=0)
    purchases_num = Column(Integer, default=0)


class Category(Base):
    __tablename__ = "categories"

    cat_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class ActivePromocode(Base):
    __tablename__ = "active_promocodes"

    promocode_name = Column(String, primary_key=True)
    user_id = Column(BigInteger)




class ProductNotification(Base):
    """Таблица для хранения уведомлений о товарах"""
    __tablename__ = "product_notifications"

    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    pos_id = Column(Integer)  # ID позиции товара
    title = Column(String)  # Заголовок уведомления
    message = Column(String)  # Текст уведомления
    file_path = Column(String)  # Путь к обновленному файлу (если есть)
    file_id = Column(String)  # Telegram file_id для быстрой отправки
    created_date = Column(String)  # Дата создания
    created_unix = Column(BigInteger)  # Unix timestamp
    is_sent = Column(Boolean, default=False)  # Отправлено ли уведомление
    sent_count = Column(Integer, default=0)  # Количество отправленных уведомлений


class NotificationQueue(Base):
    """Очередь уведомлений для отправки пользователям"""
    __tablename__ = "notification_queue"

    queue_id = Column(Integer, primary_key=True, autoincrement=True)
    notification_id = Column(Integer)  # ID уведомления
    user_id = Column(BigInteger)  # ID пользователя
    is_sent = Column(Boolean, default=False)  # Отправлено ли
    sent_date = Column(String)  # Дата отправки
    sent_unix = Column(BigInteger)  # Unix timestamp отправки
    error_message = Column(String)  # Сообщение об ошибке (если есть)


# Новые модели для системы отзывов и Steam Points
class ProductReview(Base):
    """Отзывы о товарах"""
    __tablename__ = 'product_reviews'

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    purchase_receipt = Column(String(50), nullable=False)  # Связь с Purchase
    pos_id = Column(Integer)  # ID товара
    steam_order_id = Column(Integer)  # Связь с steam_orders (если есть)
    rating = Column(Integer, nullable=False)  # 1-5 звезд
    review_text = Column(Text)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(String)  # Дата создания
    created_unix = Column(BigInteger)  # Unix timestamp
    is_approved = Column(Boolean, default=True)
    admin_reply = Column(Text)
    admin_reply_at = Column(String)
    helpful_count = Column(Integer, default=0)


class ReviewReaction(Base):
    """Реакции на отзывы (полезно/не полезно)"""
    __tablename__ = 'review_reactions'

    reaction_id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    is_helpful = Column(Boolean, nullable=False)  # true = полезно, false = не полезно
    created_at = Column(String)
    created_unix = Column(BigInteger)


class ReviewBonus(Base):
    """Бонусы за отзывы - УДАЛЕНО"""
    __tablename__ = 'review_bonuses'

    bonus_id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    bonus_amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)  # 'rub', 'usd', 'eur'
    reason = Column(String(255))  # "5-star review", "detailed review", etc.
    created_at = Column(String)
    created_unix = Column(BigInteger)


class ReviewSettings(Base):
    """Настройки системы отзывов"""
    __tablename__ = 'review_settings'

    id = Column(Integer, primary_key=True)
    review_system_enabled = Column(Boolean, default=True)
    require_purchase_for_review = Column(Boolean, default=True)
    auto_approve_reviews = Column(Boolean, default=True)
    min_review_length = Column(Integer, default=10)
    max_review_length = Column(Integer, default=1000)


# Steam Points система
class SteamOrderStatus(enum.Enum):
    pending = "pending"
    processing = "processing" 
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class SteamOrder(Base):
    """Заказы Steam очков"""
    __tablename__ = 'steam_orders'

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    steam_link = Column(String(255), nullable=False)
    steam_amount = Column(Integer, nullable=False)  # Переименовал из points_requested
    points_delivered = Column(Integer, default=0)
    price_rub = Column(Float, nullable=False)
    price_usd = Column(Float, nullable=False)
    price_eur = Column(Float, nullable=False)
    api_cost = Column(Float)  # Стоимость через API
    profit = Column(Float)    # Прибыль
    status = Column(Enum(SteamOrderStatus), default=SteamOrderStatus.pending)
    steam64 = Column(String(50))
    before_points = Column(String(20))
    after_points = Column(String(20))
    api_response = Column(Text)  # JSON ответ от API
    created_at = Column(String)
    created_unix = Column(BigInteger)
    completed_at = Column(String)
    receipt = Column(String(50), unique=True, nullable=False)


class SteamApiConfig(Base):
    """Настройки Steam Points API"""
    __tablename__ = 'steam_api_config'
    
    id = Column(Integer, primary_key=True)
    api_url = Column(String(255), default='https://api.buysteampoints.com')
    api_key = Column(String(255), default='')
    is_enabled = Column(Boolean, default=False)
    price_per_point = Column(Float, default=0.015)  # Цена за 1 очко в рублях (администраторская)
    api_price_per_point = Column(Float, default=0.005)  # Актуальная API цена за очко (для себестоимости)
    commission_percent = Column(Float, default=0.0)  # Комиссия в % (не используется, цена уже финальная)
    min_amount = Column(Integer, default=100)  # Минимум 100 очков
    max_amount = Column(Integer, default=100000)  # Максимум 100к очков
    last_balance_check = Column(String)
    last_price_check = Column(String)  # Время последней проверки API цены
    current_balance = Column(Float, default=0)  # Баланс в рублях от API
    auto_disable_on_low_balance = Column(Boolean, default=True)
    low_balance_threshold = Column(Float, default=50.0)  # Порог в рублях


payments_configs = [
    {
        "payment_id": "cryptomus",
        "text": "[Cryptomus] Merchant ID",
        "field": "merchant_id"
    },
    {
        "payment_id": "cryptomus",
        "text": "[Cryptomus] API Key",
        "field": "payment_api_key"
    },
    {
        "payment_id": "cryptoBot",
        "text": "[CryptoBot] Token",
        "field": "crypto_token"
    },
    {
        "payment_id": "yoomoney",
        "text": "[ЮMoney] Token",
        "field": "cryptoyoomoney_token_token"
    },
    {
        "payment_id": "yoomoney",
        "text": "[ЮMoney] Number",
        "field": "yoomoney_number"
    },
    {
        "payment_id": "aaio",
        "text": "[Aaio] API Key",
        "field": "aaio_api_key"
    },
    {
        "payment_id": "aaio",
        "text": "[Aaio] Shop ID",
        "field": "aaio_shop_id"
    },
    {
        "payment_id": "aaio",
        "text": "[Aaio] Secret key 1",
        "field": "aaio_secret_key_1"
    },
    {
        "payment_id": "payok",
        "text": "[PayOK] Secret",
        "field": "payok_secret"
    },
    {
        "payment_id": "payok",
        "text": "[PayOK] Api ID",
        "field": "payok_api_id"
    },
    {
        "payment_id": "payok",
        "text": "[PayOK] Api Key",
        "field": "payok_api_key"
    },
    {
        "payment_id": "payok",
        "text": "[PayOK] Shop ID",
        "field": "payok_shop_id"
    },
    {
        "payment_id": "lava",
        "text": "[Lava] Project ID",
        "field": "lava_project_id"
    },
    {
        "payment_id": "lava",
        "text": "[Lava] Secret Key",
        "field": "lava_secret_key"
    },
    {
        "payment_id": "lolz",
        "text": "[Lolzteam] Merchant ID",
        "field": "lolz_merchant_id"
    },
    {
        "payment_id": "lolz",
        "text": "[Lolzteam] Token",
        "field": "lolz_token"
    },
    {
        "payment_id": "crystalPay",
        "text": "[CrystalPay] Token",
        "field": "crystal_token"
    },
    {
        "payment_id": "crystalPay",
        "text": "[CrystalPay] Login",
        "field": "crystal_cassa"
    },
    {
        "payment_id": "pal24",
        "text": "[PAL24] API Token",
        "field": "pal24_token"
    },
    {
        "payment_id": "pal24",
        "text": "[PAL24] Shop ID",
        "field": "pal24_shop_id"
    },
    {
        "payment_id": "platega",
        "text": "[Platega] Merchant ID",
        "field": "platega_merchant_id"
    },
    {
        "payment_id": "platega",
        "text": "[Platega] API Secret",
        "field": "platega_api_secret"
    },
]


async def async_main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        if len((await conn.execute(select(Rates))).scalars().all()) == 0:
            await conn.execute(insert(Rates))
        if len((await conn.execute(select(Settings))).scalars().all()) == 0:
            await conn.execute(insert(Settings).values(
                profit_day=int(time.time()),
                profit_week=int(time.time())
            ))
        # Добавляем конфигурации платежей, если их нет
        try:
            existing_count = len((await conn.execute(select(PaymentConfig))).scalars().all())
            if existing_count < len(payments_configs):
                for paymentConfig in payments_configs:
                    try:
                        await conn.execute(insert(PaymentConfig).values(**paymentConfig))
                    except Exception:
                        # Запись уже существует, пропускаем
                        pass
        except Exception as e:
            print(f"Ошибка при инициализации конфигурации платежей: {e}")
        if len((await conn.execute(select(Payment))).scalars().all()) == 0:
            await conn.execute(insert(Payment).values())
        if len((await conn.execute(select(ContestsSettings))).scalars().all()) == 0:
            await conn.execute(insert(ContestsSettings).values(
                channels_ids="-",
                end_time=0,
            ))
                
        await conn.commit()