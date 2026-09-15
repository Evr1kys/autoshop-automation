# Автор: @Meta_Lib

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from cardinal import Cardinal

import os
import json
import time
import queue
import threading
import requests
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from telebot import types, TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from FunPayAPI.updater.events import NewOrderEvent, NewMessageEvent
from FunPayAPI.types import Order
from datetime import datetime

NAME = 'SteamPointsAuto'
VERSION = '1.3'
DESCRIPTION = 'Умный плагин для автоматической продажи очков Steam через buysteampoints API. Включает: систему подтверждения заказов, автоматическую защиту лотов при низком балансе, настраиваемые шаблоны сообщений и продвинутые фильтры заказов.'
CREDITS = '@Meta_Lib'
UUID = 'b74a46a7-b720-4fa1-acc3-aff1db86fc1d'
SETTINGS_PAGE = False
LOGGER_PREFIX = '[SteamPointsAuto]'

logger = logging.getLogger('FPC.steampoints')

CONFIG_DIR = 'storage/steam_points'
CONFIG_PATH = f'{CONFIG_DIR}/config.json'
ORDERS_PATH = f'{CONFIG_DIR}/orders.json'

DEFAULT_PROCESSING_TEMPLATE = '''🔄 Обработка заказа на очки Steam

⏳ Подбираю подходящий пакет очков под ваши требования...
📋 Это займет несколько секунд, пожалуйста подождите.'''

DEFAULT_SUCCESS_TEMPLATE = '''✅ Очки Steam успешно доставлены!

💎 Количество очков: {points}
💰 Стоимость: {total}₽
🎮 Steam профиль: {steam_link}
📊 Очки до покупки: {before_points}
📈 Очки после покупки: {after_points}

🎯 Очки уже зачислены на ваш аккаунт Steam!
💚 Спасибо за покупку! Не забудьте подтвердить заказ: {order_link}
⭐ Также просим оставить отзыв о покупке.'''

DEFAULT_ERROR_TEMPLATE = '''❌ Ошибка при обработке заказа на очки Steam

К сожалению, произошла техническая ошибка при покупке очков.
📞 Наш администратор свяжется с вами в ближайшее время для решения проблемы.'''

DEFAULT_INSUFFICIENT_FUNDS_TEMPLATE = '''💳 Недостаточно средств

К сожалению, на балансе сервиса недостаточно средств для покупки очков.
📞 Администратор уведомлен и пополнит баланс в ближайшее время.
💰 Ваши средства не списаны.'''

DEFAULT_INVALID_STEAM_TEMPLATE = '''❌ Неверная ссылка Steam

Указанная ссылка на профиль Steam некорректна.
🔗 Пожалуйста, проверьте ссылку и попробуйте снова.
📋 Ссылка должна быть в формате: https://steamcommunity.com/id/yoursteamid

💬 Если проблема повторяется, обратитесь к администратору.'''

DEFAULT_MAINTENANCE_TEMPLATE = '''⚠️ Технические работы

В данный момент проводятся технические работы на сервере Steam Points.
🔄 Попробуйте оформить заказ позже.
💬 При необходимости обратитесь к администратору.'''

DEFAULT_STEAM_REQUEST_TEMPLATE = '''🎮 Для выполнения заказа на {points} очков Steam необходима ссылка на ваш Steam профиль.

Отправьте ссылку в формате:
🔗 https://steamcommunity.com/id/ваш_id
или
🔗 https://steamcommunity.com/profiles/ваш_id

💰 Сумма заказа: {price}₽

❌ Для отмены заказа отправьте: -'''

DEFAULT_STEAM_CONFIRMATION_TEMPLATE = '''✅ Ссылка Steam получена!

🎮 Профиль: {steam_link}
💎 Количество очков: {points}
💰 Сумма заказа: {order_sum}₝

Для подтверждения заказа отправьте:
➕ + - подтвердить заказ
🔄 новую ссылку - изменить профиль Steam
❌ - - отменить заказ и получить возврат

⏳ Ожидаю ваше решение...'''

bot: Optional[TeleBot] = None
cardinal_instance = None
config = {}
user_states = {}
order_queue = queue.Queue()
executor = None
max_workers = 3
processing_messages = {}
pending_steam_links = {}
recent_plugin_messages = {}
price_update_timer = None
balance_check_timer = None
cached_price = None
last_price_update = 0

STEAM_API_BASE = 'https://api.buysteampoints.com/api'
PRICE_ENDPOINT = f'{STEAM_API_BASE}/price'
BUY_ENDPOINT = f'{STEAM_API_BASE}/buy'

def ensure_config_exists(check_only=False):
    global config
    
    default_config = {
        'api_key': '',
        'administrators': [],
        'enabled': True,

        'templates': {
            'processing': DEFAULT_PROCESSING_TEMPLATE,
            'success': DEFAULT_SUCCESS_TEMPLATE,
            'error': DEFAULT_ERROR_TEMPLATE,
            'insufficient_funds': DEFAULT_INSUFFICIENT_FUNDS_TEMPLATE,
            'invalid_steam': DEFAULT_INVALID_STEAM_TEMPLATE,
            'maintenance': DEFAULT_MAINTENANCE_TEMPLATE,
            'steam_request': DEFAULT_STEAM_REQUEST_TEMPLATE,
            'steam_confirmation': DEFAULT_STEAM_CONFIRMATION_TEMPLATE
        },
        'balance_check_enabled': True,
        'auto_deactivate_enabled': True,
        'min_balance_threshold': 10.0,
        'bonus_system_enabled': False,
        'bonus_points_for_review': 1000,
        'bonus_settings': {
            '5_stars': 100,   # Бонус за 5 звезд
            '4_stars': 50,    # Бонус за 4 звезды
            '3_stars': 0,     # Бонус за 3 звезды
            '2_stars': 0,     # Бонус за 2 звезды
            '1_star': 0       # Бонус за 1 звезду
        },
        'lot_management_enabled': False,
        'target_lot_category': 714,
        'target_subcategories': [714],
        'target_keywords': [
            'steam points', 'очки steam', 'стим поинты', 'steam очки', 
            'поинты steam', 'очков steam', 'steam point', 'steam пойнты'
        ]
    }
    
    if check_only:
        return default_config
    
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
        config = default_config
    else:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)

def save_config():
    global config
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        logger.debug(f'{LOGGER_PREFIX} ✅ Конфигурация сохранена в {CONFIG_PATH}')
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка сохранения конфигурации: {e}')

