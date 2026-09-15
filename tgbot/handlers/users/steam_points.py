from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from tgbot.data.loader import userRouter, bot
from tgbot.data.config import BotConfig, DB
from tgbot.data.config import BotTexts as BTs
from tgbot.utils.utils import get_unix, get_date
from tgbot.keyboards.new_buttons import STEAM_BUTTONS
from tgbot.keyboards.users import USERS_INLINE
from tgbot.states import userStates

import re
import requests
import json


async def safe_edit_message(call, text, reply_markup=None, parse_mode='HTML'):
    """Безопасное редактирование сообщения (работает и с фото, и с текстом)"""
    try:
        # Сначала пытаемся отредактировать текст (для обычных сообщений)
        await call.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    except Exception:
        try:
            # Если не получилось, пытаемся отредактировать подпись (для сообщений с фото)
            await bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        except Exception:
            # Если и это не получилось, отправляем новое сообщение
            await call.message.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )


class SteamPointsAPI:
    """Класс для работы с API Steam Points"""
    
    def __init__(self):
        self.base_url = "https://api.buysteampoints.com/api"
        
    async def get_price(self):
        """Получает текущую цену за очко"""
        try:
            response = requests.get(f"{self.base_url}/price", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('price', 0.012)
            return 0.012  # Цена по умолчанию
        except:
            return 0.012
    
    async def get_balance(self, api_key):
        """Получает баланс API"""
        try:
            response = requests.post(f"{self.base_url}/balance", 
                                   json={'api_key': api_key}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('balance', 0)
            return None
        except:
            return None
    
    async def buy_points(self, api_key, points, steam_link):
        """Покупает Steam Points"""
        try:
            payload = {
                'api_key': api_key,
                'puan': points,
                'steam_link': steam_link
            }
            
            response = requests.post(f"{self.base_url}/buy", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def validate_steam_profile(self, steam_link):
        """Проверяет валидность Steam профиля"""
        try:
            # Извлекаем ID из ссылки
            steam_id = None
            
            # Проверяем формат ссылки
            if 'steamcommunity.com' not in steam_link:
                return {'valid': False, 'error': 'Неверный формат ссылки. Используйте ссылку на профиль Steam'}
            
            # Извлекаем Steam ID или имя пользователя
            if '/id/' in steam_link:
                # Кастомный URL
                match = re.search(r'/id/([^/]+)', steam_link)
                if match:
                    custom_url = match.group(1)
                    steam_id = custom_url
            elif '/profiles/' in steam_link:
                # Steam64 ID
                match = re.search(r'/profiles/(\d+)', steam_link)
                if match:
                    steam_id = match.group(1)
            
            if not steam_id:
                return {'valid': False, 'error': 'Не удалось извлечь ID из ссылки'}
            
            # Проверяем доступность профиля
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(steam_link, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return {'valid': False, 'error': 'Профиль недоступен или не существует'}
            
            content = response.text.lower()
            
            # Проверяем, что профиль не приватный
            if 'this profile is private' in content or 'этот профиль является приватным' in content:
                return {'valid': False, 'error': 'Профиль является приватным. Сделайте профиль публичным'}
            
            if 'the specified profile could not be found' in content:
                return {'valid': False, 'error': 'Указанный профиль не найден'}
            
            if 'error' in content and 'profile' in content:
                return {'valid': False, 'error': 'Ошибка при загрузке профиля'}
            
            # Проверяем наличие базовых элементов профиля
            if 'steamcommunity' not in content:
                return {'valid': False, 'error': 'Неверная ссылка на профиль Steam'}
            
            return {'valid': True, 'steam_id': steam_id}
            
        except requests.exceptions.Timeout:
            return {'valid': False, 'error': 'Превышено время ожидания при проверке профиля'}
        except Exception as e:
            return {'valid': False, 'error': f'Ошибка проверки профиля: {str(e)}'}


def validate_steam_link(steam_link):
    """Проверяет корректность ссылки Steam"""
    patterns = [
        r'^https://steamcommunity\.com/id/[a-zA-Z0-9_-]+/?$',
        r'^https://steamcommunity\.com/profiles/\d{17}/?$'
    ]
    
    for pattern in patterns:
        if re.match(pattern, steam_link.strip()):
            return True
    return False


@userRouter.message(F.text == BTs.Ru.BUTTONS.steam_points)
@userRouter.message(F.text == BTs.En.BUTTONS.steam_points)  
@userRouter.message(F.text == BTs.Ua.BUTTONS.steam_points)
async def steam_points_menu(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработчик кнопки Steam Points из главного меню"""
    await state.clear()
    
    # Проверяем, включена ли система Steam Points
    steam_config = await DB.get_steam_config()
    if not steam_config:
        await DB.create_steam_config()
        steam_config = await DB.get_steam_config()
    
    if not steam_config.is_enabled:
        await msg.answer("🎮 Steam Points временно недоступны", 
                        reply_markup=USERS_INLINE.close(BotTexts).as_markup())
        return
    
    # Отправляем с фото Steam Points  
    from tgbot.data.config import BotImages
    steam_photo = FSInputFile(BotImages.STEAM_PHOTO)
    await msg.answer_photo(
        photo=steam_photo,
        caption=BotTexts.TEXTS.steam_points_description,
        reply_markup=STEAM_BUTTONS.steam_points_menu(BotTexts).as_markup(),
        parse_mode='HTML'
    )


@userRouter.callback_query(F.data == "steam_points")
async def steam_points_callback(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Callback для Steam Points"""
    await state.clear()
    
    steam_config = await DB.get_steam_config()
    if not steam_config:
        await DB.create_steam_config()
        steam_config = await DB.get_steam_config()
    
    if not steam_config.is_enabled:
        await safe_edit_message(
            call,
            "🎮 Steam Points временно недоступны",
            reply_markup=USERS_INLINE.close(BotTexts).as_markup()
        )
        return
    
    # Используем безопасное редактирование для отображения меню Steam Points
    await safe_edit_message(
        call,
        BotTexts.TEXTS.steam_points_description,
        reply_markup=STEAM_BUTTONS.steam_points_menu(BotTexts).as_markup(),
        parse_mode='HTML'
    )


@userRouter.callback_query(F.data.startswith("steam_buy:"))
async def steam_buy_amount(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработчик выбора количества Steam Points"""
    points = int(call.data.split(":")[1])
    
    # Получаем конфигурацию Steam API
    steam_config = await DB.get_steam_config()
    if not steam_config or not steam_config.is_enabled:
        await call.answer("❌ Steam Points временно недоступны")
        return
    
    # Проверяем лимиты
    if points < steam_config.min_amount or points > steam_config.max_amount:
        await call.answer(f"❌ Недопустимое количество очков! {steam_config.min_amount}-{steam_config.max_amount}")
        return
    
    # Проверяем кратность 100
    if points % 100 != 0:
        await call.answer("❌ Количество очков должно быть кратно 100!")
        return
    
    # Используем только админскую цену (финальную цену для пользователей)
    price_per_point = steam_config.price_per_point
    final_price_rub = points * price_per_point
    
    # Конвертируем в другие валюты
    settings = await DB.get_settings()
    if settings.currency.value == "usd":
        # Конвертируем в USD
        from tgbot.utils.utils import get_exchange
        final_price_usd = await get_exchange(final_price_rub, 'RUB', 'USD', DB)
        currency = "USD"
        price = final_price_usd
    elif settings.currency.value == "eur":
        # Конвертируем в EUR
        final_price_eur = await get_exchange(final_price_rub, 'RUB', 'EUR', DB)
        currency = "EUR"
        price = final_price_eur
    else:
        currency = "RUB"
        price = final_price_rub
    
    # Сохраняем данные в состоянии
    await state.update_data(
        points=points,
        price_rub=final_price_rub,
        api_cost=final_price_rub,  # Теперь api_cost и final_price одинаковы
        currency=currency,
        price=price
    )
    
    # Calculate rate safely
    if points > 0:
        rate_value = price / points
        rate_text = f"{rate_value:.4f}"
    else:
        rate_text = "0.0000"
    
    # Format price safely
    price_text = f"{price:.2f}"
    
    # Create the message text safely
    try:
        message_text = BotTexts.TEXTS.steam_points_amount.format(
            points=points,
            price=price_text,
            currency=BotConfig.CURRENCIES[settings.currency.value]['sign'],
            rate=rate_text
        )
    except ValueError as e:
        # Fallback if format fails
        message_text = f"""🎮 <b>Количество: {points} очков</b>

💰 <b>Цена: {price_text} {BotConfig.CURRENCIES[settings.currency.value]['sign']}</b>
📈 <b>Курс: {rate_text} {BotConfig.CURRENCIES[settings.currency.value]['sign']} за очко</b>

Для продолжения введите ссылку на ваш Steam профиль:

<b>Принимаются ссылки вида:</b>
🔗 <code>https://steamcommunity.com/id/ваш_ник</code>
🔗 <code>https://steamcommunity.com/profiles/76561198000000000</code>"""
    
    # Создаем клавиатуру для ввода Steam профиля
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к Steam Points",
            callback_data="steam_points"
        )
    )
    
    # Поскольку исходное сообщение содержит фото, используем edit_message_caption
    try:
        await bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=message_text,
            parse_mode='HTML',
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        # Если не получается отредактировать подпись, отправляем новое сообщение
        await call.message.answer(
            message_text,
            parse_mode='HTML',
            reply_markup=builder.as_markup()
        )
    
    await state.set_state(userStates.SteamStates.enter_steam_link)


@userRouter.callback_query(F.data == "steam_custom")
async def steam_custom_amount(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработчик ввода пользовательского количества очков"""
    steam_config = await DB.get_steam_config()
    
    await safe_edit_message(
        call,
        BotTexts.TEXTS.steam_custom_amount.format(
            min_points=steam_config.min_amount,
            max_points=steam_config.max_amount
        ),
        reply_markup=USERS_INLINE.custom_button(BotTexts, "steam_points").as_markup(),
        parse_mode='HTML'
    )
    
    await state.set_state(userStates.SteamStates.enter_steam_amount)


@userRouter.message(StateFilter(userStates.SteamStates.enter_steam_amount))
async def process_custom_amount(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработка пользовательского количества очков"""
    if not msg.text.isdigit():
        steam_config = await DB.get_steam_config()
        await msg.answer(
            BotTexts.TEXTS.steam_amount_invalid.format(
                min_points=steam_config.min_amount,
                max_points=steam_config.max_amount
            ),
            parse_mode='HTML'
        )
        return
    
    points = int(msg.text)
    steam_config = await DB.get_steam_config()
    
    # Проверяем лимиты и кратность 100
    if points < steam_config.min_amount or points > steam_config.max_amount or points % 100 != 0:
        await msg.answer(
            BotTexts.TEXTS.steam_amount_invalid.format(
                min_points=steam_config.min_amount,
                max_points=steam_config.max_amount
            ),
            parse_mode='HTML'
        )
        return
    
    # Симулируем клик по кнопке с этим количеством
    await state.clear()
    
    # Используем только админскую цену (финальную цену для пользователей)
    price_per_point = steam_config.price_per_point
    final_price_rub = points * price_per_point
    
    settings = await DB.get_settings()
    if settings.currency.value == "usd":
        from tgbot.utils.utils import get_exchange
        final_price_usd = await get_exchange(final_price_rub, 'RUB', 'USD', DB)
        currency = "USD"
        price = final_price_usd
    elif settings.currency.value == "eur":
        final_price_eur = await get_exchange(final_price_rub, 'RUB', 'EUR', DB)
        currency = "EUR"
        price = final_price_eur
    else:
        currency = "RUB"
        price = final_price_rub
    
    await state.update_data(
        points=points,
        price_rub=final_price_rub,
        api_cost=final_price_rub,  # Теперь api_cost и final_price одинаковы
        currency=currency,
        price=price
    )
    
    # Calculate rate safely
    if points > 0:
        rate_value = price / points
        rate_text = f"{rate_value:.4f}"
    else:
        rate_text = "0.0000"
    
    # Format price safely
    price_text = f"{price:.2f}"
    
    # Create the message text safely
    try:
        message_text = BotTexts.TEXTS.steam_points_amount.format(
            points=points,
            price=price_text,
            currency=BotConfig.CURRENCIES[settings.currency.value]['sign'],
            rate=rate_text
        )
    except ValueError as e:
        # Fallback if format fails
        message_text = f"""🎮 <b>Количество: {points} очков</b>

💰 <b>Цена: {price_text} {BotConfig.CURRENCIES[settings.currency.value]['sign']}</b>
📈 <b>Курс: {rate_text} {BotConfig.CURRENCIES[settings.currency.value]['sign']} за очко</b>

Для продолжения введите ссылку на ваш Steam профиль:

<b>Принимаются ссылки вида:</b>
🔗 <code>https://steamcommunity.com/id/ваш_ник</code>
🔗 <code>https://steamcommunity.com/profiles/76561198000000000</code>"""
    
    await msg.answer(
        message_text,
        parse_mode='HTML'
    )
    
    await state.set_state(userStates.SteamStates.enter_steam_link)


@userRouter.message(StateFilter(userStates.SteamStates.enter_steam_link))
async def process_steam_link(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработка ссылки Steam"""
    steam_link = msg.text.strip()
    
    if not validate_steam_link(steam_link):
        # Создаем клавиатуру с кнопкой "Назад"
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_user_menu")]
        ])
        
        await msg.answer(
            BotTexts.TEXTS.steam_link_invalid,
            reply_markup=back_keyboard,
            parse_mode='HTML'
        )
        return
    
    # Отправляем сообщение о проверке профиля
    checking_msg = await msg.answer(
        "🔄 <b>Проверка Steam профиля...</b>\n\nПожалуйста, подождите...",
        parse_mode='HTML'
    )
    
    # Проверяем Steam профиль
    api = SteamPointsAPI()
    validation_result = await api.validate_steam_profile(steam_link)
    
    if not validation_result['valid']:
        # Создаем клавиатуру с кнопкой "Назад"
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_user_menu")]
        ])
        
        await checking_msg.edit_text(
            f"❌ <b>Ошибка проверки профиля</b>\n\n{validation_result['error']}\n\n"
            f"📝 <b>Убедитесь что:</b>\n"
            f"• Профиль существует и доступен\n"
            f"• Профиль не является приватным\n"
            f"• Ссылка корректна (steamcommunity.com/id/... или steamcommunity.com/profiles/...)",
            reply_markup=back_keyboard,
            parse_mode='HTML'
        )
        return
    
    await checking_msg.edit_text(
        "✅ <b>Steam профиль проверен успешно!</b>",
        parse_mode='HTML'
    )
    
    # Получаем данные из состояния
    data = await state.get_data()
    points = data['points']
    price = data['price']
    currency = data['currency']
    
    # Проверяем баланс пользователя
    user = await DB.get_user(user_id=msg.from_user.id)
    settings = await DB.get_settings()
    
    if settings.currency.value == "rub":
        user_balance = user.balance_rub
    elif settings.currency.value == "usd":
        user_balance = user.balance_usd
    else:
        user_balance = user.balance_eur
    
    if user_balance < price:
        await msg.answer(
            BotTexts.TEXTS.steam_insufficient_funds.format(
                balance=user_balance,
                required=price,
                currency=BotConfig.CURRENCIES[settings.currency.value]['sign']
            ),
            reply_markup=STEAM_BUTTONS.steam_insufficient_funds(BotTexts).as_markup(),
            parse_mode='HTML'
        )
        return
    
    # Сохраняем ссылку Steam
    await state.update_data(steam_link=steam_link)
    
    # Format price safely
    price_text = f"{price:.2f}"
    currency_sign = BotConfig.CURRENCIES[settings.currency.value]['sign']
    
    # Create the message text safely
    try:
        message_text = BotTexts.TEXTS.steam_order_confirm.format(
            steam_link=steam_link,
            points=points,
            price=price_text,
            currency=currency_sign
        )
    except ValueError as e:
        # Fallback if format fails
        message_text = f"""✅ <b>Подтверждение заказа</b>

🎮 <b>Steam профиль:</b> {steam_link}
💎 <b>Количество очков:</b> {points}
💰 <b>К оплате:</b> {price_text} {currency_sign}

Подтвердите заказ:"""
    
    await msg.answer(
        message_text,
        reply_markup=STEAM_BUTTONS.steam_order_confirm(BotTexts, points, price, currency).as_markup(),
        parse_mode='HTML'
    )


@userRouter.callback_query(F.data.startswith("steam_confirm:"))
async def confirm_steam_order(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Подтверждение и обработка заказа Steam Points"""
    points = int(call.data.split(":")[1])
    
    # Получаем данные из состояния
    data = await state.get_data()
    steam_link = data['steam_link']
    price_rub = data['price_rub']
    api_cost = data['api_cost']
    price = data['price']
    
    await safe_edit_message(
        call,
        BotTexts.TEXTS.steam_processing.format(points=points),
        parse_mode='HTML'
    )
    
    # Получаем конфигурацию API
    steam_config = await DB.get_steam_config()
    if not steam_config:
        await DB.create_steam_config()
        steam_config = await DB.get_steam_config()
    
    if not steam_config.api_key:
        await safe_edit_message(
            call,
            BotTexts.TEXTS.steam_error.format(error="API ключ не настроен. Обратитесь к администратору"),
            parse_mode='HTML'
        )
        return
    
    # Списываем средства с баланса пользователя
    user = await DB.get_user(user_id=call.from_user.id)
    settings = await DB.get_settings()
    
    new_balance_rub = user.balance_rub
    new_balance_usd = user.balance_usd
    new_balance_eur = user.balance_eur
    
    if settings.currency.value == "rub":
        new_balance_rub -= price
    elif settings.currency.value == "usd":
        new_balance_usd -= price
    else:
        new_balance_eur -= price
    
    await DB.update_user(
        user_id=call.from_user.id,
        balance_rub=new_balance_rub,
        balance_usd=new_balance_usd,
        balance_eur=new_balance_eur
    )
    
    # Покупаем Steam Points через API
    api = SteamPointsAPI()
    result = await api.buy_points(steam_config.api_key, points, steam_link)
    
    # Создаем запись заказа
    receipt = get_unix(True)
    
    if result.get('success'):
        # Успешная покупка
        points_delivered = result.get('points', points)
        total_cost = result.get('total', 0)
        steam64 = result.get('steam64', '')
        before_points = result.get('before_point', '')
        remaining_balance = result.get('remaining_balance', 0)
        
        try:
            after_points = int(before_points) + points_delivered if before_points.isdigit() else 'N/A'
        except:
            after_points = 'N/A'
        
        # Добавляем заказ в базу
        await DB.add_steam_order(
            user_id=call.from_user.id,
            steam_link=steam_link,
            steam_amount=points,
            points_delivered=points_delivered,
            price_rub=price_rub,
            price_usd=data.get('price_usd', 0),
            price_eur=data.get('price_eur', 0),
            api_cost=api_cost,
            profit=price_rub - api_cost,
            status='completed',
            steam64=steam64,
            before_points=str(before_points),
            after_points=str(after_points),
            api_response=json.dumps(result),
            receipt=receipt
        )
        
        # Форматируем значения перед передачей в .format()
        total_cost_text = f"{price:.2f}"
        currency_sign = BotConfig.CURRENCIES[settings.currency.value]['sign']
        date_text = get_date()
        
        try:
            message_text = BotTexts.TEXTS.steam_success.format(
                steam_link=steam_link,
                points=points_delivered,
                total_cost=price,
                currency=currency_sign,
                before_points=before_points,
                after_points=after_points,
                receipt=receipt,
                date=date_text
            )
        except ValueError:
            # Fallback сообщение если форматирование не удалось
            message_text = f"""✅ <b>Заказ выполнен успешно!</b>

🎮 <b>Steam профиль:</b> {steam_link}
💎 <b>Очки доставлены:</b> {points_delivered}
💰 <b>Стоимость:</b> {total_cost_text} {currency_sign}

📊 <b>Баланс очков:</b>
• До: {before_points}
• После: {after_points}

🆔 <b>Номер заказа:</b> {receipt}
📅 <b>Дата:</b> {date_text}"""
        
        await safe_edit_message(call, message_text, parse_mode='HTML')
        
        # Добавляем заказ в систему покупок
        await DB.add_purchase(
            user_id=call.from_user.id,
            receipt=receipt,
            count=1,  # Steam Points заказ всегда 1 штука
            price_rub=price_rub,
            price_usd=data.get('price_usd', 0),
            price_eur=data.get('price_eur', 0),
            pos_id=0,  # Специальный ID для Steam Points
            item=f"Steam Points: {points_delivered} очков для {steam_link}",
            file_id=None
        )
        
        # Отправляем уведомление администратору
        from tgbot.utils import utils
        await utils.send_admins(
            "steam_points_purchase_log", bot, DB,
            steam_link=steam_link,
            points=points_delivered,
            total_cost=total_cost_text,
            currency=currency_sign,
            before_points=before_points,
            after_points=after_points,
            receipt=receipt,
            user_id=call.from_user.id,
            username=call.from_user.username or "Нет username",
            full_name=call.from_user.full_name
        )
        
    else:
        # Ошибка - возвращаем средства
        await DB.update_user(
            user_id=call.from_user.id,
            balance_rub=user.balance_rub,
            balance_usd=user.balance_usd,
            balance_eur=user.balance_eur
        )
        
        # Добавляем заказ с ошибкой
        await DB.add_steam_order(
            user_id=call.from_user.id,
            steam_link=steam_link,
            steam_amount=points,
            points_delivered=0,
            price_rub=price_rub,
            price_usd=data.get('price_usd', 0),
            price_eur=data.get('price_eur', 0),
            api_cost=api_cost,
            profit=0,
            status='failed',
            api_response=json.dumps(result),
            receipt=receipt
        )
        
        error = result.get('error', 'Unknown error')
        if 'insufficient' in error.lower() or 'balance' in error.lower():
            await safe_edit_message(
                call,
                BotTexts.TEXTS.steam_insufficient_balance,
                parse_mode='HTML'
            )
        else:
            await safe_edit_message(
                call,
                BotTexts.TEXTS.steam_error.format(error=error),
                parse_mode='HTML'
            )
    
    await state.clear()
