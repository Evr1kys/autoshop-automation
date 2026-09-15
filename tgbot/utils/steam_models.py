from sqlalchemy import Column, Integer, String, BigInteger, Float, Boolean, Text, Enum, DateTime
from sqlalchemy.sql import func
from tgbot.utils.models import Base
import enum


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
    points_requested = Column(Integer, nullable=False)
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
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    receipt = Column(String(50), unique=True, nullable=False)


class SteamApiConfig(Base):
    """Настройки Steam Points API"""
    __tablename__ = 'steam_api_config'
    
    id = Column(Integer, primary_key=True)
    api_key = Column(String(255), nullable=False)
    markup_percentage = Column(Float, default=15.0)  # Наценка в %
    min_points = Column(Integer, default=100)
    max_points = Column(Integer, default=10000)
    is_enabled = Column(Boolean, default=False)
    last_balance_check = Column(DateTime)
    current_balance = Column(Float, default=0)
    auto_disable_on_low_balance = Column(Boolean, default=True)
    low_balance_threshold = Column(Float, default=100.0)


class ProductReview(Base):
    """Отзывы о товарах"""
    __tablename__ = 'product_reviews'

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    purchase_receipt = Column(String(50), nullable=False)  # Связь с Purchase
    pos_id = Column(Integer)  # ID товара
    steam_order_id = Column(Integer)  # Связь с steam_orders
    rating = Column(Integer, nullable=False)  # 1-5 звезд
    review_text = Column(Text)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    is_approved = Column(Boolean, default=True)
    admin_reply = Column(Text)
    admin_reply_at = Column(DateTime)
    helpful_count = Column(Integer, default=0)


class ReviewReaction(Base):
    """Реакции на отзывы (полезно/не полезно)"""
    __tablename__ = 'review_reactions'

    reaction_id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    is_helpful = Column(Boolean, nullable=False)  # true = полезно, false = не полезно
    created_at = Column(DateTime, server_default=func.now())


class ReviewBonus(Base):
    """Бонусы за отзывы"""
    __tablename__ = 'review_bonuses'

    bonus_id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    bonus_amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)  # 'rub', 'usd', 'eur'
    reason = Column(String(255))  # "5-star review", "detailed review", etc.
    created_at = Column(DateTime, server_default=func.now())


class ReviewSettings(Base):
    """Настройки системы отзывов"""
    __tablename__ = 'review_settings'

    id = Column(Integer, primary_key=True)
    review_system_enabled = Column(Boolean, default=True)
    require_purchase_for_review = Column(Boolean, default=True)
    auto_approve_reviews = Column(Boolean, default=True)
    min_review_length = Column(Integer, default=10)
    max_review_length = Column(Integer, default=1000)
    
    # Бонусы за отзывы
    bonus_5_stars = Column(Float, default=10.0)
    bonus_4_stars = Column(Float, default=5.0)
    bonus_3_stars = Column(Float, default=2.0)
    bonus_2_stars = Column(Float, default=0.0)
    bonus_1_star = Column(Float, default=0.0)
    
    # Дополнительные бонусы
    bonus_detailed_review = Column(Float, default=5.0)  # За развернутый отзыв (>100 символов)
    bonus_first_review = Column(Float, default=15.0)    # За первый отзыв пользователя
    
    # Валюта бонусов
    bonus_currency = Column(String(3), default='rub')