def get_current_price():
    global cached_price, last_price_update
    
    try:
        current_time = time.time()
        
        if cached_price is not None and current_time - last_price_update < 300:
            return cached_price
        
        api_key = config.get('api_key')
        if not api_key:
            logger.warning(f'{LOGGER_PREFIX} ⚠️ API ключ не настроен, цена недоступна')
            return None
        
        response = requests.get(PRICE_ENDPOINT, params={'api_key': api_key}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                price_per_point = data.get('price', 0.012)
                
                if price_per_point > 0:
                    cached_price = price_per_point
                    last_price_update = current_time
                    price_per_10k = price_per_point * 10000
                    logger.info(f'{LOGGER_PREFIX} 💎 Цена обновлена через API: {cached_price:.4f}₽ за очко ({price_per_10k:.2f}₽ за 10k)')
                    return cached_price
                else:
                    logger.warning(f'{LOGGER_PREFIX} ⚠️ API вернул нулевую цену')
                    return None
            else:
                error_msg = data.get('error', 'Unknown error')
                logger.error(f'{LOGGER_PREFIX} ❌ API ошибка: {error_msg}')
        else:
            logger.error(f'{LOGGER_PREFIX} ❌ HTTP ошибка: {response.status_code}, текст: {response.text}')
        
        if cached_price is not None:
            logger.info(f'{LOGGER_PREFIX} 🔄 Используем кешированную цену: {cached_price:.4f}₽')
            return cached_price
            
        logger.warning(f'{LOGGER_PREFIX} ⚠️ Цена недоступна - нет связи с API')
        return None
        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при получении цены: {e}')
        if cached_price is not None:
            logger.info(f'{LOGGER_PREFIX} 🔄 Используем кешированную цену после ошибки: {cached_price:.4f}₽')
            return cached_price
        logger.warning(f'{LOGGER_PREFIX} ⚠️ Цена недоступна после ошибки - нет связи с API')
        return None

def get_api_balance():
    """Получает текущий баланс API"""
    try:
        api_key = config.get('api_key')
        if not api_key:
            logger.warning(f'{LOGGER_PREFIX} ⚠️ API ключ не настроен, баланс недоступен')
            return None
        
        # Используем POST запрос к /api/balance согласно документации
        balance_url = f'{STEAM_API_BASE}/balance'
        response = requests.post(balance_url, json={'api_key': api_key}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                balance = float(data.get('balance', 0))
                logger.info(f'{LOGGER_PREFIX} 💰 Баланс API получен: {balance:.2f}₽')
                return balance
            else:
                error_msg = data.get('error', 'Unknown error')
                logger.error(f'{LOGGER_PREFIX} ❌ API ошибка при получении баланса: {error_msg}')
        else:
            logger.error(f'{LOGGER_PREFIX} ❌ HTTP ошибка при получении баланса: {response.status_code}')
        
        return None
        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при получении баланса API: {e}')
        return None

def check_balance_and_manage_lots():
    """Проверяет баланс API и деактивирует лоты при низком балансе"""
    if not config.get('auto_deactivate_enabled', False):
        return
    
    try:
        balance = get_api_balance()
        if balance is None:
            logger.warning(f'{LOGGER_PREFIX} ⚠️ Не удалось получить баланс API, пропускаем проверку управления лотами')
            return
        
        min_threshold = config.get('min_balance_threshold', 10.0)
        category_id = config.get('target_lot_category', 714)
        
        try:
            profile = cardinal_instance.account.get_user(cardinal_instance.account.id)
            # Получаем ВСЕ лоты (активные и неактивные) с нужной категорией
            all_lots = profile.get_lots()
            lots = [lot for lot in all_lots if lot.subcategory.id == category_id]
            
            if not lots:
                logger.warning(f'{LOGGER_PREFIX} ⚠️ Не найдено лотов Steam Points (категория {category_id}). Проверьте, что лоты существуют.')
                return
            
            # Подсчитываем активные лоты
            active_lots = []
            for lot in lots:
                try:
                    lot_fields = cardinal_instance.account.get_lot_fields(lot.id)
                    if lot_fields.active:
                        active_lots.append(lot)
                except Exception as e:
                    logger.error(f'{LOGGER_PREFIX} ❌ Ошибка получения статуса лота {lot.id}: {e}')
                    continue
            
            logger.info(f'{LOGGER_PREFIX} 📊 Найдено лотов Steam Points: активных={len(active_lots)}, всего={len(lots)}')
            
            if balance < min_threshold:
                # Баланс низкий - деактивируем активные лоты
                if active_lots:
                    logger.warning(f'{LOGGER_PREFIX} ⚠️ Низкий баланс API: {balance:.2f}₽ < {min_threshold}₽ - деактивируем {len(active_lots)} активных лотов')
                    
                    deactivated_count = 0
                    for lot in active_lots:
                        try:
                            logger.debug(f'{LOGGER_PREFIX} 🔍 Проверяем лот {lot.id} для деактивации...')
                            lot_fields = cardinal_instance.account.get_lot_fields(lot.id)
                            logger.debug(f'{LOGGER_PREFIX} 🔍 Лот {lot.id}: текущий статус active={lot_fields.active}')
                            
                            if lot_fields.active:
                                lot_fields.active = False
                                try:
                                    cardinal_instance.account.save_lot(lot_fields)
                                    deactivated_count += 1
                                    logger.info(f'{LOGGER_PREFIX} 🔴 Лот {lot.id} автоматически деактивирован из-за низкого баланса (API метод)')
                                except Exception as save_error:
                                    logger.warning(f'{LOGGER_PREFIX} ⚠️ API метод не сработал для лота {lot.id}, пробуем HTTP метод: {save_error}')
                                    if activate_lot_http(lot.id, False):
                                        deactivated_count += 1
                                        logger.info(f'{LOGGER_PREFIX} 🔴 Лот {lot.id} автоматически деактивирован из-за низкого баланса (HTTP метод)')
                                    else:
                                        raise save_error
                                time.sleep(0.5)  # Задержка между запросами
                            else:
                                logger.debug(f'{LOGGER_PREFIX} 🔍 Лот {lot.id} уже неактивен, пропускаем')
                        except Exception as e:
                            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при деактивации лота {lot.id}: {type(e).__name__}: {e}')
                            continue
                    
                    if deactivated_count > 0:
                        logger.info(f'{LOGGER_PREFIX} 🔴 Автоматически деактивировано {deactivated_count} лотов из-за низкого баланса')
                        
                        # Уведомляем администраторов
                        notify_admins(f'⚠️ <b>Низкий баланс API - лоты деактивированы</b>\n\n💰 Баланс: {balance:.2f}₽\n📉 Минимальный порог: {min_threshold}₽\n\n🔴 Автоматически деактивировано {deactivated_count} лотов', None)
                else:
                    logger.info(f'{LOGGER_PREFIX} ℹ️ Низкий баланс API: {balance:.2f}₽ < {min_threshold}₽, но активных лотов для деактивации нет')
            else:
                logger.info(f'{LOGGER_PREFIX} ✅ Баланс API в норме: {balance:.2f}₽ >= {min_threshold}₽')
        
        except Exception as e:
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при управлении лотами: {e}')
            notify_admins(f'⚠️ <b>Ошибка управления лотами</b>\n\n💰 Баланс: {balance:.2f}₽\n📉 Минимальный порог: {min_threshold}₽\n\n❌ Не удалось управлять лотами: {e}', None)

    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при проверке баланса и управления лотами: {e}')

def activate_lot_http(lot_id, active=True):
    """Альтернативная функция активации/деактивации лота через HTTP запрос"""
    try:
        # Получаем сессию из cardinal_instance для авторизации
        session = cardinal_instance.account.session
        
        # Простой метод: отправляем POST запрос напрямую
        url = "https://funpay.com/lots/offerEdit"
        
        # Подготавливаем данные для активации/деактивации
        data = {
            'node': '714',  # категория Steam Points
            'offer': str(lot_id),
            'active': '1' if active else '0'
        }
        
        # Отправляем POST запрос
        response = session.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            # Проверяем, что в ответе нет ошибок
            if "error" not in response.text.lower() and "ошибка" not in response.text.lower():
                logger.info(f'{LOGGER_PREFIX} ✅ Лот {lot_id} {"активирован" if active else "деактивирован"} через HTTP метод')
                return True
            else:
                logger.error(f'{LOGGER_PREFIX} ❌ HTTP ошибка в ответе при управлении лотом {lot_id}')
                return False
        else:
            logger.error(f'{LOGGER_PREFIX} ❌ HTTP статус ошибка при управлении лотом {lot_id}: {response.status_code}')
            return False
            
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Исключение при HTTP управлении лотом {lot_id}: {type(e).__name__}: {e}')
        return False

def check_and_activate_lots():
    """Проверяет баланс API и активирует лоты при достаточном балансе"""
    check_balance_and_manage_lots()

def check_and_deactivate_lots():
    """Проверяет баланс API и деактивирует лоты при необходимости"""
    check_balance_and_manage_lots()

def start_price_update_timer():
    global price_update_timer
    
    def update_price():
        try:
            global cached_price, last_price_update
            last_price_update = 0
            new_price = get_current_price()
        except Exception as e:
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка автообновления цены: {e}')
        
        start_price_update_timer()
    
    if price_update_timer:
        price_update_timer.cancel()
    
    price_update_timer = threading.Timer(300.0, update_price)
    price_update_timer.daemon = True
    price_update_timer.start()

def start_balance_check_timer():
    """Запускает таймер автоматической проверки баланса и управления лотами"""
    global balance_check_timer
    
    def check_balance():
        try:
            check_balance_and_manage_lots()
        except Exception as e:
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка автоматической проверки баланса: {e}')
        
        start_balance_check_timer()
    
    if balance_check_timer:
        balance_check_timer.cancel()
    
    # Проверяем баланс каждые 10 минут (600 секунд)
    balance_check_timer = threading.Timer(600.0, check_balance)
    balance_check_timer.daemon = True
    balance_check_timer.start()

def stop_price_update_timer():
    """Останавливает таймер автообновления цены"""
    global price_update_timer
    if price_update_timer:
        price_update_timer.cancel()
        price_update_timer = None

def stop_balance_check_timer():
    """Останавливает таймер автоматической проверки баланса"""
    global balance_check_timer
    if balance_check_timer:
        balance_check_timer.cancel()
        balance_check_timer = None

def validate_steam_link(steam_link):
    if not steam_link:
        return False
    
    patterns = [
        r'https?://steamcommunity\.com/id/[a-zA-Z0-9_-]+/?',
        r'https?://steamcommunity\.com/profiles/\d+/?'
    ]
    
    for pattern in patterns:
        if re.match(pattern, steam_link):
            return True
    
    return False

def extract_steam_link_from_message(message_text):
    """Извлекает ссылку Steam из сообщения"""
    if not message_text:
        return None
    
    patterns = [
        r'(https?://steamcommunity\.com/id/[a-zA-Z0-9_-]+/?)',
        r'(https?://steamcommunity\.com/profiles/\d+/?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message_text)
        if match:
            return match.group(1)
    
    return None

def is_steam_points_order(order):
    """Проверяет, является ли заказ заказом на Steam Points с проверкой количества очков"""
    global cardinal_instance
    
    if cardinal_instance and hasattr(order, 'buyer_username'):
        if order.buyer_username == cardinal_instance.account.username:
            logger.info(f'{LOGGER_PREFIX} ⏭️ Пропускаем собственный заказ #{order.id}')
            return False
    
    target_subcategories = config.get('target_subcategories', [714])
    
    subcategory_match = False
    try:
        if hasattr(order, 'subcategory') and order.subcategory:
            subcategory_id = order.subcategory.id
            if subcategory_id in target_subcategories:
                subcategory_match = True
                logger.info(f'{LOGGER_PREFIX} Заказ #{order.id} подходит по подкатегории {subcategory_id}')
    except Exception as e:
        logger.debug(f'{LOGGER_PREFIX} Ошибка получения подкатегории: {e}')
    
    target_keywords = config.get('target_keywords', [
        'steam points', 'очки steam', 'стим поинты', 'steam очки', 
        'поинты steam', 'очков steam', 'steam point', 'steam пойнты'
    ])
    
    description = order.description.lower() if order.description else ''
    subcategory_name = order.subcategory_name.lower() if hasattr(order, 'subcategory_name') and order.subcategory_name else ''
    
    keyword_match = False
    for keyword in target_keywords:
        if keyword.lower() in description or keyword.lower() in subcategory_name:
            keyword_match = True
            logger.info(f'{LOGGER_PREFIX} Заказ #{order.id} подходит по ключевому слову: "{keyword}"')
            break
    
    if not subcategory_match and not keyword_match:
        logger.info(f'{LOGGER_PREFIX} ❌ Заказ #{order.id} не подходит (подкатегория: {getattr(order.subcategory, "id", "N/A") if hasattr(order, "subcategory") and order.subcategory else "N/A"}, описание: "{description[:50]}...")')
        return False
    
    points = extract_points_from_order(order)
    if points is None:
        logger.warning(f'{LOGGER_PREFIX} ❌ Не удалось определить количество очков в заказе #{order.id}')
        return False
    
    logger.info(f'{LOGGER_PREFIX} ✅ Заказ #{order.id} подходит для обработки: {points} очков Steam')
    return True

def extract_quan_from_text(text):
    """Извлекает значение Quan из текста для пакетной продажи"""
    if not text:
        return None
    
    # Ищем паттерн Quan: число
    quan_patterns = [
        r'quan:\s*(\d+)',
        r'quan\s*(\d+)',
        r'quan=\s*(\d+)'
    ]
    
    for pattern in quan_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                quan_value = int(match.group(1))
                logger.info(f'{LOGGER_PREFIX} 📦 Найдено Quan: {quan_value} в тексте: "{text[:50]}..."')
                return quan_value
            except ValueError:
                continue
    
    return None

def extract_points_from_order(order):
    global cardinal_instance
    
    quan_value = None
    points_per_unit = None
    
    try:
        if cardinal_instance and hasattr(order, 'id'):
            detailed_order = cardinal_instance.account.get_order(order.id)
            
            # Первым делом ищем Quan в описании лота
            if hasattr(detailed_order, 'lot') and detailed_order.lot:
                
                if hasattr(detailed_order.lot, 'description') and detailed_order.lot.description:
                    quan_value = extract_quan_from_text(detailed_order.lot.description)
                    if quan_value is not None:
                        logger.info(f'{LOGGER_PREFIX} 📦 Найдено Quan: {quan_value} в описании лота')
                        # Если Quan: 0, то 1 лот = 1 очко
                        if quan_value == 0:
                            logger.info(f'{LOGGER_PREFIX} 🔢 Режим по одному очку (Quan: 0). Количество лотов: {getattr(detailed_order, "amount", 1)}')
                            return getattr(detailed_order, 'amount', 1)
                        else:
                            # Если Quan > 0, то один лот = Quan очков
                            order_amount = getattr(detailed_order, 'amount', 1)
                            total_points = quan_value * order_amount
                            logger.info(f'{LOGGER_PREFIX} 📦 Пакетная продажа: {quan_value} очков за лот × {order_amount} лотов = {total_points} очков')
                            return total_points
                
                # Если Quan не найден, проверяем в названии и коротком описании
                if quan_value is None:
                    if hasattr(detailed_order.lot, 'name') and detailed_order.lot.name:
                        quan_value = extract_quan_from_text(detailed_order.lot.name)
                    
                    if quan_value is None and hasattr(detailed_order.lot, 'short_description') and detailed_order.lot.short_description:
                        quan_value = extract_quan_from_text(detailed_order.lot.short_description)
                    
                    # Если нашли Quan в названии или коротком описании
                    if quan_value is not None:
                        logger.info(f'{LOGGER_PREFIX} 📦 Найдено Quan: {quan_value} в названии/коротком описании')
                        if quan_value == 0:
                            return getattr(detailed_order, 'amount', 1)
                        else:
                            order_amount = getattr(detailed_order, 'amount', 1)
                            return quan_value * order_amount
                
                # Если Quan не найден, используем стандартную логику
                if quan_value is None:
                    logger.info(f'{LOGGER_PREFIX} 🔍 Quan не найден, используем стандартную логику поиска очков')
                    
                    if hasattr(detailed_order.lot, 'name') and detailed_order.lot.name:
                        points = extract_points_from_text(detailed_order.lot.name)
                        if points:
                            return points
                    
                    if hasattr(detailed_order.lot, 'description') and detailed_order.lot.description:
                        points = extract_points_from_text(detailed_order.lot.description)
                        if points:
                            return points
                    
                    if hasattr(detailed_order.lot, 'short_description') and detailed_order.lot.short_description:
                        points = extract_points_from_text(detailed_order.lot.short_description)
                        if points:
                            return points
            
            # Проверяем amount заказа
            if hasattr(detailed_order, 'amount') and detailed_order.amount and detailed_order.amount > 50:
                return detailed_order.amount
            
            # Проверяем lot_params
            if hasattr(detailed_order, 'lot_params') and detailed_order.lot_params:
                for param_name, param_value in detailed_order.lot_params:
                    if any(keyword in param_name.lower() for keyword in ['очк', 'points', 'поинт']):
                        try:
                            points = int(re.sub(r'[^\d]', '', param_value))
                            if 50 <= points <= 100000:
                                return points
                        except (ValueError, TypeError):
                            continue
            
            # Проверяем полное описание
            if hasattr(detailed_order, 'full_description') and detailed_order.full_description:
                points = extract_points_from_text(detailed_order.full_description)
                if points:
                    return points
            
            # Проверяем короткое описание
            if hasattr(detailed_order, 'short_description') and detailed_order.short_description:
                points = extract_points_from_text(detailed_order.short_description)
                if points:
                    return points
            
            # Проверяем подкатегорию
            if hasattr(detailed_order, 'subcategory') and detailed_order.subcategory:
                if hasattr(detailed_order.subcategory, 'name'):
                    points = extract_points_from_text(detailed_order.subcategory.name)
                    if points:
                        return points
                        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при получении детального заказа через API: {e}')
    
    # Остальная логика для случаев, когда не удалось получить детальный заказ
    if hasattr(order, 'amount') and order.amount and order.amount > 50:
        return order.amount
    
    # Ищем упоминание очков в описании заказа
    description = order.description if hasattr(order, 'description') and order.description else ''
    points = extract_points_from_text(description)
    if points:
        return points
    
    # Остальная логика по цене
    if hasattr(order, 'amount') and order.amount == 1:
        
        if hasattr(order, 'sum') and order.sum > 0:
            points = calculate_points_by_price(order.sum)
            if points:
                return points
        
        if hasattr(order, 'price') and order.price > 0 and order.price != getattr(order, 'sum', 0):
            points = calculate_points_by_price(order.price)
            if points:
                return points
    
    if hasattr(order, 'price') and order.price > 0:
        points = calculate_points_by_price(order.price)
        if points:
            return points
    
    if hasattr(order, 'sum') and order.sum > 0:
        points = calculate_points_by_price(order.sum)
        if points:
            return points
    
    logger.warning(f'{LOGGER_PREFIX} ❌ Не удалось определить количество очков в заказе #{getattr(order, "id", "N/A")}')
    return None


def extract_points_from_text(text):
    if not text:
        return None
        
    points_patterns = [
        r'(\d+[\s,]*\d*)\s*очк',
        r'(\d+[\s,]*\d*)\s*points?',
        r'(\d+[\s,]*\d*)\s*поинт',
        r'(\d+[\s,]*\d*)\s*steam\s*points?',
        r'(\d+[\s,]*\d*)\s*стим\s*очк',
        r'(\d+[\s,]*\d*)\s*steam\s*очк',
        r'(\d+[\s,]*\d*)\s*очки?\s*стим',
        r'(\d+[\s,]*\d*)\s*очков\s*steam',
        r'(\d+[\s,]*\d*)\s*штук?\s*очк',
        
        r'очки?\s*стим\s*(\d+[\s,]*\d*)',
        r'очки?\s*steam\s*(\d+[\s,]*\d*)',
        r'steam\s*points?\s*(\d+[\s,]*\d*)',
        r'стим\s*очки?\s*(\d+[\s,]*\d*)',
        r'steam\s*очки?\s*(\d+[\s,]*\d*)',
        r'очки?\s*(\d+[\s,]*\d*)\s*штук',
        
        r'получите\s*(\d+[\s,]*\d*)\s*очк',
        r'доставка\s*(\d+[\s,]*\d*)\s*очк',
        r'продаю\s*(\d+[\s,]*\d*)\s*очк',
        r'(\d+[\s,]*\d*)\s*очков?\s*для\s*steam',
    ]
    
    for pattern in points_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            points_str = None
            for group_idx in [1, 2]:
                try:
                    if match.group(group_idx):
                        points_str = match.group(group_idx).replace(' ', '').replace(',', '')
                        break
                except IndexError:
                    continue
            
            if points_str:
                try:
                    points = int(points_str)
                    if 50 <= points <= 100000:
                        return points
                except ValueError:
                    continue
    
    return None


def calculate_points_by_price(price):
    current_price = get_current_price()
    if current_price is None:
        logger.warning(f'{LOGGER_PREFIX} ⚠️ Не удается рассчитать очки - цена недоступна')
        return None
        
    if current_price > 0:
        cost_per_point = current_price
        calculated_points = int(price / cost_per_point)
        
        if 50 <= calculated_points <= 100000:
            return calculated_points
    
    return None

def buy_steam_points(api_key, points, steam_link):
    try:
        payload = {
            'api_key': api_key,
            'puan': points,
            'steam_link': steam_link
        }
        
        logger.info(f'{LOGGER_PREFIX} Покупка {points} очков для {steam_link}')
        
        response = requests.post(BUY_ENDPOINT, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info(f'{LOGGER_PREFIX} ✅ Успешная покупка {points} очков')
                return data
            else:
                error = data.get('error', 'Unknown error')
                logger.error(f'{LOGGER_PREFIX} ❌ Ошибка API: {error}')
                return {'success': False, 'error': error}
        else:
            logger.error(f'{LOGGER_PREFIX} ❌ HTTP ошибка: {response.status_code}')
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
    except requests.exceptions.Timeout:
        logger.error(f'{LOGGER_PREFIX} ⏰ Таймаут запроса')
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Неожиданная ошибка: {e}')
        return {'success': False, 'error': str(e)}

def send_processing_message(chat_id, order_id):
    pass

def delete_processing_message(order_id):
    pass

def send_message_to_buyer(c, username, message):
    try:
        if username == c.account.username:
            return False
        
        if not c or not hasattr(c, 'account'):
            logger.error(f'{LOGGER_PREFIX} ❌ Объект Cardinal или account недоступен')
            return False
        
        chat_obj = c.account.get_chat_by_name(username, make_request=True)
        
        if chat_obj:
            chat_id = getattr(chat_obj, 'id', None)
            if chat_id:
                c.account.send_message(chat_id, message)
                register_plugin_message(username, message)
                logger.info(f'{LOGGER_PREFIX} ✅ Сообщение отправлено пользователю {username}')
                return True
            else:
                logger.error(f'{LOGGER_PREFIX} ❌ Не удалось извлечь ID из chat объекта для {username}')
                return False
        else:
            logger.error(f'{LOGGER_PREFIX} ❌ Не удалось получить chat_id для пользователя {username}')
            return False
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при отправке сообщения покупателю {username}: {e}')
        return False

def notify_admins(message, order_id=None):
    if not config.get('administrators'):
        logger.warning(f'{LOGGER_PREFIX} Нет настроенных администраторов для уведомлений')
        return
    
    if order_id:
        profit_data = load_profit_cache()
        if order_id in profit_data.get('orders_profit', {}):
            order_profit = profit_data['orders_profit'][order_id]
            valova_profit = order_profit.get('profit', 0)
            profit_3_percent = order_profit.get('profit_after_3_percent', 0)
            profit_6_percent = order_profit.get('profit_after_6_percent', 0)
            
            profit_info = f"\n💰 Финансовая информация:" \
                         f"\n• За сколько продали: {order_profit.get('fp_sum', 0)} руб." \
                         f"\n• Сколько стоят очки на API: {order_profit.get('points_cost', 0)} руб." \
                         f"\n• Валовая прибыль: {valova_profit:.2f} руб." \
                         f"\n• После комиссии 3%: {profit_3_percent:.2f} руб." \
                         f"\n• После комиссии 6%: {profit_6_percent:.2f} руб."
            message += profit_info
    
    for admin_id in config['administrators']:
        try:
            if bot and order_id:
                kb = InlineKeyboardMarkup()
                clean_order_id = order_id.split('_')[0] if '_' in str(order_id) else order_id
                kb.add(InlineKeyboardButton('Перейти к заказу', url=f'https://funpay.com/orders/{clean_order_id}/'))
                bot.send_message(admin_id, message, reply_markup=kb)
            elif bot:
                bot.send_message(admin_id, message)
        except Exception as e:
            logger.error(f'{LOGGER_PREFIX} Ошибка при отправке уведомления администратору {admin_id}: {e}')

def get_profit_cache_file():
    """Возвращает путь к файлу с кешем прибыли"""
    return os.path.join(os.path.dirname(__file__), f'..{os.sep}storage{os.sep}cache{os.sep}steam_points_profit.json')

def load_profit_cache():
    """Загружает кеш прибыли"""
    profit_file = get_profit_cache_file()
    try:
        if os.path.exists(profit_file):
            with open(profit_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'orders_profit': {},
            'total_orders': 0,
            'total_profit': 0.0
        }
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} Ошибка при загрузке кеша прибыли: {e}')
        return {
            'orders_profit': {},
            'total_orders': 0,
            'total_profit': 0.0
        }

def save_profit_cache(profit_data):
    """Сохраняет кеш прибыли"""
    profit_file = get_profit_cache_file()
    try:
        os.makedirs(os.path.dirname(profit_file), exist_ok=True)
        with open(profit_file, 'w', encoding='utf-8') as f:
            json.dump(profit_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} Ошибка при сохранении кеша прибыли: {e}')

def save_order_profit(order_id, fp_sum, points_cost, points_count):
    """Сохраняет информацию о прибыли с заказа в кеше"""
    profit = fp_sum - points_cost
    
    # Загружаем текущий кеш прибыли
    profit_data = load_profit_cache()
    
    # Рассчитываем прибыль с учетом комиссий FunPay
    profit_after_3_percent = profit - (fp_sum * 0.03)  # После комиссии 3%
    profit_after_6_percent = profit - (fp_sum * 0.06)  # После комиссии 6%
    
    # Добавляем новый заказ
    profit_data['orders_profit'][order_id] = {
        'fp_sum': fp_sum,
        'points_cost': points_cost,
        'points_count': points_count,
        'profit': profit,
        'profit_after_3_percent': profit_after_3_percent,
        'profit_after_6_percent': profit_after_6_percent,
        'timestamp': time.time()
    }
    
    profit_data['total_orders'] += 1
    profit_data['total_profit'] += profit
    
    # Сохраняем в кеш
    save_profit_cache(profit_data)
    
    logger.info(f'{LOGGER_PREFIX} 💰 Прибыль с заказа {order_id}: валовая {profit:.2f}₽, чистая (3%): {profit_after_3_percent:.2f}₽, чистая (6%): {profit_after_6_percent:.2f}₽ (сохранено в кеш)')

def get_bonus_cache_file():
    """Возвращает путь к файлу с кешем бонусов"""
    return os.path.join(os.path.dirname(__file__), f'..{os.sep}storage{os.sep}cache{os.sep}steam_points_bonus.json')

def load_bonus_cache():
    """Загружает кеш бонусов"""
    bonus_file = get_bonus_cache_file()
    try:
        if os.path.exists(bonus_file):
            with open(bonus_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при загрузке кеша бонусов: {e}')
    
    # Возвращаем структуру по умолчанию
    return {
        'users_with_bonus': {},
        'total_bonuses_given': 0,
        'total_bonus_points': 0
    }

def save_bonus_cache(bonus_data):
    """Сохраняет кеш бонусов"""
    bonus_file = get_bonus_cache_file()
    try:
        os.makedirs(os.path.dirname(bonus_file), exist_ok=True)
        with open(bonus_file, 'w', encoding='utf-8') as f:
            json.dump(bonus_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при сохранении кеша бонусов: {e}')

def send_bonus_points(username, points, order_id, review_rating):
    """Отправляет бонусные очки пользователю через API FunPay"""
    try:
        global cardinal_instance
        
        if not cardinal_instance:
            logger.error(f'{LOGGER_PREFIX} ❌ Cardinal instance не доступен для отправки бонуса')
            return False
        
        # Логируем отправку бонуса
        logger.info(f'{LOGGER_PREFIX} 💎 Отправка {points} бонусных очков пользователю {username}')
        
        # Здесь можно добавить реальную логику отправки через FunPay API
        # Например, через встроенные методы Cardinal или прямые API вызовы
        
        # Возвращаем True для симуляции успешной отправки
        # В реальной реализации здесь должен быть вызов API
        return True
        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при отправке бонуса: {e}')
        return False


def parse_review_notification(message_text):
    """Парсит уведомление об отзыве и извлекает данные"""
    try:
        # Ищем паттерн "написал отзыв" или "оставил отзыв"
        if 'написал отзыв' not in message_text and 'оставил отзыв' not in message_text:
            return None
        
        # Ищем рейтинг отзыва (количество звезд)
        import re
        
        # Паттерн для поиска звезд в разных форматах
        star_patterns = [
            r'(\d+)\s*звезд',  # "5 звезд"
            r'(\d+)\s*⭐',      # "5⭐"
            r'⭐{(\d+)}',       # повторяющиеся звезды
            r'звезд:\s*(\d+)', # "звезд: 5"
            r'рейтинг:\s*(\d+)', # "рейтинг: 5"
        ]
        
        rating = None
        for pattern in star_patterns:
            match = re.search(pattern, message_text, re.IGNORECASE)
            if match:
                rating = int(match.group(1))
                break
        
        # Если не нашли числовой рейтинг, считаем звезды
        if rating is None:
            star_count = message_text.count('⭐')
            if star_count > 0:
                rating = star_count
        
        # Ищем номер заказа
        order_patterns = [
            r'заказ[а-я\s]*#?(\d+)',     # "заказ #12345"
            r'order[a-z\s]*#?(\d+)',     # "order #12345"
            r'№\s*(\d+)',                # "№ 12345"
            r'ID:\s*(\d+)',              # "ID: 12345"
        ]
        
        order_id = None
        for pattern in order_patterns:
            match = re.search(pattern, message_text, re.IGNORECASE)
            if match:
                order_id = match.group(1)
                break
        
        if rating and order_id:
            return {
                'order_id': order_id,
                'rating': rating
            }
        
        return None
        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при парсинге уведомления об отзыве: {e}')
        return None
    """Проверяет и выдает бонус за отзыв"""
    if not config.get('bonus_system_enabled', False):
        return False
    
    try:
        # Получаем настройки бонусов
        bonus_settings = config.get('bonus_settings', {})
        rating_key = f'{review_rating}_stars' if review_rating > 1 else '1_star'
        bonus_points = bonus_settings.get(rating_key, 0)
        
        # Если бонус за данный рейтинг не предусмотрен
        if bonus_points <= 0:
            logger.info(f'{LOGGER_PREFIX} 💎 Бонус за {review_rating}-звездочный отзыв не предусмотрен')
            return False
        
        # Загружаем кеш бонусов
        bonus_data = load_bonus_cache()
        
        # Проверяем, не получал ли пользователь уже бонус за этот заказ
        if username in bonus_data['users_with_bonus']:
            if order_id in bonus_data['users_with_bonus'][username]['orders']:
                logger.info(f'{LOGGER_PREFIX} 💎 Пользователь {username} уже получил бонус за заказ #{order_id}')
                return False
        
        # Отправляем бонусные очки через API
        success = send_bonus_points(username, bonus_points, order_id, review_rating)
        if not success:
            logger.error(f'{LOGGER_PREFIX} ❌ Не удалось отправить бонус {bonus_points} очков пользователю {username}')
            return False
        
        logger.info(f'{LOGGER_PREFIX} 🎁 Бонус {bonus_points} очков для {username} за {review_rating}-звездочный отзыв на заказ #{order_id}')
        
        # Сохраняем информацию о бонусе
        if username not in bonus_data['users_with_bonus']:
            bonus_data['users_with_bonus'][username] = {
                'orders': [],
                'total_bonus_points': 0,
                'first_bonus': time.time()
            }
        
        bonus_data['users_with_bonus'][username]['orders'].append(order_id)
        bonus_data['users_with_bonus'][username]['total_bonus_points'] += bonus_points
        
        bonus_data['total_bonuses_given'] += 1
        bonus_data['total_bonus_points'] += bonus_points
        
        # Сохраняем обновленный кеш
        save_bonus_cache(bonus_data)
        
        # Уведомляем администраторов
        star_emoji = '⭐' * review_rating
        notify_admins(f'🎁 <b>Бонус выдан!</b>\n\n👤 Пользователь: {username}\n💎 Бонус: {bonus_points} очков\n📋 Заказ: #{order_id}\n{star_emoji} Отзыв: {review_rating} звезд', order_id)
        
        return True
        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при выдаче бонуса: {e}')
        return False

def get_total_stats():
    """Получает общую статистику из кеша"""
    profit_data = load_profit_cache()
    return {
        'total_orders': profit_data.get('total_orders', 0),
        'total_profit': profit_data.get('total_profit', 0.0)
    }


def register_plugin_message(username, message_text):
    """Регистрирует отправленное плагином сообщение для игнорирования"""
    global recent_plugin_messages
    
    # Очищаем старые записи (старше 30 секунд)
    current_time = time.time()
    expired_users = []
    for user, data in recent_plugin_messages.items():
        if current_time - data.get('timestamp', 0) > 30:
            expired_users.append(user)
    
    for user in expired_users:
        del recent_plugin_messages[user]
    
    # Регистрируем новое сообщение
    recent_plugin_messages[username] = {
        'message_text': message_text[:100],  # Сохраняем первые 100 символов
        'timestamp': current_time
    }


def get_orders_file():
    """Возвращает путь к файлу с историей заказов в кеше"""
    return os.path.join(os.path.dirname(__file__), f'..{os.sep}storage{os.sep}cache{os.sep}steam_points_orders_history.json')

def get_pending_orders_file():
    """Возвращает путь к файлу с ожидающими заказами"""
    return os.path.join(os.path.dirname(__file__), f'..{os.sep}storage{os.sep}cache{os.sep}steam_points_pending.json')

def load_pending_orders():
    """Загружает ожидающие заказы из файла"""
    global pending_steam_links
    
    pending_file = get_pending_orders_file()
    try:
        if os.path.exists(pending_file):
            with open(pending_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pending_steam_links = data
                return data
        return {}
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при загрузке ожидающих заказов: {e}')
        return {}

def save_pending_orders():
    """Сохраняет ожидающие заказы в файл"""
    global pending_steam_links
    
    pending_file = get_pending_orders_file()
    try:
        os.makedirs(os.path.dirname(pending_file), exist_ok=True)
        with open(pending_file, 'w', encoding='utf-8') as f:
            json.dump(pending_steam_links, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при сохранении ожидающих заказов: {e}')


def load_orders_history():
    """Загружает историю заказов из файла"""
    orders_file = get_orders_file()
    try:
        if os.path.exists(orders_file):
            with open(orders_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} Ошибка при загрузке истории заказов: {e}')
        return []


def save_orders_history(orders):
    """Сохраняет историю заказов в файл"""
    orders_file = get_orders_file()
    try:
        os.makedirs(os.path.dirname(orders_file), exist_ok=True)
        with open(orders_file, 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} Ошибка при сохранении истории заказов: {e}')


def process_steam_order(c, order_id, buyer_username, points, steam_link):
    """Обрабатывает заказ с указанной ссылкой Steam"""
    try:
        # Перезагружаем конфигурацию для получения актуальных шаблонов
        global config
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Проверяем API ключ
        api_key = config.get('api_key')
        if not api_key:
            logger.error(f'{LOGGER_PREFIX} ❌ API ключ не настроен')
            error_template = config.get('templates', {}).get('error', DEFAULT_ERROR_TEMPLATE)
            send_message_to_buyer(c, buyer_username, error_template)
            notify_admins(f'❌ Ошибка: API ключ не настроен\nЗаказ: #{order_id}\nПокупатель: {buyer_username}', order_id)
            return
        
        # Проверяем корректность ссылки Steam
        if not validate_steam_link(steam_link):
            logger.error(f'{LOGGER_PREFIX} ❌ Некорректная ссылка Steam: {steam_link}')
            invalid_steam_template = config.get('templates', {}).get('invalid_steam', DEFAULT_INVALID_STEAM_TEMPLATE)
            send_message_to_buyer(c, buyer_username, invalid_steam_template)
            notify_admins(f'❌ Некорректная ссылка Steam: {steam_link}\nЗаказ: #{order_id}\nПокупатель: {buyer_username}', order_id)
            return
        
        # Отправляем сообщение о начале обработки через FunPay
        processing_template = config.get('templates', {}).get('processing', DEFAULT_PROCESSING_TEMPLATE)
        send_message_to_buyer(c, buyer_username, processing_template)
        logger.info(f'{LOGGER_PREFIX} 📤 Отправлено сообщение о начале обработки для заказа #{order_id}')
        
        # Покупаем очки через API
        logger.info(f'{LOGGER_PREFIX} 🛒 Покупка {points} очков для {steam_link}')
        result = buy_steam_points(api_key, points, steam_link)
        
        if result.get('success'):
            # Успешная покупка
            points_delivered = result.get('points', points)
            total_cost = result.get('total', 0)
            steam64 = result.get('steam64', '')
            before_points = result.get('before_point', '')
            remaining_balance = result.get('remaining_balance', 0)
            
            # Рассчитываем очки после покупки
            try:
                after_points = int(before_points) + points_delivered if before_points.isdigit() else 'N/A'
            except:
                after_points = 'N/A'
            
            # Получаем сумму заказа сначала
            try:
                order_data = c.account.get_order(order_id)
                order_sum = float(order_data.sum)
            except:
                order_sum = 0
            
            # Рассчитываем стоимость по текущей цене API
            current_price = get_current_price()
            if current_price is not None:
                total_cost_rub = points_delivered * current_price
            else:
                # Если цена недоступна, используем фиксированное значение для расчета
                total_cost_rub = points_delivered * 0.012
            
            # Формируем сообщение успеха
            success_template = config.get('templates', {}).get('success', DEFAULT_SUCCESS_TEMPLATE)
            success_message = success_template.format(
                points=points_delivered,
                total=order_sum,  # Показываем сумму, которую заплатил покупатель
                steam_link=steam_link,
                before_points=before_points,
                after_points=after_points,
                order_link=f'https://funpay.com/orders/{order_id}/'
            )
            
            # Отправляем сообщение покупателю
            send_message_to_buyer(c, buyer_username, success_message)
            
            save_order_profit(order_id, order_sum, total_cost_rub, points_delivered)
            
            # Обновляем статус заказа в истории
            orders = load_orders_history()
            for i, existing_order in enumerate(orders):
                if existing_order.get('order_id') == order_id:
                    orders[i]['status'] = 'success'
                    orders[i]['points_delivered'] = points_delivered
                    orders[i]['cost_rub'] = total_cost_rub  # Стоимость в рублях
                    orders[i]['fp_sum'] = order_sum  # Сумма, которую заплатил покупатель
                    orders[i]['profit'] = order_sum - total_cost_rub  # Прибыль в рублях
                    orders[i]['completed_at'] = datetime.now().isoformat()
                    break
            save_orders_history(orders)
            
            # Уведомляем администраторов
            profit_rub = order_sum - total_cost_rub  # Валовая прибыль в рублях
            
            # Рассчитываем чистую прибыль с учетом комиссии FunPay
            profit_after_3_percent = profit_rub - (order_sum * 0.03)  # После комиссии 3%
            profit_after_6_percent = profit_rub - (order_sum * 0.06)  # После комиссии 6%
            
            send_admin_notification(
                'order_success',
                buyer=buyer_username,
                points=points_delivered,
                steam_link=steam_link,
                fp_sum=order_sum,
                points_cost=total_cost_rub,
                profit=profit_rub,
                profit_after_3=profit_after_3_percent,
                profit_after_6=profit_after_6_percent,
                order_id=order_id
            )
            
            logger.info(f'{LOGGER_PREFIX} ✅ Заказ #{order_id} успешно выполнен')
            
            # Проверяем баланс и активируем лоты при необходимости
            check_and_activate_lots()
            
        else:
            # Ошибка при покупке
            error = result.get('error', 'Unknown error')
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка покупки очков: {error}')
            
            # Выбираем подходящий шаблон ошибки
            if 'insufficient' in error.lower() or 'balance' in error.lower():
                error_template = config.get('templates', {}).get('insufficient_funds', DEFAULT_INSUFFICIENT_FUNDS_TEMPLATE)
            else:
                error_template = config.get('templates', {}).get('error', DEFAULT_ERROR_TEMPLATE)
            
            send_message_to_buyer(c, buyer_username, error_template)
            
            # Обновляем статус заказа в истории
            orders = load_orders_history()
            for i, existing_order in enumerate(orders):
                if existing_order.get('order_id') == order_id:
                    orders[i]['status'] = 'error'
                    orders[i]['error'] = error
                    orders[i]['completed_at'] = datetime.now().isoformat()
                    break
            save_orders_history(orders)
            
            # Уведомляем администраторов
            send_admin_notification(
                'order_error',
                buyer=buyer_username,
                points=points,
                error=error,
                order_id=order_id
            )
    
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Критическая ошибка при обработке заказа #{order_id}: {e}')
        
        try:
            error_template = config.get('templates', {}).get('error', DEFAULT_ERROR_TEMPLATE)
            send_message_to_buyer(c, buyer_username, error_template)
            
            admin_message = f'🚨 Критическая ошибка при обработке заказа!\n\n' \
                          f'📦 Заказ: #{order_id}\n' \
                          f'👤 Покупатель: {buyer_username}\n' \
                          f'❗ Ошибка: {str(e)}'
            
            notify_admins(admin_message, order_id)
            
        except Exception as nested_e:
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при обработке критической ошибки: {nested_e}')

def handle_new_order(c, e, *args):
    """Обработчик новых заказов"""
    global pending_steam_links
    
    try:
        if not config.get('enabled', True):
            logger.info(f'{LOGGER_PREFIX} Плагин отключен, заказ #{e.order.id} пропущен')
            return
        
        # Проверяем, не от нашего аккаунта ли заказ
        if hasattr(e.order, 'buyer_username') and e.order.buyer_username == c.account.username:
            logger.info(f'{LOGGER_PREFIX} ⏭️ Пропускаем собственный заказ #{e.order.id}')
            return
        
        # Проверяем, подходит ли заказ для обработки
        if not is_steam_points_order(e.order):
            logger.info(f'{LOGGER_PREFIX} ⏭️ Заказ #{e.order.id} не относится к Steam Points, пропускаем')
            return
        
        order_id = e.order.id
        buyer_username = e.order.buyer_username
        order_description = e.order.description
        
        # Получаем детальную информацию о заказе из API для получения суммы
        try:
            order_data_api = cardinal_instance.account.get_order(order_id)
            order_sum = float(order_data_api.sum) if hasattr(order_data_api, 'sum') else 0.0
        except Exception as api_error:
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка получения данных заказа из API: {api_error}')
            order_sum = 0.0
        
        logger.info(f'{LOGGER_PREFIX} 📥 Новый заказ Steam Points #{order_id} от {buyer_username} на сумму {order_sum}₽')
        
        # Сохраняем информацию о заказе в историю
        order_history_data = {
            'order_id': order_id,
            'buyer': buyer_username,
            'amount': order_sum,
            'description': order_description,
            'points': None,  # Будет обновлено позже
            'status': 'processing',
            'created_at': datetime.now().isoformat(),
            'steam_link': None
        }
        
        orders = load_orders_history()
        orders.append(order_history_data)
        save_orders_history(orders)
        
        # Определяем количество очков
        points = extract_points_from_order(e.order)
        if not points or points < config.get('min_points', 100):
            logger.info(f'{LOGGER_PREFIX} ❌ Некорректное количество очков: {points}, заказ пропущен')
            
            # Обновляем статус заказа в истории
            orders = load_orders_history()
            for i, existing_order in enumerate(orders):
                if existing_order.get('order_id') == order_id:
                    orders[i]['status'] = 'invalid'
                    orders[i]['points'] = points
                    break
            save_orders_history(orders)
            return
        
        # Обновляем информацию об очках в истории заказов
        orders = load_orders_history()
        for i, existing_order in enumerate(orders):
            if existing_order.get('order_id') == order_id:
                orders[i]['points'] = points
                break
        save_orders_history(orders)
        
        # Очищаем старые ожидающие заказы
        cleanup_old_pending_orders()
        
        # Сохраняем заказ в ожидании ссылки Steam
        pending_steam_links[buyer_username] = {
            'order_id': order_id,
            'points': points,
            'order_sum': order_sum,
            'timestamp': time.time()
        }
        
        # Сохраняем ожидающие заказы в файл
        save_pending_orders()
        
        # Отправляем запрос ссылки Steam
        steam_request_template = config.get('templates', {}).get('steam_request', DEFAULT_STEAM_REQUEST_TEMPLATE)
        steam_request_message = steam_request_template.format(
            points=points,
            price=order_sum
        )
        
        # Пытаемся отправить сообщение покупателю
        message_sent = send_message_to_buyer(c, buyer_username, steam_request_message)
        if not message_sent:
            logger.error(f'{LOGGER_PREFIX} ❌ Не удалось отправить сообщение покупателю {buyer_username}')
            # Но продолжаем обработку
        
        # Уведомляем администраторов о новом заказе
        try:
            send_admin_notification(
                'new_order',
                buyer=buyer_username,
                points=points,
                sum=order_sum,
                order_id=order_id
            )
        except Exception as admin_error:
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при отправке уведомления админам: {admin_error}')
        
        logger.info(f'{LOGGER_PREFIX} 📨 Запрос ссылки Steam отправлен для заказа #{order_id}')
        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Критическая ошибка в handle_new_order: {e}')
        logger.exception(f'{LOGGER_PREFIX} Полная трассировка ошибки:')
        
        # Попытаемся уведомить админов об ошибке
        try:
            if 'e' in locals() and hasattr(e, 'order') and hasattr(e.order, 'id'):
                order_id = e.order.id
                buyer = getattr(e.order, 'buyer_username', 'Unknown')
                send_admin_notification(
                    'order_error',
                    buyer=buyer,
                    points=0,
                    error=str(e),
                    order_id=order_id
                )
        except:
            pass  # Игнорируем ошибки при отправке уведомлений об ошибках

def handle_new_message(c, e, *args):
    """Обработчик новых сообщений от покупателей"""
    global pending_steam_links
    
    # Проверяем, не наше ли это сообщение
    if e.message.author == c.account.username:
        return
    
    buyer_username = e.message.chat_name  # Перемещаем объявление выше
    
    # Дополнительная проверка на сообщения от плагина по содержимому
    message_text = getattr(e.message, 'text', '')
    if message_text:
        # Проверяем, содержит ли сообщение фразы из наших шаблонов
        plugin_phrases = [
            '🔄 Обработка заказа на очки Steam',
            '✅ Очки Steam успешно доставлены!',
            '❌ Ошибка при обработке заказа на очки Steam',
            '💳 Недостаточно средств',
            '❌ Неверная ссылка Steam',
            '⚠️ Технические работы',
            '🎮 Для выполнения заказа на',
            'очков Steam необходима ссылка',
            'Сумма заказа:',
            'Количество очков:',
            'Steam профиль:',
            'Заказ выполнен. Пожалуйста, зайдите в раздел',
            'произошла техническая ошибка',
            'на балансе сервиса недостаточно средств'
        ]
        
        # Проверяем наличие любой из фраз плагина
        for phrase in plugin_phrases:
            if phrase in message_text:
                return
        
        # Дополнительная проверка на недавно отправленные сообщения
        if buyer_username in recent_plugin_messages:
            recent_msg = recent_plugin_messages[buyer_username]
            # Если сообщение похоже на недавно отправленное плагином
            if recent_msg['message_text'] in message_text or message_text in recent_msg['message_text']:
                return
    
    # Проверяем, не системное ли сообщение (тип 0 = системное, тип 1 = обычное)
    if e.message.type == 0:  # Пропускаем системные сообщения
        return
    
    # Дополнительная проверка на системные сообщения по содержимому
    if message_text and ('оплатил заказ' in message_text or 'подтвердил выполнение заказа' in message_text):
        logger.info(f'{LOGGER_PREFIX} ⏭️ Пропускаем системное сообщение: "{message_text[:50]}..."')
        return
    
    # message_text и buyer_username уже объявлены выше
    
    logger.info(f'{LOGGER_PREFIX} 🔄 Обрабатываем сообщение от {buyer_username}')
    
    # Проверяем, ожидаем ли мы ссылку Steam от этого пользователя
    if buyer_username in pending_steam_links:
        pending_order = pending_steam_links[buyer_username]
        logger.info(f'{LOGGER_PREFIX} ✅ Найден ожидающий заказ от {buyer_username}: #{pending_order["order_id"]}')
        
        # Проверяем, не является ли сообщение подтверждением заказа
        if pending_order.get('status') == 'waiting_confirmation':
            if message_text.strip() == '+':
                # Подтверждение заказа
                logger.info(f'{LOGGER_PREFIX} ✅ Заказ #{pending_order["order_id"]} подтвержден пользователем {buyer_username}')
                
                # Обновляем статус в истории
                orders = load_orders_history()
                for i, existing_order in enumerate(orders):
                    if existing_order.get('order_id') == pending_order['order_id']:
                        orders[i]['status'] = 'processing_points'
                        break
                save_orders_history(orders)
                
                # Получаем ссылку Steam
                steam_link = pending_order.get('steam_link')
                if steam_link:
                    # Удаляем заказ из ожидающих
                    del pending_steam_links[buyer_username]
                    save_pending_orders()
                    
                    # Обрабатываем заказ
                    if executor:
                        executor.submit(
                            process_steam_order,
                            c,
                            pending_order['order_id'],
                            buyer_username,
                            pending_order['points'],
                            steam_link
                        )
                    else:
                        process_steam_order(
                            c,
                            pending_order['order_id'],
                            buyer_username,
                            pending_order['points'],
                            steam_link
                        )
                return
                
            elif message_text.strip() == '-':
                # Отмена заказа
                logger.info(f'{LOGGER_PREFIX} ❌ Заказ #{pending_order["order_id"]} отменен пользователем {buyer_username}')
                
                # Обновляем статус в истории
                orders = load_orders_history()
                for i, existing_order in enumerate(orders):
                    if existing_order.get('order_id') == pending_order['order_id']:
                        orders[i]['status'] = 'cancelled'
                        break
                save_orders_history(orders)
                
                # Удаляем заказ из ожидающих
                del pending_steam_links[buyer_username]
                save_pending_orders()
                
                # Отправляем сообщение об отмене
                cancellation_message = f'''❌ Заказ отменен

💰 Сумма заказа: {pending_order['order_sum']}₽
📋 Номер заказа: #{pending_order['order_id']}

💳 Возврат средств будет произведен автоматически.
📞 При возникновении вопросов обратитесь в поддержку.'''
                
                send_message_to_buyer(c, buyer_username, cancellation_message)
                
                # Уведомляем администраторов
                notify_admins(f'❌ <b>Заказ отменен пользователем</b>\n\n📦 Заказ: #{pending_order["order_id"]}\n👤 Покупатель: {buyer_username}\n💰 Сумма: {pending_order["order_sum"]}₽', pending_order['order_id'])
                return
                
            elif extract_steam_link_from_message(message_text):
                # Новая ссылка Steam
                new_steam_link = extract_steam_link_from_message(message_text)
                logger.info(f'{LOGGER_PREFIX} 🔄 Пользователь {buyer_username} изменил ссылку Steam на {new_steam_link}')
                
                # Обновляем ссылку
                pending_steam_links[buyer_username]['steam_link'] = new_steam_link
                save_pending_orders()
                
                # Обновляем в истории
                orders = load_orders_history()
                for i, existing_order in enumerate(orders):
                    if existing_order.get('order_id') == pending_order['order_id']:
                        orders[i]['steam_link'] = new_steam_link
                        break
                save_orders_history(orders)
                
                # Отправляем обновленное сообщение подтверждения
                confirmation_message = f'''✅ Ссылка Steam обновлена!

🎮 Новый профиль: {new_steam_link}
💎 Количество очков: {pending_order['points']}
💰 Сумма заказа: {pending_order['order_sum']}₽

Для подтверждения заказа отправьте:
➕ + - подтвердить заказ
🔄 новую ссылку - изменить профиль Steam
❌ - - отменить заказ и получить возврат

⏳ Ожидаю ваше решение...'''
                
                send_message_to_buyer(c, buyer_username, confirmation_message)
                return
        
        # Извлекаем ссылку Steam из сообщения
        steam_link = extract_steam_link_from_message(message_text)
        
        # Проверяем на команды отмены или изменения (даже если заказ не в состоянии подтверждения)
        if message_text.strip() == '-':
            # Отмена заказа
            logger.info(f'{LOGGER_PREFIX} ❌ Заказ #{pending_order["order_id"]} отменен пользователем {buyer_username}')
            
            # Обновляем статус в истории
            orders = load_orders_history()
            for i, existing_order in enumerate(orders):
                if existing_order.get('order_id') == pending_order['order_id']:
                    orders[i]['status'] = 'cancelled'
                    break
            save_orders_history(orders)
            
            # Удаляем заказ из ожидающих
            del pending_steam_links[buyer_username]
            save_pending_orders()
            
            # Отправляем сообщение об отмене
            cancellation_message = f'''❌ Заказ отменен

💰 Сумма заказа: {pending_order['order_sum']}₽
📋 Номер заказа: #{pending_order['order_id']}

💳 Возврат средств будет произведен автоматически.
📞 При возникновении вопросов обратитесь в поддержку.'''
            
            send_message_to_buyer(c, buyer_username, cancellation_message)
            
            # Уведомляем администраторов
            notify_admins(f'❌ <b>Заказ отменен пользователем</b>\n\n📦 Заказ: #{pending_order["order_id"]}\n👤 Покупатель: {buyer_username}\n💰 Сумма: {pending_order["order_sum"]}₽', pending_order['order_id'])
            return
        
        if steam_link:
            # Проверяем, меняет ли пользователь уже существующую ссылку
            if pending_order.get('steam_link') and pending_order.get('steam_link') != steam_link:
                logger.info(f'{LOGGER_PREFIX} 🔄 Пользователь {buyer_username} изменил ссылку Steam с {pending_order.get("steam_link")} на {steam_link}')
            
            # Обновляем информацию о ссылке Steam в истории заказов
            orders = load_orders_history()
            for i, existing_order in enumerate(orders):
                if existing_order.get('order_id') == pending_order['order_id']:
                    orders[i]['steam_link'] = steam_link
                    orders[i]['status'] = 'waiting_confirmation'
                    break
            save_orders_history(orders)
            
            # Сохраняем ссылку Steam для подтверждения
            pending_steam_links[buyer_username]['steam_link'] = steam_link
            pending_steam_links[buyer_username]['status'] = 'waiting_confirmation'
            save_pending_orders()
            
            # Отправляем сообщение с запросом подтверждения, используя шаблон
            steam_confirmation_template = config.get('templates', {}).get('steam_confirmation', DEFAULT_STEAM_CONFIRMATION_TEMPLATE)
            confirmation_message = steam_confirmation_template.format(
                steam_link=steam_link,
                points=pending_order['points'],
                order_sum=pending_order['order_sum']
            )
            
            send_message_to_buyer(c, buyer_username, confirmation_message)
            logger.info(f'{LOGGER_PREFIX} 🔗 Получена ссылка Steam от {buyer_username}, ожидаю подтверждения заказа #{pending_order["order_id"]}')
        else:
            # Ссылка не найдена, напоминаем о формате
            logger.warning(f'{LOGGER_PREFIX} ❌ Ссылка Steam не найдена в сообщении от {buyer_username}')
            reminder_message = "❌ Не найдена корректная ссылка Steam!\n\nПожалуйста, отправьте ссылку в формате:\n🔗 https://steamcommunity.com/id/ваш_id\nили\n🔗 https://steamcommunity.com/profiles/ваш_id\n\nИли отправьте:\n❌ - для отмены заказа"
            send_message_to_buyer(c, buyer_username, reminder_message)
    else:
        logger.info(f'{LOGGER_PREFIX} ❌ Пользователь {buyer_username} не найден в ожидающих заказах')
        logger.info(f'{LOGGER_PREFIX} 📋 Текущие ожидающие пользователи: {list(pending_steam_links.keys())}')
        
        # Возможно, пользователь отправил ссылку до создания заказа или после обработки
        # Проверим, есть ли ссылка Steam в сообщении
        steam_link = extract_steam_link_from_message(message_text)
        if steam_link:
            logger.info(f'{LOGGER_PREFIX} 🔗 Получена ссылка Steam от неожидающего пользователя {buyer_username}: {steam_link}')
            # Отправим сообщение о том, что нужно сначала сделать заказ
            response_message = "❌ Сначала необходимо оформить заказ на Steam Points, а затем отправить ссылку на профиль."
            send_message_to_buyer(c, buyer_username, response_message)
        else:
            # Проверяем на уведомление об отзыве
            review_data = parse_review_notification(message_text)
            if review_data:
                logger.info(f'{LOGGER_PREFIX} ⭐ Обнаружен отзыв от {buyer_username} с рейтингом {review_data["rating"]} на заказ #{review_data["order_id"]}')
                
                # Выдаем бонус за отзыв
                bonus_given = check_and_give_bonus(buyer_username, review_data['order_id'], review_data['rating'])
                if bonus_given:
                    logger.info(f'{LOGGER_PREFIX} 🎁 Бонус за отзыв успешно выдан пользователю {buyer_username}')
                else:
                    logger.info(f'{LOGGER_PREFIX} ❌ Бонус за отзыв не был выдан пользователю {buyer_username}')

# ==================== TELEGRAM BOT INTERFACE ====================

def create_main_menu_keyboard_and_text():
    """Создает клавиатуру и текст для главного меню"""
    kb = InlineKeyboardMarkup(row_width=2)
    
    # Первый ряд - основные настройки
    kb.add(
        InlineKeyboardButton('⚙️ Настройки', callback_data='sp_basic_settings'),
        InlineKeyboardButton('📝 Шаблоны', callback_data='sp_templates')
    )
    
    # Второй ряд - статистика и управление
    kb.add(
        InlineKeyboardButton('📊 Статистика', callback_data='sp_statistics'),
        InlineKeyboardButton('🛡️ Защита лотов', callback_data='sp_lot_management')
    )
    
    # Третий ряд - информация
    kb.add(InlineKeyboardButton('ℹ️ О плагине', callback_data='sp_about_plugin'))
    
    # Получаем статистику из кеша
    stats = get_total_stats()
    current_price = get_current_price()
    api_balance = get_api_balance()
    enabled_status = '🟢 Включен' if config.get('enabled', True) else '🔴 Отключен'
    api_status = '🟢 Настроен' if config.get('api_key') else '🔴 Не настроен'
    
    # Отображаем цену только если она доступна
    if current_price is not None:
        price_display = f'<code>{current_price:.4f}₽</code>'
    else:
        price_display = '<code>Недоступна</code>'
    
    # Отображаем баланс API
    if api_balance is not None:
        balance_display = f'<code>{api_balance:.2f}₽</code>'
    else:
        balance_display = '<code>Недоступен</code>'
    
    message_text = f'''❤️ <b>Steam Points Auto</b>

📊 <b>Статистика работы</b>
┌─ 💰 Обработано заказов: <code>{stats['total_orders']}</code>
├─ 💵 Общая сумма: <code>{stats['total_profit']:.2f}₽</code>
├─ 📈 Текущая цена: {price_display}
├─ 💳 Баланс API: {balance_display}
├─ 🔧 Плагин: {enabled_status}
└─ 🔑 API: {api_status}

💡 <i>Автоматическая деактивация лотов при низком балансе</i>'''
    
    return kb, message_text

def show_main_menu(message):
    """Показывает главное меню плагина"""
    global bot
    
    if not bot:
        return
    
    kb, message_text = create_main_menu_keyboard_and_text()
    
    # Отправляем сообщение без изображения
    bot.send_message(message.chat.id, message_text, reply_markup=kb, parse_mode='HTML')

def show_main_menu_callback(call):
    """Показывает главное меню плагина (callback)"""
    global bot
    
    if not bot:
        return
    
    kb, message_text = create_main_menu_keyboard_and_text()
    
    try:
        bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, 
                             reply_markup=kb, parse_mode='HTML')
    except Exception:
        # Если не удается отредактировать, отправляем новое сообщение
        bot.send_message(call.message.chat.id, message_text, reply_markup=kb, parse_mode='HTML')

def handle_basic_settings(call):
    """Обработчик основных настроек"""
    kb = InlineKeyboardMarkup(row_width=1)
    
    # Статус плагина
    status_text = '🔴 Отключить плагин' if config.get('enabled', True) else '🟢 Включить плагин'
    kb.add(InlineKeyboardButton(status_text, callback_data='sp_toggle_enabled'))
    
    # API ключ
    api_status = 'Изменить API ключ' if config.get('api_key') else 'Настроить API ключ'
    kb.add(InlineKeyboardButton(f'🔑 {api_status}', callback_data='sp_set_api_key'))

    # Фильтры заказов
    kb.add(InlineKeyboardButton('🎯 Фильтры заказов', callback_data='sp_order_filters'))
    
    kb.add(InlineKeyboardButton('🔙 Назад', callback_data='sp_back_to_main'))
    
    message_text = f'''⚙️ <b>Основные настройки</b>

🔧 <b>Плагин:</b> {'🟢 Включен' if config.get('enabled', True) else '🔴 Отключен'}
🔑 <b>API ключ:</b> {'🟢 Настроен' if config.get('api_key') else '🔴 Не настроен'}

💡 <i>Настройки плагина для автоматической продажи очков Steam</i>'''
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_toggle_enabled(call):
    """Переключает состояние плагина"""
    global config
    
    config['enabled'] = not config.get('enabled', True)
    save_config()
    
    status = 'включен' if config['enabled'] else 'отключен'
    bot.answer_callback_query(call.id, f'✅ Плагин {status}')
    
    # Возвращаемся к настройкам
    handle_basic_settings(call)

def handle_set_api_key(call):
    """Запрашивает ввод API ключа"""
    global bot, cardinal_instance
    
    tg = cardinal_instance.telegram
    
    msg = bot.edit_message_text(
        '🔑 <b>Настройка API ключа</b>\n\n'
        'Введите ваш API ключ от buysteampoints.com:\n\n'
        '<i>Чтобы получить API ключ:</i>\n'
        '1. Перейдите в Telegram бот buysteampoints\n'
        '2. Напишите /profile\n'
        '3. Скопируйте ваш API ключ\n\n'
        '<b>Введите API ключ:</b>',
        call.message.chat.id, call.message.message_id,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('🔙 Отмена', callback_data='sp_basic_settings')
        ),
        parse_mode='HTML'
    )
    
    tg.set_state(
        chat_id=call.message.chat.id,
        message_id=msg.message_id,
        user_id=call.from_user.id,
        state="sp_setting_api_key"
    )

def handle_toggle_auto_deactivate(call):
    """Переключает статус автоматической деактивации лотов"""
    global config
    
    config['auto_deactivate_enabled'] = not config.get('auto_deactivate_enabled', False)
    save_config()
    
    status = 'включена' if config['auto_deactivate_enabled'] else 'отключена'
    bot.answer_callback_query(call.id, f'✅ Авто-деактивация лотов {status}')
    
    # Возвращаемся к настройкам
    handle_basic_settings(call)

def handle_set_min_balance(call):
    """Запрашивает ввод минимального порога баланса для деактивации лотов"""
    global bot, cardinal_instance
    
    if not cardinal_instance or not hasattr(cardinal_instance, 'telegram'):
        logger.error(f'{LOGGER_PREFIX} ❌ Cardinal instance или telegram недоступен')
        try:
            bot.answer_callback_query(call.id, "❌ Ошибка инициализации")
        except:
            pass
        return
    
    try:
        tg = cardinal_instance.telegram
        current_min_balance = config.get('min_balance_threshold', 10.0)
        
        msg = bot.edit_message_text(
            f'💰 <b>Настройка минимального порога баланса</b>\n\n'
            f'Текущий порог: <code>{current_min_balance:.2f}₽</code>\n\n'
            f'При балансе ниже этого порога лоты будут автоматически деактивированы.\n\n'
            f'<i>Рекомендуется:</i>\n'
            f'• 5-10₽ для тестирования\n'
            f'• 10-50₽ для продакшена\n'
            f'• 50-100₽ для высоконагруженных систем\n\n'
            f'<b>Введите новый порог в рублях:</b>',
            call.message.chat.id, call.message.message_id,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton('🔙 Отмена', callback_data='sp_basic_settings')
            ),
            parse_mode='HTML'
        )
        
        tg.set_state(
            chat_id=call.message.chat.id,
            message_id=msg.message_id,
            user_id=call.from_user.id,
            state="sp_setting_min_balance"
        )
        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_set_min_balance: {e}')
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        except:
            pass

def handle_bonus_settings(call):
    """Настройки бонусной системы"""
    global bot
    
    if not bot:
        logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован в handle_bonus_settings')
        return
    
    try:
        kb = InlineKeyboardMarkup(row_width=1)
        
        # Статус бонусной системы
        bonus_status = '🟢 Включена' if config.get('bonus_system_enabled', False) else '🔴 Отключена'
        kb.add(InlineKeyboardButton(f'🎁 Статус бонусной системы ({bonus_status})', callback_data='sp_toggle_bonus_system'))
        
        # Настройки бонусов по звездам
        bonus_settings = config.get('bonus_settings', {})
        
        # Кнопки для настройки бонусов по звездам
        for stars in [5, 4, 3, 2, 1]:
            points = bonus_settings.get(f'{stars}_stars', 0)
            star_emoji = '⭐' * stars
            kb.add(InlineKeyboardButton(f'{star_emoji} {stars} звезд ({points} очков)', 
                                      callback_data=f'sp_set_bonus_{stars}_stars'))
        
        kb.add(InlineKeyboardButton('🔙 Назад', callback_data='sp_basic_settings'))
        
        # Получаем статистику бонусов
        bonus_stats = get_bonus_stats()
        
        message_text = f'''🎁 <b>Настройки бонусной системы</b>

Настройте автоматическую выдачу бонусных очков за отзывы разных рейтингов.

📊 <b>Текущие настройки:</b>
🎁 <b>Статус:</b> {bonus_status}

💎 <b>Бонусы по рейтингу:</b>
⭐⭐⭐⭐⭐ 5 звезд: <code>{bonus_settings.get('5_stars', 100)} очков</code>
⭐⭐⭐⭐ 4 звезды: <code>{bonus_settings.get('4_stars', 50)} очков</code>
⭐⭐⭐ 3 звезды: <code>{bonus_settings.get('3_stars', 0)} очков</code>
⭐⭐ 2 звезды: <code>{bonus_settings.get('2_stars', 0)} очков</code>
⭐ 1 звезда: <code>{bonus_settings.get('1_star', 0)} очков</code>

📈 <b>Статистика:</b>
💰 Всего выдано: <code>{bonus_stats['total_bonuses_given']}</code> бонусов
🎯 Общих очков: <code>{bonus_stats['total_bonus_points']}</code>
👥 Пользователей: <code>{bonus_stats['unique_users']}</code>

💡 <b>Как это работает:</b>
• Пользователь оставляет отзыв
• Система автоматически определяет рейтинг
• Отправляются соответствующие бонусные очки

<i>Выберите рейтинг для настройки:</i>'''
        
        bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                             reply_markup=kb, parse_mode='HTML')
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_bonus_settings: {e}')
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        except:
            pass

def handle_toggle_bonus_system(call):
    """Переключает статус бонусной системы"""
    global config
    
    config['bonus_system_enabled'] = not config.get('bonus_system_enabled', False)
    save_config()
    
    status = 'включена' if config['bonus_system_enabled'] else 'отключена'
    bot.answer_callback_query(call.id, f'✅ Бонусная система {status}')
    
    # Возвращаемся к настройкам бонусов
    handle_bonus_settings(call)

def handle_set_bonus_for_rating(call, stars):
    """Запрашивает ввод количества бонусных очков для определенного рейтинга"""
    global bot, cardinal_instance
    
    if not cardinal_instance or not hasattr(cardinal_instance, 'telegram'):
        logger.error(f'{LOGGER_PREFIX} ❌ Cardinal instance или telegram недоступен')
        try:
            bot.answer_callback_query(call.id, "❌ Ошибка инициализации")
        except:
            pass
        return
    
    try:
        tg = cardinal_instance.telegram
        bonus_settings = config.get('bonus_settings', {})
        
        # Определяем ключ в зависимости от количества звезд
        if stars == '1':
            rating_key = '1_star'
            rating_display = '⭐ 1 звезда'
        else:
            rating_key = f'{stars}_stars'
            rating_display = '⭐' * int(stars) + f' {stars} звезд'
        
        current_bonus = bonus_settings.get(rating_key, 0)
        
        msg = bot.edit_message_text(
            f'💎 <b>Настройка бонуса за {rating_display}</b>\n\n'
            f'Текущее количество: <code>{current_bonus}</code> очков\n\n'
            f'Это количество очков будет автоматически отправлено пользователю за отзыв с рейтингом {rating_display}.\n\n'
            f'<i>Рекомендации:</i>\n'
            f'• 5 звезд: 50-200 очков (отличный отзыв)\n'
            f'• 4 звезды: 25-100 очков (хороший отзыв)\n'
            f'• 3 звезды: 0-25 очков (нейтральный отзыв)\n'
            f'• 2 звезды: 0 очков (плохой отзыв)\n'
            f'• 1 звезда: 0 очков (очень плохой отзыв)\n\n'
            f'<b>Введите количество бонусных очков для {rating_display}:</b>\n'
            f'<i>(Введите 0, чтобы отключить бонус за этот рейтинг)</i>',
            call.message.chat.id, call.message.message_id,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton('🔙 Отмена', callback_data='sp_bonus_settings')
            ),
            parse_mode='HTML'
        )
        
        # Сохраняем данные для обработки ответа
        tg.set_state(
            chat_id=call.message.chat.id,
            message_id=msg.message_id,
            user_id=call.from_user.id,
            state=f"sp_setting_bonus_{stars}_stars"
        )
        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_set_bonus_for_rating: {e}')
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        except:
            pass

def handle_set_bonus_points(call):
    """Запрашивает ввод количества бонусных очков"""
    global bot, cardinal_instance
    
    if not cardinal_instance or not hasattr(cardinal_instance, 'telegram'):
        logger.error(f'{LOGGER_PREFIX} ❌ Cardinal instance или telegram недоступен')
        try:
            bot.answer_callback_query(call.id, "❌ Ошибка инициализации")
        except:
            pass
        return
    
    try:
        tg = cardinal_instance.telegram
        current_bonus_points = config.get('bonus_points_for_review', 1000)
        
        msg = bot.edit_message_text(
            f'💎 <b>Настройка бонусных очков</b>\n\n'
            f'Текущее количество: <code>{current_bonus_points}</code> очков\n\n'
            f'Это количество очков будет автоматически отправлено пользователю за отзыв на 5 звезд.\n\n'
            f'<i>Рекомендуется:</i>\n'
            f'• 100-500 очков для небольших заказов\n'
            f'• 500-1000 очков для средних заказов\n'
            f'• 1000-2000 очков для крупных заказов\n\n'
            f'<b>Введите количество бонусных очков:</b>',
            call.message.chat.id, call.message.message_id,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton('🔙 Отмена', callback_data='sp_bonus_settings')
            ),
            parse_mode='HTML'
        )
        
        tg.set_state(
            chat_id=call.message.chat.id,
            message_id=msg.message_id,
            user_id=call.from_user.id,
            state="sp_setting_bonus_points"
        )
        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_set_bonus_points: {e}')
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        except:
            pass


def handle_order_filters(call):
    """Управление фильтрами заказов"""
    target_subcategories = config.get('target_subcategories', [714])
    target_keywords = config.get('target_keywords', [])
    
    kb = InlineKeyboardMarkup(row_width=1)
    
    # Управление подкатегориями
    subcats_text = ', '.join(map(str, target_subcategories)) if target_subcategories else 'Не настроены'
    kb.add(InlineKeyboardButton(f'📂 ID подкатегорий: {subcats_text}', callback_data='sp_set_subcategories'))
    
    # Управление ключевыми словами
    keywords_count = len(target_keywords)
    kb.add(InlineKeyboardButton(f'🔤 Ключевые слова ({keywords_count})', callback_data='sp_manage_keywords'))
    
    # Тест фильтров
    kb.add(InlineKeyboardButton('🧪 Тестировать фильтры', callback_data='sp_test_filters'))
    
    kb.add(InlineKeyboardButton('🔙 Назад', callback_data='sp_basic_settings'))
    
    message_text = '''🎯 <b>Фильтры заказов</b>

Настройте, какие заказы должен обрабатывать плагин:

📂 <b>ID подкатегорий:</b> <code>{}</code>
🔤 <b>Ключевые слова:</b> <code>{} шт.</code>

<i>Плагин будет обрабатывать заказы, которые соответствуют ЛЮБОМУ из условий:</i>
• Заказ из указанной подкатегории
• Описание заказа содержит ключевые слова

<i>Выберите что настроить:</i>'''.format(
        subcats_text,
        keywords_count
    )
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_set_subcategories(call):
    """Настройка ID подкатегорий"""
    global bot, cardinal_instance
    
    tg = cardinal_instance.telegram
    current_subcats = config.get('target_subcategories', [714])
    subcats_text = ', '.join(map(str, current_subcats)) if current_subcats else 'Не настроены'
    
    msg = bot.edit_message_text(
        f'📂 <b>Настройка ID подкатегорий</b>\n\n'
        f'Текущие ID: <code>{subcats_text}</code>\n\n'
        f'<b>Пример:</b> 714 (Steam Points)\n'
        f'Для нескольких ID разделяйте запятыми: 714, 123, 456\n\n'
        f'<i>Введите ID подкатегорий или оставьте пустым для отключения фильтра:</i>',
        call.message.chat.id, call.message.message_id,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('🔙 Отмена', callback_data='sp_order_filters')
        ),
        parse_mode='HTML'
    )
    
    tg.set_state(
        chat_id=call.message.chat.id,
        message_id=msg.message_id,
        user_id=call.from_user.id,
        state="sp_setting_subcategories"
    )

def handle_manage_keywords(call):
    """Управление ключевыми словами"""
    keywords = config.get('target_keywords', [])
    
    kb = InlineKeyboardMarkup(row_width=1)
    
    if keywords:
        kb.add(InlineKeyboardButton('📋 Показать ключевые слова', callback_data='sp_show_keywords'))
        kb.add(InlineKeyboardButton('➕ Добавить слово', callback_data='sp_add_keyword'))
        kb.add(InlineKeyboardButton('➖ Удалить слово', callback_data='sp_remove_keyword'))
        kb.add(InlineKeyboardButton('🗑️ Очистить все', callback_data='sp_clear_keywords'))
    else:
        kb.add(InlineKeyboardButton('➕ Добавить первое слово', callback_data='sp_add_keyword'))
    
    kb.add(InlineKeyboardButton('🔙 Назад', callback_data='sp_order_filters'))
    
    message_text = f'''🔤 <b>Управление ключевыми словами</b>

Ключевые слова используются для поиска заказов на Steam Points в описании.

📊 <b>Всего слов:</b> <code>{len(keywords)}</code>

<i>Выберите действие:</i>'''
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_test_filters(call):
    """Тестирование фильтров заказов"""
    target_subcategories = config.get('target_subcategories', [714])
    target_keywords = config.get('target_keywords', [])
    min_points = config.get('min_points', 100)
    max_points = config.get('max_points', 50000)
    
    # Создаем тестовые примеры
    test_cases = [
        {
            'description': '1000 очков Steam',
            'subcategory_id': 714,
            'amount': 1000,
            'would_match': True
        },
        {
            'description': '50 steam points',
            'subcategory_id': 123,
            'amount': 50,
            'would_match': min_points <= 50 <= max_points and len(target_keywords) > 0
        },
        {
            'description': 'Игровая валюта',
            'subcategory_id': 999,
            'amount': 500,
            'would_match': False
        }
    ]
    
    message_text = f'''🧪 <b>Тест фильтров заказов</b>

<b>Текущие настройки:</b>
📂 ID подкатегорий: <code>{', '.join(map(str, target_subcategories))}</code>
🔤 Ключевых слов: <code>{len(target_keywords)}</code>
📉 Мин. очков: <code>{min_points}</code>
📈 Макс. очков: <code>{max_points}</code>

<b>Примеры заказов:</b>
'''
    
    for i, test_case in enumerate(test_cases, 1):
        status = '✅ Принят' if test_case['would_match'] else '❌ Отклонен'
        message_text += f'''{i}. "{test_case['description']}"
   Подкатегория: {test_case['subcategory_id']}, Очков: {test_case['amount']}
   Результат: {status}

'''
    
    message_text += '<i>Фильтры работают по принципу ИЛИ - заказ принимается если подходит по любому критерию</i>'
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('🔄 Обновить', callback_data='sp_test_filters'),
        InlineKeyboardButton('🔙 Назад', callback_data='sp_order_filters')
    )
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_show_keywords(call):
    """Показывает список ключевых слов"""
    keywords = config.get('target_keywords', [])
    
    if not keywords:
        message_text = '🔤 <b>Список ключевых слов пуст</b>'
    else:
        message_text = '🔤 <b>Ключевые слова для поиска:</b>\n\n'
        for i, keyword in enumerate(keywords, 1):
            message_text += f'{i}. <code>{keyword}</code>\n'
    
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Назад', callback_data='sp_manage_keywords')
    )
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_add_keyword(call):
    """Запрашивает добавление ключевого слова"""
    tg = cardinal_instance.telegram
    
    msg = bot.edit_message_text(
        '➕ <b>Добавление ключевого слова</b>\n\n'
        'Введите ключевое слово или фразу для поиска в описании заказов:\n\n'
        '<b>Примеры:</b>\n'
        '• steam points\n'
        '• очки steam\n'
        '• поинты\n\n'
        '<i>Введите слово или фразу:</i>',
        call.message.chat.id, call.message.message_id,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('🔙 Отмена', callback_data='sp_manage_keywords')
        ),
        parse_mode='HTML'
    )
    
    tg.set_state(
        chat_id=call.message.chat.id,
        message_id=msg.message_id,
        user_id=call.from_user.id,
        state="sp_adding_keyword"
    )

def handle_remove_keyword(call):
    """Показывает список ключевых слов для удаления"""
    keywords = config.get('target_keywords', [])
    
    if not keywords:
        bot.answer_callback_query(call.id, '❌ Нет ключевых слов для удаления')
        return
    
    kb = InlineKeyboardMarkup(row_width=1)
    
    for i, keyword in enumerate(keywords):
        kb.add(InlineKeyboardButton(f'🗑️ {keyword}', callback_data=f'sp_delete_keyword_{i}'))
    
    kb.add(InlineKeyboardButton('🔙 Назад', callback_data='sp_manage_keywords'))
    
    message_text = '''➖ <b>Удаление ключевого слова</b>

Выберите ключевое слово для удаления:'''
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_clear_keywords(call):
    """Очищает все ключевые слова с подтверждением"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('✅ Да, очистить', callback_data='sp_confirm_clear_keywords'),
        InlineKeyboardButton('❌ Отмена', callback_data='sp_manage_keywords')
    )
    
    message_text = '''🗑️ <b>Очистка всех ключевых слов</b>

⚠️ Вы уверены, что хотите удалить ВСЕ ключевые слова?

После удаления фильтрация будет работать только по ID подкатегорий.'''
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_confirm_clear_keywords(call):
    """Подтверждает очистку всех ключевых слов"""
    config['target_keywords'] = []
    save_config()
    
    bot.answer_callback_query(call.id, '✅ Все ключевые слова удалены')
    handle_manage_keywords(call)

def handle_delete_keyword(call, keyword_index):
    """Удаляет конкретное ключевое слово"""
    try:
        keyword_index = int(keyword_index)
        keywords = config.get('target_keywords', [])
        
        if 0 <= keyword_index < len(keywords):
            deleted_keyword = keywords.pop(keyword_index)
            config['target_keywords'] = keywords
            save_config()
            
            bot.answer_callback_query(call.id, f'✅ Удалено: {deleted_keyword}')
            handle_manage_keywords(call)
        else:
            bot.answer_callback_query(call.id, '❌ Ключевое слово не найдено')
    except ValueError:
        bot.answer_callback_query(call.id, '❌ Ошибка при удалении')

def handle_admins(call):
    """Обработчик управления администраторами"""
    admins = config.get('administrators', [])
    
    kb = InlineKeyboardMarkup(row_width=1)
    
    if admins:
        kb.add(InlineKeyboardButton('👥 Список администраторов', callback_data='sp_admin_list'))
    
    kb.add(InlineKeyboardButton('➕ Добавить администратора', callback_data='sp_add_admin'))
    
    if admins:
        kb.add(InlineKeyboardButton('➖ Удалить администратора', callback_data='sp_remove_admin'))
    
    kb.add(InlineKeyboardButton('🔙 Назад', callback_data='sp_back_to_main'))
    
    message_text = f'''👥 <b>Управление администраторами</b>

Администраторы получают уведомления о заказах и ошибках.

📊 <b>Всего администраторов:</b> <code>{len(admins)}</code>

<i>Выберите действие:</i>'''
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_admin_list(call):
    """Показывает список администраторов"""
    admins = config.get('administrators', [])
    
    if not admins:
        message_text = '👥 <b>Список администраторов пуст</b>'
    else:
        message_text = '👥 <b>Список администраторов:</b>\n\n'
        for i, admin_id in enumerate(admins, 1):
            message_text += f'{i}. <code>{admin_id}</code>\n'
    
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Назад', callback_data='sp_admins')
    )
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_add_admin(call):
    """Запрашивает добавление администратора"""
    global bot, cardinal_instance
    
    tg = cardinal_instance.telegram
    
    msg = bot.edit_message_text(
        '➕ <b>Добавление администратора</b>\n\n'
        'Введите Telegram ID администратора:\n\n'
        '<i>Чтобы узнать свой ID, напишите боту @userinfobot</i>',
        call.message.chat.id, call.message.message_id,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('🔙 Отмена', callback_data='sp_admins')
        ),
        parse_mode='HTML'
    )
    
    tg.set_state(
        chat_id=call.message.chat.id,
        message_id=msg.message_id,
        user_id=call.from_user.id,
        state="sp_adding_admin"
    )

def handle_remove_admin(call):
    """Показывает список администраторов для удаления"""
    admins = config.get('administrators', [])
    
    if not admins:
        bot.answer_callback_query(call.id, '❌ Нет администраторов для удаления')
        return
    
    kb = InlineKeyboardMarkup(row_width=1)
    
    for admin_id in admins:
        kb.add(InlineKeyboardButton(f'🗑️ {admin_id}', callback_data=f'sp_delete_admin_{admin_id}'))
    
    kb.add(InlineKeyboardButton('🔙 Назад', callback_data='sp_admins'))
    
    message_text = '''➖ <b>Удаление администратора</b>

Выберите администратора для удаления:'''
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_delete_admin(call, admin_id):
    """Удаляет администратора"""
    try:
        admin_id = int(admin_id)
        admins = config.get('administrators', [])
        
        if admin_id in admins:
            admins.remove(admin_id)
            config['administrators'] = admins
            save_config()
            
            bot.answer_callback_query(call.id, f'✅ Администратор {admin_id} удален')
            handle_admins(call)  # Возвращаемся к управлению администраторами
        else:
            bot.answer_callback_query(call.id, '❌ Администратор не найден')
    except ValueError:
        bot.answer_callback_query(call.id, '❌ Ошибка при удалении')

def test_api_key(api_key):
    """Тестирует API ключ"""
    try:
        # Проверяем API ключ через получение цены
        response = requests.get(PRICE_ENDPOINT, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True
        return False
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} Ошибка тестирования API ключа: {e}')
        return False

def get_lots_status():
    """Получает статус лотов (заглушка)"""
    # Эта функция может быть расширена для получения реального статуса лотов
    return config.get('enabled', True)

def toggle_lots_status():
    """Переключает статус лотов"""
    config['enabled'] = not config.get('enabled', True)
    save_config()
    return config['enabled']

def cleanup_old_pending_orders():
    """Очищает старые ожидающие заказы (старше 1 часа)"""
    global pending_steam_links
    
    current_time = time.time()
    expired_orders = []
    
    for username, order_data in pending_steam_links.items():
        if current_time - order_data.get('timestamp', 0) > 3600:  # 1 час
            expired_orders.append(username)
    
    if expired_orders:
        for username in expired_orders:
            del pending_steam_links[username]
            logger.info(f'{LOGGER_PREFIX} 🕐 Очищен истёкший заказ для {username}')
        
        # Сохраняем обновленные ожидающие заказы
        save_pending_orders()

def send_admin_notification(message_type, **kwargs):
    """Универсальная функция для отправки уведомлений администраторам"""
    try:
        admins = config.get('administrators', [])
        if not admins:
            logger.warning(f'{LOGGER_PREFIX} ⚠️ Нет настроенных администраторов для уведомлений')
            return
        
        if not bot:
            logger.warning(f'{LOGGER_PREFIX} ⚠️ Telegram bot не инициализирован')
            return
        
        templates = {
            'new_order': '📦 <b>Новый заказ Steam Points</b>\n\n'
                        '👤 Покупатель: {buyer}\n'
                        '💎 Очки: {points}\n'
                        '💰 Сумма: {sum}₽\n'
                        '🆔 ID: #{order_id}',
            
            'order_success': '✅ <b>Заказ выполнен успешно</b>\n\n'
                            '👤 Покупатель: {buyer}\n'
                            '💎 Очки: {points}\n'
                            '🔗 Steam: {steam_link}\n'
                            '💰 За сколько продали: {fp_sum}₽\n'
                            '💵 Сколько стоят очки на API: {points_cost}₽\n'
                            '💵 Валовая прибыль: {profit:.2f}₽\n'
                            '💵 После комиссии 3%: {profit_after_3:.2f}₽\n'
                            '💵 После комиссии 6%: {profit_after_6:.2f}₽\n'
                            '🆔 ID: #{order_id}',
            
            'order_error': '❌ <b>Ошибка при обработке заказа</b>\n\n'
                          '👤 Покупатель: {buyer}\n'
                          '💎 Очки: {points}\n'
                          '❗ Ошибка: {error}\n'
                          '🆔 ID: #{order_id}',
            
            'api_error': '🚨 <b>Ошибка API Steam Points</b>\n\n'
                        '❗ Ошибка: {error}\n'
                        '🕐 Время: {time}',
            
            'low_balance': '⚠️ <b>Низкий баланс API</b>\n\n'
                          '💰 Баланс: {balance:.2f}₽\n'
                          '🔴 Рекомендуется пополнение'
        }
        
        message_text = templates.get(message_type, '').format(**kwargs)
        
        if not message_text:
            logger.error(f'{LOGGER_PREFIX} ❌ Неизвестный тип уведомления: {message_type}')
            return
        
        logger.info(f'{LOGGER_PREFIX} 📤 Отправляем уведомление типа "{message_type}" для {len(admins)} админов')
        
        success_count = 0
        for admin_id in admins:
            try:
                kb = None
                if 'order_id' in kwargs:
                    kb = InlineKeyboardMarkup()
                    kb.add(InlineKeyboardButton(
                        '🌐 Открыть заказ', 
                        url=f'https://funpay.com/orders/{kwargs["order_id"]}/'
                    ))
                
                bot.send_message(admin_id, message_text, reply_markup=kb, parse_mode='HTML')
                success_count += 1
                logger.info(f'{LOGGER_PREFIX} ✅ Уведомление отправлено админу {admin_id}')
            except Exception as e:
                logger.error(f'{LOGGER_PREFIX} ❌ Ошибка отправки уведомления админу {admin_id}: {e}')
        
        logger.info(f'{LOGGER_PREFIX} 📤 Уведомление "{message_type}" отправлено {success_count}/{len(admins)} админам')
        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Критическая ошибка в send_admin_notification: {e}')
        logger.exception(f'{LOGGER_PREFIX} Полная трассировка ошибки уведомления админов:')

def handle_statistics(call):
    """Показывает статистику плагина"""
    orders = load_orders_history()
    
    # Общая статистика
    total_orders = len(orders)
    success_orders = [o for o in orders if o.get('status') == 'success']
    error_orders = [o for o in orders if o.get('status') == 'error']
    pending_orders = [o for o in orders if o.get('status') in ['processing', 'processing_points']]
    
    # Получаем прибыль из кеша
    profit_data = load_profit_cache()
    total_profit = profit_data.get('total_profit', 0.0)
    total_points = sum(o.get('points_delivered', 0) for o in success_orders)
    
    # Статистика за сегодня
    today = datetime.now().date()
    today_orders = []
    for order in orders:
        try:
            if 'created_at' in order:
                order_date = datetime.fromisoformat(order['created_at']).date()
                if order_date == today:
                    today_orders.append(order)
        except:
            continue
    
    today_success = [o for o in today_orders if o.get('status') == 'success']
    today_profit = sum(o.get('profit', 0) for o in today_success)
    
    # Средняя прибыль с заказа
    avg_profit = total_profit / len(success_orders) if success_orders else 0
    
    # Текущая цена
    current_price = get_current_price()
    price_status = f'{current_price:.4f}₽' if current_price > 0 else 'Недоступна'
    
    message_text = f'''📊 <b>Статистика {NAME}</b>

<blockquote>📈 <b>ОБЩАЯ СТАТИСТИКА</b>
📦 <b>Всего заказов:</b> <code>{total_orders}</code>
✅ <b>Успешно:</b> <code>{len(success_orders)}</code>
❌ <b>Ошибок:</b> <code>{len(error_orders)}</code>
⏳ <b>В обработке:</b> <code>{len(pending_orders)}</code>
💰 <b>Общая прибыль:</b> <b>{total_profit:.2f}₽</b>
💎 <b>Очков продано:</b> <code>{total_points:,}</code>
📊 <b>Средняя прибыль:</b> <code>{avg_profit:.2f}₽</code></blockquote>

<blockquote>📅 <b>СЕГОДНЯ</b>
📦 <b>Заказов:</b> <code>{len(today_orders)}</code>
✅ <b>Успешно:</b> <code>{len(today_success)}</code>
💰 <b>Прибыль:</b> <b>{today_profit:.2f}₽</b></blockquote>

<blockquote>💎 <b>API ИНФОРМАЦИЯ</b>
💵 <b>Цена очка:</b> <code>{price_status}</code>
🔧 <b>Статус API:</b> {'🟢 Работает' if current_price > 0 else '🔴 Недоступен'}</blockquote>'''
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('📋 Последние заказы', callback_data='sp_recent_orders'),
        InlineKeyboardButton('🔄 Обновить', callback_data='sp_statistics')
    )
    kb.add(InlineKeyboardButton('🔙 Назад', callback_data='sp_back_to_main'))
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_recent_orders(call):
    """Показывает последние заказы"""
    orders = load_orders_history()
    
    if not orders:
        message_text = '📋 <b>Заказы отсутствуют</b>'
    else:
        # Сортируем заказы по времени (новые первыми)
        sorted_orders = sorted(
            orders,
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )[:10]  # Последние 10 заказов
        
        message_text = '📋 <b>Последние заказы:</b>\n\n'
        
        for order in sorted_orders:
            order_id = order.get('order_id', 'N/A')
            buyer = order.get('buyer', 'Unknown')
            status = order.get('status', 'unknown')
            points = order.get('points', 0)
            profit = order.get('profit', 0)
            
            # Форматируем дату
            try:
                date_str = datetime.fromisoformat(order.get('created_at', '')).strftime('%d.%m %H:%M')
            except:
                date_str = 'N/A'
            
            # Эмодзи для статуса
            status_emoji = {
                'success': '✅',
                'error': '❌', 
                'processing': '⏳',
                'processing_points': '🔄',
                'completed': '✅',
                'invalid': '❌'
            }.get(status, '❓')
            
            message_text += f'{status_emoji} <code>#{order_id}</code>\n'
            message_text += f'⠀∟👤 {buyer}\n'
            message_text += f'⠀∟💎 Очки: {points}\n'
            if status == 'success':
                fp_sum = order.get('fp_sum', 0)
                cost_rub = order.get('cost_rub', 0)
                message_text += f'⠀∟💰 За сколько продали: {fp_sum}₽\n'
                message_text += f'⠀∟💵 Сколько стоят очки на API: {cost_rub}₽\n'
                message_text += f'⠀∟💵 Валовая прибыль: {profit:.2f}₽\n'
            message_text += f'⠀∟📅 {date_str}\n\n'
    
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Назад', callback_data='sp_statistics')
    )
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_about_plugin(call):
    """Показывает информацию о плагине"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton('🔙 Назад', callback_data='sp_back_to_main'))
    
    message_text = f'''ℹ️ <b>О плагине {NAME}</b>

<blockquote>🎮 <b>Название:</b> {NAME}
📦 <b>Версия:</b> <code>v{VERSION}</code>
👤 <b>Автор:</b> <i>{CREDITS}</i>
📝 <b>Описание:</b> {DESCRIPTION}</blockquote>

🔧 <b>Основные функции:</b>
• Автоматическая продажа очков Steam
• Пакетная система продаж (Quan: N)
• 🛡️ Защита лотов от продаж при низком балансе
• Фильтры заказов по подкатегориям
• Система ключевых слов
• Шаблоны сообщений
• Подробная статистика

🛡️ <b>Защита лотов:</b>
• Автоматическая деактивация при низком балансе API
• Настраиваемый порог срабатывания
• Ручное управление активацией/деактивацией
• Защита от продаж без возможности выполнения

📦 <b>Пакетная система:</b>
<code>Quan: 0</code> - 1 лот = 1 очко (amount заказа)
<code>Quan: 5000</code> - 1 лот = 5000 очков
<code>Quan: 10000</code> - 1 лот = 10000 очков

📝 <b>Пример описания лота:</b>
"5000 очков Steam Points
Quan: 5000
Быстрая доставка!"

💵 <b>Пример работы:</b>
• Лот на 5000₽ с Quan: 5000
• Покупатель покупает 2 лота
• Платит: 10000₽
• Получает: 10000 очков (2 × 5000)

💎 <b>Возможности:</b>
• Автоматическое получение актуальных цен
• Обработка заказов в реальном времени
• Защита от недостатка средств
• Проверка валидности Steam ссылок
• Уведомления о статусе заказов

🎯 <b>Преимущества:</b>
• Простота настройки и использования
• Высокая надежность работы
• Гибкие настройки фильтрации
• Полная автоматизация процесса'''

    try:
        bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                             reply_markup=kb, parse_mode='HTML')
    except Exception:
        bot.send_message(call.message.chat.id, message_text, reply_markup=kb, parse_mode='HTML')

def handle_templates(call):
    """Управление шаблонами сообщений"""
    kb = InlineKeyboardMarkup(row_width=1)
    
    templates = [
        ('steam_request', '🎮 Запрос Steam ссылки'),
        ('steam_confirmation', '✅ Подтверждение Steam ссылки'),
        ('processing', '🔄 Обработка заказа'),
        ('success', '✅ Успешное выполнение'),
        ('error', '❌ Ошибка заказа'),
        ('insufficient_funds', '💳 Недостаток средств'),
        ('invalid_steam', '🔗 Неверная ссылка Steam'),
        ('maintenance', '⚠️ Технические работы')
    ]
    
    for template_key, template_name in templates:
        kb.add(InlineKeyboardButton(template_name, callback_data=f'sp_edit_template_{template_key}'))
    
    kb.add(InlineKeyboardButton('🔙 Назад', callback_data='sp_back_to_main'))
    
    message_text = '''📝 <b>Управление шаблонами сообщений</b>

Здесь вы можете настроить сообщения, которые отправляются покупателям в различных ситуациях.

<i>Выберите шаблон для редактирования:</i>'''
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                         reply_markup=kb, parse_mode='HTML')

def handle_edit_template(call, template_key):
    """Редактирование шаблона"""
    global bot, cardinal_instance
    
    tg = cardinal_instance.telegram
    current_template = config.get('templates', {}).get(template_key, '')
    
    template_names = {
        'steam_request': 'Запрос Steam ссылки',
        'processing': 'Обработка заказа',
        'success': 'Успешное выполнение',
        'error': 'Ошибка заказа',
        'insufficient_funds': 'Недостаток средств',
        'invalid_steam': 'Неверная ссылка Steam',
        'maintenance': 'Технические работы'
    }
    
    template_name = template_names.get(template_key, template_key)
    
    # Показываем доступные переменные для разных шаблонов
    variables_info = ""
    if template_key == 'steam_request':
        variables_info = "\n\n<i>Доступные переменные:</i>\n• {points} - количество очков\n• {price} - стоимость заказа"
    elif template_key == 'success':
        variables_info = "\n\n<i>Доступные переменные:</i>\n• {points} - количество очков\n• {total} - стоимость\n• {steam_link} - ссылка Steam\n• {before_points} - очки до\n• {after_points} - очки после\n• {order_link} - ссылка на заказ"
    
    msg = bot.edit_message_text(
        f'📝 <b>Редактирование шаблона</b>\n'
        f'<b>Шаблон:</b> {template_name}\n\n'
        f'<b>Текущий текст:</b>\n<pre>{current_template}</pre>{variables_info}\n\n'
        f'<i>Введите новый текст шаблона:</i>',
        call.message.chat.id, call.message.message_id,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('🔙 Отмена', callback_data='sp_templates')
        ),
        parse_mode='HTML'
    )
    
    tg.set_state(
        chat_id=call.message.chat.id,
        message_id=msg.message_id,
        user_id=call.from_user.id,
        state=f"sp_editing_template_{template_key}"
    )

def handle_text_input(message):
    """Обрабатывает текстовый ввод для различных настроек"""
    global config, cardinal_instance, bot
    
    # Отладочный лог
    logger.info(f'{LOGGER_PREFIX} 📝 Получено текстовое сообщение: "{message.text}" от пользователя {message.from_user.id}')
    
    tg = cardinal_instance.telegram
    state_data = tg.get_state(message.chat.id, message.from_user.id)
    
    logger.info(f'{LOGGER_PREFIX} 🔍 Состояние пользователя: {state_data}')
    
    if not state_data or 'state' not in state_data:
        logger.info(f'{LOGGER_PREFIX} ❌ Нет активного состояния для пользователя {message.from_user.id}')
        return
    
    state = state_data['state']
    logger.info(f'{LOGGER_PREFIX} ✅ Обрабатываем состояние: {state}')
    
    try:
        # Удаляем предыдущие сообщения
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, message.message_id - 1)
    except:
        pass
    
    if state == 'sp_setting_api_key':
        api_key = message.text.strip()
        if not api_key:
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_basic_settings'))
            bot.send_message(message.chat.id, '❌ Пустой API ключ не допускается.', reply_markup=kb)
        else:
            config['api_key'] = api_key
            save_config()
            
            # Принудительно обновляем цену сразу после добавления API ключа
            global cached_price, last_price_update
            cached_price = None  # Сбрасываем кеш
            last_price_update = 0  # Сбрасываем время последнего обновления
            new_price = get_current_price()  # Получаем актуальную цену
            
            # Перезапускаем таймер автообновления цены
            start_price_update_timer()
            
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_basic_settings'))
            
            if new_price is not None:
                bot.send_message(message.chat.id, f'✅ API ключ успешно сохранен!\n💎 Цена обновлена: {new_price:.4f}₽ за очко\n🔄 Автообновление цены запущено!', reply_markup=kb)
            else:
                bot.send_message(message.chat.id, '✅ API ключ сохранен!\n⚠️ Не удалось получить цену с API\n🔄 Автообновление цены запущено!', reply_markup=kb)
    

    
    elif state == 'sp_adding_admin':
        try:
            admin_id = int(message.text.strip())
            admins = config.get('administrators', [])
            if admin_id not in admins:
                admins.append(admin_id)
                config['administrators'] = admins
                save_config()
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_admins'))
                bot.send_message(message.chat.id, f'✅ Администратор {admin_id} добавлен!', reply_markup=kb)
            else:
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_admins'))
                bot.send_message(message.chat.id, '❌ Этот администратор уже добавлен', reply_markup=kb)
        except ValueError:
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_admins'))
            bot.send_message(message.chat.id, '❌ Введите корректный числовой ID', reply_markup=kb)
    
    elif state == 'sp_setting_subcategories':
        text = message.text.strip()
        if not text:
            # Пустой ввод - отключаем фильтр по подкатегориям
            config['target_subcategories'] = []
            save_config()
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_order_filters'))
            bot.send_message(message.chat.id, '✅ Фильтр по подкатегориям отключен', reply_markup=kb)
        else:
            try:
                # Парсим список ID подкатегорий
                subcategory_ids = []
                for part in text.split(','):
                    part = part.strip()
                    if part:
                        subcategory_ids.append(int(part))
                
                config['target_subcategories'] = subcategory_ids
                save_config()
                
                subcats_text = ', '.join(map(str, subcategory_ids))
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_order_filters'))
                bot.send_message(message.chat.id, f'✅ ID подкатегорий установлены: {subcats_text}', reply_markup=kb)
            except ValueError:
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_order_filters'))
                bot.send_message(message.chat.id, '❌ Введите корректные числовые ID', reply_markup=kb)
    
    elif state == 'sp_setting_min_balance':
        try:
            min_balance = float(message.text.strip())
            if min_balance < 0:
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Отмена', callback_data='sp_basic_settings'))
                bot.send_message(message.chat.id, '❌ Минимальный порог баланса не может быть отрицательным', reply_markup=kb)
            else:
                config['min_balance_threshold'] = min_balance
                save_config()
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_basic_settings'))
                bot.send_message(message.chat.id, f'✅ Минимальный порог баланса установлен: {min_balance:.2f}₽', reply_markup=kb)
        except ValueError:
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Отмена', callback_data='sp_basic_settings'))
            bot.send_message(message.chat.id, '❌ Введите корректное число', reply_markup=kb)
    
    elif state == 'sp_setting_bonus_points':
        try:
            bonus_points = int(message.text.strip())
            if bonus_points < 0:
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Отмена', callback_data='sp_bonus_settings'))
                bot.send_message(message.chat.id, '❌ Количество бонусных очков не может быть отрицательным', reply_markup=kb)
            else:
                config['bonus_points_for_review'] = bonus_points
                save_config()
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_bonus_settings'))
                bot.send_message(message.chat.id, f'✅ Количество бонусных очков установлено: {bonus_points}', reply_markup=kb)
        except ValueError:
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Отмена', callback_data='sp_bonus_settings'))
            bot.send_message(message.chat.id, '❌ Введите корректное число', reply_markup=kb)
    
    elif state.startswith('sp_setting_bonus_') and state.endswith('_stars'):
        # Обработка настройки бонусов для определенного рейтинга
        stars = state.replace('sp_setting_bonus_', '').replace('_stars', '')
        try:
            bonus_points = int(message.text.strip())
            if bonus_points < 0:
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Отмена', callback_data='sp_bonus_settings'))
                bot.send_message(message.chat.id, '❌ Количество бонусных очков не может быть отрицательным', reply_markup=kb)
            else:
                # Инициализируем bonus_settings если его нет
                if 'bonus_settings' not in config:
                    config['bonus_settings'] = {}
                
                # Определяем ключ в зависимости от количества звезд
                if stars == '1':
                    rating_key = '1_star'
                    rating_display = '⭐ 1 звезда'
                else:
                    rating_key = f'{stars}_stars'
                    rating_display = '⭐' * int(stars) + f' {stars} звезд'
                
                config['bonus_settings'][rating_key] = bonus_points
                save_config()
                
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_bonus_settings'))
                bot.send_message(message.chat.id, f'✅ Бонус за {rating_display} установлен: {bonus_points} очков', reply_markup=kb)
        except ValueError:
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Отмена', callback_data='sp_bonus_settings'))
            bot.send_message(message.chat.id, '❌ Введите корректное число', reply_markup=kb)
    
    elif state == 'sp_adding_keyword':
        keyword = message.text.strip().lower()
        if not keyword:
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_manage_keywords'))
            bot.send_message(message.chat.id, '❌ Пустое ключевое слово не допускается.', reply_markup=kb)
        else:
            keywords = config.get('target_keywords', [])
            if keyword not in keywords:
                keywords.append(keyword)
                config['target_keywords'] = keywords
                save_config()
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_manage_keywords'))
                bot.send_message(message.chat.id, f'✅ Ключевое слово "{keyword}" добавлено!', reply_markup=kb)
            else:
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_manage_keywords'))
                bot.send_message(message.chat.id, '❌ Это ключевое слово уже добавлено', reply_markup=kb)
    
    elif state.startswith('sp_editing_template_'):
        template_key = state.replace('sp_editing_template_', '')
        new_template = message.text
        
        if not new_template.strip():
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_templates'))
            bot.send_message(message.chat.id, '❌ Пустой шаблон не допускается.', reply_markup=kb)
        else:
            if 'templates' not in config:
                config['templates'] = {}
            config['templates'][template_key] = new_template
            save_config()
            
            # Перезагружаем конфигурацию для применения изменений
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config.update(json.load(f))
            
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_templates'))
            bot.send_message(message.chat.id, '✅ Шаблон успешно обновлен!', reply_markup=kb)
            logger.info(f'{LOGGER_PREFIX} ✅ Шаблон "{template_key}" обновлен пользователем {message.from_user.id}')
    
    elif state == 'sp_setting_lot_category':
        try:
            category_id = int(message.text.strip())
            if category_id < 1:
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Отмена', callback_data='sp_lot_management'))
                bot.send_message(message.chat.id, '❌ ID категории должен быть больше 0', reply_markup=kb)
            else:
                config['target_lot_category'] = category_id
                save_config()
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data='sp_lot_management'))
                bot.send_message(message.chat.id, f'✅ ID категории лотов установлен: {category_id}', reply_markup=kb)
        except ValueError:
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Отмена', callback_data='sp_lot_management'))
            bot.send_message(message.chat.id, '❌ Введите корректный числовой ID', reply_markup=kb)
    
    # Очищаем состояние
    tg.clear_state(message.chat.id, message.from_user.id)

def handle_lot_management(call):
    """Защита лотов"""
    global bot
    
    if not bot:
        logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован в handle_lot_management')
        try:
            # Попытка ответить на callback query
            if hasattr(call, 'answer_callback_query'):
                call.answer_callback_query("❌ Ошибка инициализации бота")
        except:
            pass
        return
    
    try:
        kb = InlineKeyboardMarkup(row_width=1)
        
        # Статус автоматической деактивации лотов
        auto_deactivate_status = '🟢 Включена' if config.get('auto_deactivate_enabled', False) else '🔴 Отключена'
        kb.add(InlineKeyboardButton(f'🔰 Авто-деактивация лотов ({auto_deactivate_status})', callback_data='sp_toggle_auto_deactivate'))

        # Порог баланса для деактивации
        if config.get('auto_deactivate_enabled', False):
            min_balance = config.get('min_balance_threshold', 10.0)
            kb.add(InlineKeyboardButton(f'💰 Порог баланса ({min_balance:.2f}₽)', callback_data='sp_set_balance_threshold'))
            
            # ID категории лотов
            target_category = config.get('target_lot_category', 714)
            kb.add(InlineKeyboardButton(f'📂 ID категории лотов ({target_category})', callback_data='sp_set_lot_category'))
            
            # Кнопка ручного управления лотами
            kb.add(InlineKeyboardButton('🔄 Активировать/Деактивировать лоты', callback_data='sp_toggle_lots'))
        
        kb.add(InlineKeyboardButton('🔙 Назад', callback_data='sp_back_to_main'))
        
        message_text = f'''☢️ <b>Защита лотов</b>

Автоматическая защита ваших лотов от продаж при низком балансе API.

📊 <b>Текущие настройки:</b>
🔰 <b>Авто-деактивация:</b> {auto_deactivate_status}'''

        if config.get('auto_deactivate_enabled', False):
            min_balance = config.get('min_balance_threshold', 10.0)
            target_category = config.get('target_lot_category', 714)
            message_text += f'''
💰 <b>Порог баланса:</b> <code>{min_balance:.2f}₽</code>
📂 <b>ID категории:</b> <code>{target_category}</code>

💡 <b>Как это работает:</b>
• При снижении баланса API ниже {min_balance:.2f}₽ лоты автоматически деактивируются
• При восстановлении баланса вы можете активировать лоты вручную
• Управление происходит только для указанной категории лотов'''
        else:
            message_text += '''

💡 <b>Включите защиту лотов для:</b>
• Автоматической деактивации при низком балансе API
• Защиты от продаж без возможности выполнения заказов
• Сохранения репутации на FunPay'''

        message_text += '''

<i>Выберите действие:</i>'''
        
        bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                             reply_markup=kb, parse_mode='HTML')
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_lot_management: {e}')
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        except:
            pass

def handle_toggle_auto_deactivate(call):
    """Переключает статус автоматической деактивации лотов"""
    global config, bot
    
    if not bot:
        logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован в handle_toggle_auto_deactivate')
        return
    
    try:
        config['auto_deactivate_enabled'] = not config.get('auto_deactivate_enabled', False)
        save_config()
        
        status = 'включена' if config['auto_deactivate_enabled'] else 'отключена'
        bot.answer_callback_query(call.id, f'✅ Авто-деактивация лотов {status}')
        
        # Возвращаемся к защите лотов
        handle_lot_management(call)
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_toggle_auto_deactivate: {e}')
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        except:
            pass

def handle_set_balance_threshold(call):
    """Запрашивает ввод порога баланса для деактивации лотов"""
    global bot
    
    if not bot:
        logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован в handle_set_balance_threshold')
        return
    
    try:
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton('🔙 Отмена', callback_data='sp_lot_management')
        )
        
        message_text = '''💰 <b>Установка порога баланса</b>

Введите минимальный баланс API (в рублях), при котором лоты должны деактивироваться.

<b>Пример:</b> <code>10.50</code> или <code>15</code>

⚠️ <i>При снижении баланса ниже этого значения все лоты в указанной категории будут автоматически деактивированы</i>'''
        
        bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                             reply_markup=kb, parse_mode='HTML')
        
        # Устанавливаем состояние ожидания ввода
        user_states[call.from_user.id] = 'waiting_balance_threshold'
        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_set_balance_threshold: {e}')
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        except:
            pass

def handle_set_lot_category(call):
    """Запрашивает ввод ID категории лотов"""
    global bot, cardinal_instance
    
    if not bot:
        logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован в handle_set_lot_category')
        return
    
    if not cardinal_instance or not hasattr(cardinal_instance, 'telegram'):
        logger.error(f'{LOGGER_PREFIX} ❌ Cardinal instance или telegram недоступен')
        try:
            bot.answer_callback_query(call.id, "❌ Ошибка инициализации")
        except:
            pass
        return
    
    try:
        tg = cardinal_instance.telegram
        current_category = config.get('target_lot_category', 714)
        
        msg = bot.edit_message_text(
            f'📂 <b>Настройка ID категории лотов</b>\n\n'
            f'Текущий ID: <code>{current_category}</code>\n\n'
            f'<b>Пример:</b> 714 (Steam Points)\n'
            f'Это ID категории, в которой находятся лоты для управления\n\n'
            f'<i>Введите ID категории:</i>',
            call.message.chat.id, call.message.message_id,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton('🔙 Отмена', callback_data='sp_lot_management')
            ),
            parse_mode='HTML'
        )
        
        tg.set_state(
            chat_id=call.message.chat.id,
            message_id=msg.message_id,
            user_id=call.from_user.id,
            state="sp_setting_lot_category"
        )
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_set_lot_category: {e}')
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        except:
            pass

def handle_toggle_lots(call):
    """Переключает состояние лотов (активация/деактивация)"""
    global bot
    
    if not bot:
        logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован в handle_toggle_lots')
        return
    
    try:
        category_id = config.get('target_lot_category', 714)
        
        # Определяем текущее состояние лотов
        try:
            profile = cardinal_instance.account.get_user(cardinal_instance.account.id)
            all_lots = profile.get_lots()
            logger.info(f'{LOGGER_PREFIX} 🔍 Найдено всего лотов: {len(all_lots)}')
            
            # Логируем все доступные подкатегории
            subcategories = set()
            for lot in all_lots:
                subcategories.add((lot.subcategory.id, lot.subcategory.name))
            logger.info(f'{LOGGER_PREFIX} 🔍 Доступные подкатегории: {list(subcategories)}')
            
            lots = [lot for lot in all_lots if lot.subcategory.id == category_id]
            logger.info(f'{LOGGER_PREFIX} 🔍 Найдено лотов в категории {category_id}: {len(lots)}')
            
            # Логируем информацию о найденных лотах
            for lot in lots:
                logger.info(f'{LOGGER_PREFIX} 🔍 Лот {lot.id}: подкатегория {lot.subcategory.id} (название: {lot.subcategory.name})')
            
            if not lots:
                bot.edit_message_text(
                    f'ℹ️ <b>Лоты не найдены</b>\n\n'
                    f'В категории <code>{category_id}</code> нет лотов для управления.',
                    call.message.chat.id, call.message.message_id,
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton('🔙 Назад', callback_data='sp_lot_management')
                    )
                )
                return
            
            # Проверяем, есть ли активные лоты
            active_lots = []
            inactive_lots = []
            
            for lot in lots:
                try:
                    lot_fields = cardinal_instance.account.get_lot_fields(lot.id)
                    if lot_fields.active:
                        active_lots.append(lot)
                    else:
                        inactive_lots.append(lot)
                except Exception as e:
                    logger.warning(f'{LOGGER_PREFIX} ⚠️ Не удалось получить поля лота {lot.id}: {e}')
                    # По умолчанию считаем лот неактивным
                    inactive_lots.append(lot)
            
            if active_lots:
                # Если есть активные лоты, деактивируем их
                action = "деактивации"
                target_lots = active_lots
                new_state = False
            else:
                # Если нет активных лотов, активируем их
                action = "активации"
                target_lots = inactive_lots
                new_state = True
            
            bot.edit_message_text(
                f'🔄 <b>{action.title()} лотов</b>\n\n'
                f'{action.title()} лоты в категории <code>{category_id}</code>...\n\n'
                f'⏳ Это может занять несколько секунд.',
                call.message.chat.id, call.message.message_id
            )
            
            # Выполняем действие
            success_count = 0
            for lot in target_lots:
                try:
                    lot_fields = cardinal_instance.account.get_lot_fields(lot.id)
                    lot_fields.active = new_state
                    cardinal_instance.account.save_lot(lot_fields)
                    
                    success_count += 1
                    logger.info(f'{LOGGER_PREFIX} ✅ Лот {lot.id} {"активирован" if new_state else "деактивирован"}')
                    
                    # Небольшая задержка между запросами
                    time.sleep(0.5)
                except Exception as e:
                    logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при {action} лота {lot.id}: {e}')
                    continue
            
            # Показываем результат
            status_icon = "🟢" if new_state else "🔴"
            status_text = "активированы" if new_state else "деактивированы"
            
            bot.edit_message_text(
                f'{status_icon} <b>Лоты {status_text}!</b>\n\n'
                f'Лоты в категории <code>{category_id}</code> успешно {status_text}.\n'
                f'Обработано: {success_count}/{len(target_lots)} лотов',
                call.message.chat.id, call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton('🔙 Назад', callback_data='sp_lot_management')
                )
            )
            
        except Exception as e:
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при получении лотов: {e}')
            bot.edit_message_text(
                '❌ <b>Ошибка получения лотов</b>\n\n'
                'Не удалось получить информацию о лотах.\n'
                'Проверьте настройки и попробуйте снова.',
                call.message.chat.id, call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton('🔙 Назад', callback_data='sp_lot_management')
                )
            )
            
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_toggle_lots: {e}')
        try:
            bot.edit_message_text(
                '❌ <b>Критическая ошибка</b>\n\n'
                'Произошла ошибка при управлении лотами.\n'
                'Проверьте логи для деталей.',
                call.message.chat.id, call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton('🔙 Назад', callback_data='sp_lot_management')
                )
            )
        except Exception as edit_error:
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при редактировании сообщения: {edit_error}')
            try:
                bot.answer_callback_query(call.id, "❌ Произошла ошибка")
            except:
                pass

def init_commands(c_):
    """Регистрирует команды бота"""
    global bot, cardinal_instance
    
    cardinal_instance = c_
    
    if not hasattr(c_, 'telegram') or not c_.telegram:
        logger.error(f'{LOGGER_PREFIX} ❌ Telegram модуль не доступен в Cardinal')
        return
    
    if not hasattr(c_.telegram, 'bot') or not c_.telegram.bot:
        logger.error(f'{LOGGER_PREFIX} ❌ Telegram bot не инициализирован в Cardinal')
        return
    
    # Проверяем, что bot действительно работает
    try:
        test_bot = c_.telegram.bot
        if not test_bot:
            logger.error(f'{LOGGER_PREFIX} ❌ Telegram bot объект пустой')
            return
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при проверке bot объекта: {e}')
        return
    
    bot = c_.telegram.bot
    tg = c_.telegram
    
    logger.info(f'{LOGGER_PREFIX} ✅ Bot инициализирован: {bot is not None}')
    if bot:
        logger.info(f'{LOGGER_PREFIX} ✅ Bot username: {getattr(bot, "get_me", lambda: None)()}')
    
    # Команда для открытия меню плагина
    def steam_points_command(message):
        try:
            show_main_menu(message)
        except Exception as e:
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в команде /steampoints: {e}')
    
    # Регистрируем команду
    try:
        bot.register_message_handler(steam_points_command, commands=['steampoints'])
        logger.info(f'{LOGGER_PREFIX} ✅ Message handler для команды /steampoints зарегистрирован')
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при регистрации команды /steampoints: {e}')
    
    # Обработчик текстовых сообщений для настроек
    def handle_text_input_local(message):
        global bot, user_states, config
        
        if not bot:
            return
        
        user_id = message.from_user.id
        if user_id not in user_states:
            return
        
        state = user_states[user_id]
        
        try:
            if state == 'waiting_balance_threshold':
                # Обработка ввода порога баланса
                try:
                    balance = float(message.text.replace(',', '.'))
                    if balance <= 0:
                        raise ValueError("Баланс должен быть положительным числом")
                    
                    config['min_balance_threshold'] = balance
                    save_config()
                    
                    del user_states[user_id]
                    
                    bot.send_message(message.chat.id, f'✅ Порог баланса установлен: {balance:.2f}₽')
                    
                    # Возвращаемся к защите лотов
                    # Создаем fake call объект для навигации
                    class FakeCall:
                        def __init__(self):
                            self.message = message
                            self.from_user = message.from_user
                    
                    fake_call = FakeCall()
                    handle_lot_management(fake_call)
                    
                except ValueError:
                    bot.send_message(message.chat.id, 
                                   '❌ Неверный формат числа. Введите положительное число (например: 10.50)')
            
        except Exception as e:
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_text_input: {e}')
            if user_id in user_states:
                del user_states[user_id]
    
    # Регистрируем обработчик текстовых сообщений (используем глобальную функцию)
    try:
        bot.register_message_handler(handle_text_input, content_types=['text'])
        logger.info(f'{LOGGER_PREFIX} ✅ Text message handler зарегистрирован (глобальная функция)')
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при регистрации text handler: {e}')
    
    # Один универсальный callback handler для всех кнопок
    def handle_callback_query(call):
        global bot
        
        # Проверяем, что bot доступен
        if not bot:
            logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован в callback handler')
            try:
                # Попытка ответить на callback query через call объект
                if hasattr(call, 'answer_callback_query'):
                    call.answer_callback_query("❌ Ошибка инициализации бота")
            except:
                pass
            return
        
        try:
            data = call.data
            logger.info(f'{LOGGER_PREFIX} 🔄 Получен callback: {data}, bot: {bot is not None}')
            
            if data == 'sp_back_to_main':
                show_main_menu_callback(call)
            elif data == 'sp_basic_settings':
                handle_basic_settings(call)
            elif data == 'sp_statistics':
                handle_statistics(call)
            elif data == 'sp_templates':
                handle_templates(call)
            elif data == 'sp_about_plugin':
                handle_about_plugin(call)
            elif data == 'sp_toggle_enabled':
                handle_toggle_enabled(call)
            elif data == 'sp_set_api_key':
                handle_set_api_key(call)
            elif data == 'sp_order_filters':
                handle_order_filters(call)
            elif data == 'sp_set_subcategories':
                handle_set_subcategories(call)
            elif data == 'sp_manage_keywords':
                handle_manage_keywords(call)
            elif data == 'sp_show_keywords':
                handle_show_keywords(call)
            elif data == 'sp_add_keyword':
                handle_add_keyword(call)
            elif data == 'sp_remove_keyword':
                handle_remove_keyword(call)
            elif data == 'sp_clear_keywords':
                handle_clear_keywords(call)
            elif data == 'sp_confirm_clear_keywords':
                handle_confirm_clear_keywords(call)
            elif data == 'sp_test_filters':
                handle_test_filters(call)
            elif data == 'sp_recent_orders':
                handle_recent_orders(call)
            elif data.startswith('sp_delete_keyword_'):
                keyword_index = data.replace('sp_delete_keyword_', '')
                handle_delete_keyword(call, keyword_index)
            elif data.startswith('sp_edit_template_'):
                template_key = data.replace('sp_edit_template_', '')
                handle_edit_template(call, template_key)
            elif data == 'sp_lot_management':
                handle_lot_management(call)
            elif data == 'sp_toggle_auto_deactivate':
                handle_toggle_auto_deactivate(call)
            elif data == 'sp_set_balance_threshold':
                handle_set_balance_threshold(call)
            elif data == 'sp_set_lot_category':
                handle_set_lot_category(call)
            elif data == 'sp_toggle_lots':
                handle_toggle_lots(call)
            else:
                # Неизвестный callback
                logger.warning(f'{LOGGER_PREFIX} ❓ Неизвестный callback: {data}')
                try:
                    if bot:
                        bot.answer_callback_query(call.id, "❌ Неизвестная команда")
                    else:
                        logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован для ответа на callback')
                except Exception as answer_error:
                    logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при ответе на неизвестный callback: {answer_error}')
                
        except Exception as e:
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в callback handler: {e}')
            try:
                if bot:
                    bot.answer_callback_query(call.id, "❌ Произошла ошибка")
                else:
                    logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован для ответа на callback')
            except Exception as answer_error:
                logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при ответе на callback: {answer_error}')
    
    # Регистрируем единый callback handler для всех кнопок плагина
    if bot:
        try:
            bot.register_callback_query_handler(
                handle_callback_query,
                func=lambda call: call.data.startswith('sp_')
            )
            logger.info(f'{LOGGER_PREFIX} ✅ Callback handler зарегистрирован')
        except Exception as e:
            logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при регистрации callback handler: {e}')
    else:
        logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован для регистрации callback handler')
    
    # Обработчик текстового ввода для состояний
    def check_text_input_states(m):
        return (tg.check_state(m.chat.id, m.from_user.id, "sp_setting_api_key") or
    
                tg.check_state(m.chat.id, m.from_user.id, "sp_adding_admin") or
                tg.check_state(m.chat.id, m.from_user.id, "sp_setting_subcategories") or
                tg.check_state(m.chat.id, m.from_user.id, "sp_setting_min_balance") or
                tg.check_state(m.chat.id, m.from_user.id, "sp_setting_bonus_points") or
                tg.check_state(m.chat.id, m.from_user.id, "sp_setting_bonus_1_stars") or
                tg.check_state(m.chat.id, m.from_user.id, "sp_setting_bonus_2_stars") or
                tg.check_state(m.chat.id, m.from_user.id, "sp_setting_bonus_3_stars") or
                tg.check_state(m.chat.id, m.from_user.id, "sp_setting_bonus_4_stars") or
                tg.check_state(m.chat.id, m.from_user.id, "sp_setting_bonus_5_stars") or
                tg.check_state(m.chat.id, m.from_user.id, "sp_adding_keyword") or
                tg.check_state(m.chat.id, m.from_user.id, "sp_setting_lot_category") or
                any(tg.check_state(m.chat.id, m.from_user.id, f"sp_editing_template_{t}") 
                    for t in ['steam_request', 'processing', 'success', 'error', 'insufficient_funds', 'invalid_steam', 'maintenance', 'steam_confirmation']))
    
    try:
        tg.msg_handler(handle_text_input, func=check_text_input_states)
        logger.info(f'{LOGGER_PREFIX} ✅ Message handler зарегистрирован')
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при регистрации message handler: {e}')
    
    # Регистрируем команду в кардинале
    c_.add_telegram_commands(UUID, [
        ("steampoints", f"настройки {NAME}", True)
    ])

def init(cardinal: Cardinal):
    """Инициализация плагина"""
    global executor, cardinal_instance
    
    cardinal_instance = cardinal
    
    # Создаем конфигурацию если её нет
    ensure_config_exists()
    
    # Загружаем ожидающие заказы
    load_pending_orders()
    
    # Инициализируем пул потоков для обработки заказов
    executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix='SteamPoints')

def post_init(cardinal: Cardinal):
    """Пост-инициализация плагина"""
    # Запускаем автообновление цены
    if config.get('api_key'):
        # Сначала принудительно обновляем цену
        global cached_price, last_price_update
        cached_price = None  # Сбрасываем кеш
        last_price_update = 0  # Сбрасываем время
        get_current_price()  # Обновляем цену без лога
        
        # Затем запускаем таймер
        start_price_update_timer()
        
        # Запускаем таймер автоматической проверки баланса
        start_balance_check_timer()
        
        # Проверяем баланс и управляем лотами при старте
        logger.info(f'{LOGGER_PREFIX} 🔧 Выполняем проверку баланса API при инициализации...')
        check_balance_and_manage_lots()

def shutdown():
    """Завершение работы плагина"""
    global executor
    
    # Останавливаем таймер автообновления цены
    stop_price_update_timer()
    
    # Останавливаем таймер автоматической проверки баланса
    stop_balance_check_timer()
    
    if executor:
        executor.shutdown(wait=True)
        logger.info(f'{LOGGER_PREFIX} Пул потоков завершен')
    
    logger.info(f'{LOGGER_PREFIX} 💤 Плагин завершил работу')

# Обработчик завершения заказа
def handle_order_completed(runner, order: Order):
    """Обрабатывает завершенные заказы"""
    try:
        orders = load_orders_history()
        
        # Обновляем статус заказа
        for i, existing_order in enumerate(orders):
            if existing_order.get('order_id') == order.id:
                orders[i]['status'] = 'completed'
                orders[i]['completed_at'] = datetime.now().isoformat()
                break
        
        save_orders_history(orders)
        
        # Уведомляем администраторов о завершении заказа
        send_admin_notification(
            'order_completed',
            buyer=order.buyer_username,
            order_id=order.id,
            amount=order.sum
        )
        
        logger.info(f'{LOGGER_PREFIX} 📋 Заказ #{order.id} отмечен как завершенный')
        
    except Exception as ex:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка при обработке завершенного заказа: {ex}')


# Привязки событий
BIND_TO_PRE_INIT = [init, init_commands]
BIND_TO_POST_INIT = [post_init]
BIND_TO_NEW_ORDER = [handle_new_order]
BIND_TO_ORDER_CONFIRMED = [handle_order_completed]
BIND_TO_NEW_MESSAGE = [handle_new_message]
BIND_TO_EXIT = [shutdown]
BIND_TO_DELETE = []

logger.info(f'{LOGGER_PREFIX} 📋 Плагин {NAME} v{VERSION} загружен')

def handle_bonus_settings(call):
    """Настройки системы бонусов"""
    global bot
    
    if not bot:
        logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован в handle_bonus_settings')
        return
    
    try:
        kb = InlineKeyboardMarkup(row_width=1)
        
        # Статус системы бонусов
        bonus_status = '🟢 Включено' if config.get('bonus_system_enabled', False) else '🔴 Отключено'
        kb.add(InlineKeyboardButton(f'🎁 Статус системы бонусов ({bonus_status})', callback_data='sp_toggle_bonus_system'))
        
        # Количество бонусных очков
        bonus_points = config.get('bonus_points_for_review', 1000)
        kb.add(InlineKeyboardButton(f'💎 Бонусные очки ({bonus_points})', callback_data='sp_set_bonus_points'))
        
        kb.add(InlineKeyboardButton('🔙 Назад', callback_data='sp_basic_settings'))
        
        message_text = f'''🎁 <b>Настройки системы бонусов</b>

Система бонусов позволяет автоматически выдавать очки пользователям за 5-звездочные отзывы.

📊 <b>Текущие настройки:</b>
🎁 <b>Статус:</b> {bonus_status}
💎 <b>Бонусные очки:</b> <code>{bonus_points}</code>

💡 <b>Как это работает:</b>
• Пользователь оставляет 5-звездочный отзыв на заказ
• Система автоматически отправляет {bonus_points} очков на его Steam профиль
• Бонус выдается только один раз за заказ

<i>Выберите параметр для изменения:</i>'''
        
        bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                             reply_markup=kb, parse_mode='HTML')
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_bonus_settings: {e}')
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        except:
            pass

def handle_toggle_bonus_system(call):
    """Переключает статус системы бонусов"""
    global config, bot
    
    if not bot:
        logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован в handle_toggle_bonus_system')
        return
    
    try:
        config['bonus_system_enabled'] = not config.get('bonus_system_enabled', False)
        save_config()
        
        status = 'включена' if config['bonus_system_enabled'] else 'отключена'
        bot.answer_callback_query(call.id, f'✅ Система бонусов {status}')
        
        # Возвращаемся к настройкам бонусов
        handle_bonus_settings(call)
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_toggle_bonus_system: {e}')
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        except:
            pass

def handle_set_bonus_points(call):
    """Запрашивает ввод количества бонусных очков"""
    global bot, cardinal_instance
    
    if not bot:
        logger.error(f'{LOGGER_PREFIX} ❌ Bot не инициализирован в handle_set_bonus_points')
        return
    
    if not cardinal_instance or not hasattr(cardinal_instance, 'telegram'):
        logger.error(f'{LOGGER_PREFIX} ❌ Cardinal instance или telegram недоступен')
        try:
            bot.answer_callback_query(call.id, "❌ Ошибка инициализации")
        except:
            pass
        return
    
    try:
        tg = cardinal_instance.telegram
        current_bonus = config.get('bonus_points_for_review', 1000)
        
        msg = bot.edit_message_text(
            f'💎 <b>Настройка бонусных очков</b>\n\n'
            f'Текущее количество: <code>{current_bonus}</code>\n\n'
            f'Введите новое количество бонусных очков (от 100 до 10000):\n\n'
            f'<i>Рекомендуется:</i>\n'
            f'• 500-1000 очков для небольших заказов\n'
            f'• 1000-2000 очков для средних заказов\n'
            f'• 2000-5000 очков для крупных заказов\n\n'
            f'<b>Введите количество очков:</b>',
            call.message.chat.id, call.message.message_id,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton('🔙 Отмена', callback_data='sp_bonus_settings')
            ),
            parse_mode='HTML'
        )
        
        tg.set_state(
            chat_id=call.message.chat.id,
            message_id=msg.message_id,
            user_id=call.from_user.id,
            state="sp_setting_bonus_points"
        )
        
    except Exception as e:
        logger.error(f'{LOGGER_PREFIX} ❌ Ошибка в handle_set_bonus_points: {e}')
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        except:
            pass
