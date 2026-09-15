from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tgbot.data.loader import adminRouter
from tgbot.data.config import BotConfig, DB
from tgbot.data.config import BotTexts as BTs
from tgbot.utils.utils import get_unix, get_date
from tgbot.keyboards.admins import ADMIN_INLINE
from tgbot.states import adminStates

import asyncio


@adminRouter.callback_query(F.data == "steam_management")
async def steam_management(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Управление Steam Points"""
    await state.clear()
    
    # Получаем конфигурацию и статистику
    steam_config = await DB.get_steam_config()
    
    # Если конфигурации нет, создаем её
    if not steam_config:
        await DB.create_steam_config()
        steam_config = await DB.get_steam_config()
    
    total_orders = await DB.get_steam_orders_count()
    pending_orders = await DB.get_pending_steam_orders_count()
    
    status = "🟢 Включено" if steam_config.is_enabled else "🔴 Выключено"
    
    # Форматируем баланс (показываем в рублях)
    balance_text = "Не проверен"
    if steam_config.current_balance is not None:
        balance_text = f"{steam_config.current_balance:.2f} ₽"
    
    await call.message.edit_text(
        f"🎮 <b>Управление Steam Points</b>\n\n"
        f"📊 Статус: {status}\n"
        f"🔑 API ключ: {'✅ Настроен' if steam_config.api_key else '❌ Не настроен'}\n"
        f"💰 Цена за 1 очко: {steam_config.price_per_point:.4f} ₽\n"
        f"📈 Комиссия: {steam_config.commission_percent}%\n"
        f"💵 Баланс API: {balance_text}\n\n"
        f"📋 Всего заказов: <b>{total_orders}</b>\n"
        f"⏳ В обработке: <b>{pending_orders}</b>\n\n"
        f"Выберите действие:",
        reply_markup=ADMIN_INLINE.steam_management().as_markup(),
        parse_mode='HTML'
    )


@adminRouter.callback_query(F.data == "steam_settings")
async def steam_settings(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Настройки Steam Points"""
    steam_config = await DB.get_steam_config()
    
    # Если конфигурации нет, создаем её
    if not steam_config:
        await DB.create_steam_config()
        steam_config = await DB.get_steam_config()
    
    # Форматируем баланс (показываем в рублях)
    balance_text = "Не проверен"
    if steam_config.current_balance is not None:
        balance_text = f"{steam_config.current_balance:.2f} ₽"
    
    await call.message.edit_text(
        f"⚙️ <b>Настройки Steam Points</b>\n\n"
        f"🌐 API URL: {steam_config.api_url}\n"
        f"🔑 API ключ: {'*' * 20 if steam_config.api_key else 'Не установлен'}\n"
        f"📊 Статус: {'Включено' if steam_config.is_enabled else 'Выключено'}\n"
        f"💰 Цена за 1 очко: {steam_config.price_per_point:.4f} ₽\n"
        f"📈 Комиссия: {steam_config.commission_percent}%\n"
        f"📏 Мин. сумма: {steam_config.min_amount} очков\n"
        f"📏 Макс. сумма: {steam_config.max_amount} очков\n"
        f"💵 Баланс API: {balance_text}\n\n"
        f"Выберите что изменить:",
        reply_markup=ADMIN_INLINE.steam_settings().as_markup(),
        parse_mode='HTML'
    )


@adminRouter.callback_query(F.data == "change_steam_price")
async def change_steam_price(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Изменить цену Steam Points"""
    await call.message.edit_text(
        "💰 <b>Изменение цены Steam Points</b>\n\n"
        "Введите новую цену за 1 Steam Point в рублях:\n"
        "Например: 0.0050 (пол копейки за очко)\n\n"
        "⚠️ Будьте осторожны! Эта цена влияет на все новые заказы.",
        reply_markup=ADMIN_INLINE.back_to_steam_settings().as_markup(),
        parse_mode='HTML'
    )
    
    await state.set_state(adminStates.SteamSettings.enter_price)


@adminRouter.message(StateFilter(adminStates.SteamSettings.enter_price))
async def process_steam_price(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработка новой цены"""
    try:
        new_price = float(msg.text)
        
        if new_price <= 0:
            await msg.answer("❌ Цена должна быть больше 0")
            return
        
        if new_price > 1:
            await msg.answer("❌ Цена слишком высокая (больше 1 рубля за очко)")
            return
        
        await DB.update_steam_config(price_per_point=new_price)
        
        await msg.answer(
            f"✅ Цена обновлена: {new_price:.4f} ₽ за 1 Steam Point",
            parse_mode='HTML'
        )
        
        await state.clear()
        
    except ValueError:
        await msg.answer("❌ Введите корректную цену (число)")


@adminRouter.callback_query(F.data == "change_steam_commission")
async def change_steam_commission(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Изменить комиссию Steam Points"""
    await call.message.edit_text(
        "📈 <b>Изменение комиссии Steam Points</b>\n\n"
        "Введите новую комиссию в процентах:\n"
        "Например: 5.0 (5% комиссии)\n\n"
        "💡 Комиссия добавляется к базовой цене API",
        reply_markup=ADMIN_INLINE.back_to_steam_settings().as_markup(),
        parse_mode='HTML'
    )
    
    await state.set_state(adminStates.SteamSettings.enter_commission)


@adminRouter.message(StateFilter(adminStates.SteamSettings.enter_commission))
async def process_steam_commission(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработка новой комиссии"""
    try:
        new_commission = float(msg.text)
        
        if new_commission < 0:
            await msg.answer("❌ Комиссия не может быть отрицательной")
            return
        
        if new_commission > 100:
            await msg.answer("❌ Комиссия не может быть больше 100%")
            return
        
        await DB.update_steam_config(commission_percent=new_commission)
        
        await msg.answer(
            f"✅ Комиссия обновлена: {new_commission}%",
            parse_mode='HTML'
        )
        
        await state.clear()
        
    except ValueError:
        await msg.answer("❌ Введите корректный процент (число)")


@adminRouter.callback_query(F.data == "change_steam_api_key")
async def change_steam_api_key(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Изменить API ключ Steam"""
    await call.message.edit_text(
        "🔑 <b>Изменение API ключа Steam</b>\n\n"
        "Введите новый API ключ для buysteampoints.com:\n\n"
        "⚠️ Убедитесь, что ключ действителен!",
        reply_markup=ADMIN_INLINE.back_to_steam_settings().as_markup(),
        parse_mode='HTML'
    )
    
    await state.set_state(adminStates.SteamSettings.enter_api_key)


@adminRouter.message(StateFilter(adminStates.SteamSettings.enter_api_key))
async def process_steam_api_key(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработка нового API ключа"""
    api_key = msg.text.strip()
    
    if len(api_key) < 10:
        await msg.answer("❌ API ключ слишком короткий")
        return
    
    await DB.update_steam_config(api_key=api_key)
    
    # Проверяем баланс после добавления API ключа
    try:
        balance = await DB.get_steam_api_balance()
        if balance is not None:
            await msg.answer(
                f"✅ API ключ обновлен\n\n"
                f"💰 Баланс API: {balance} ₽\n\n"
                f"🔄 Проверьте работоспособность в настройках Steam",
                parse_mode='HTML'
            )
        else:
            await msg.answer(
                "✅ API ключ обновлен\n\n"
                "⚠️ Не удалось проверить баланс\n\n"
                "🔄 Проверьте работоспособность в настройках Steam",
                parse_mode='HTML'
            )
    except:
        await msg.answer(
            "✅ API ключ обновлен\n\n"
            "🔄 Проверьте работоспособность в настройках Steam",
            parse_mode='HTML'
        )
    
    await state.clear()


@adminRouter.callback_query(F.data == "change_steam_limits")
async def change_steam_limits(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Изменить лимиты Steam Points"""
    await call.message.edit_text(
        "📏 <b>Изменение лимитов Steam Points</b>\n\n"
        "Введите новые лимиты в формате:\n"
        "<code>мин_лимит макс_лимит</code>\n\n"
        "Например: <code>100 10000</code>\n\n"
        "⚠️ Лимиты должны быть кратны 100",
        reply_markup=ADMIN_INLINE.back_to_steam_settings().as_markup(),
        parse_mode='HTML'
    )
    
    await state.set_state(adminStates.SteamSettings.enter_limits)


@adminRouter.message(StateFilter(adminStates.SteamSettings.enter_limits))
async def process_steam_limits(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработка новых лимитов"""
    try:
        parts = msg.text.strip().split()
        if len(parts) != 2:
            await msg.answer("❌ Введите лимиты в формате: мин_лимит макс_лимит")
            return
        
        min_amount = int(parts[0])
        max_amount = int(parts[1])
        
        if min_amount < 100 or max_amount < 100:
            await msg.answer("❌ Лимиты должны быть не менее 100")
            return
        
        if min_amount >= max_amount:
            await msg.answer("❌ Минимальный лимит должен быть меньше максимального")
            return
        
        if min_amount % 100 != 0 or max_amount % 100 != 0:
            await msg.answer("❌ Лимиты должны быть кратны 100")
            return
        
        await DB.update_steam_config(min_amount=min_amount, max_amount=max_amount)
        
        await msg.answer(
            f"✅ Лимиты обновлены:\n"
            f"📏 Минимум: {min_amount} очков\n"
            f"📏 Максимум: {max_amount} очков",
            parse_mode='HTML'
        )
        
        await state.clear()
        
    except ValueError:
        await msg.answer("❌ Введите корректные числа")


@adminRouter.callback_query(F.data == "toggle_steam_status")
async def toggle_steam_status(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Включить/выключить Steam Points"""
    steam_config = await DB.get_steam_config()
    
    # Если конфигурации нет, создаем её
    if not steam_config:
        await DB.create_steam_config()
        steam_config = await DB.get_steam_config()
    
    new_status = not steam_config.is_enabled
    
    await DB.update_steam_config(is_enabled=new_status)
    
    status_text = "включена" if new_status else "выключена"
    await call.answer(f"✅ Система Steam Points {status_text}")
    
    # Если включаем систему, проверяем баланс
    if new_status and steam_config.api_key:
        try:
            balance = await DB.get_steam_api_balance()
            if balance is not None:
                # Получаем актуальную цену за очко из конфигурации
                steam_config = await DB.get_steam_config()
                if steam_config and steam_config.api_price_per_point:
                    try:
                        api_price = float(steam_config.api_price_per_point)
                    except (ValueError, TypeError):
                        api_price = 0.011  # Значение по умолчанию
                else:
                    api_price = 0.011  # Значение по умолчанию
                    
                balance_points = balance / api_price if api_price > 0 else 0
                await call.answer(f"✅ Система Steam Points {status_text}\n💰 Баланс: {balance:.2f} ₽ ({balance_points:,.0f} очков)")
            else:
                await call.answer(f"✅ Система Steam Points {status_text}\n⚠️ Не удалось проверить баланс")
        except:
            pass
    
    # Обновляем меню
    await steam_management(call, state, BotTexts)


@adminRouter.callback_query(F.data == "steam_orders")
async def steam_orders(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Просмотр заказов Steam Points"""
    orders = await DB.get_recent_steam_orders(limit=10)
    
    if not orders:
        await call.message.edit_text(
            "📋 Нет заказов Steam Points",
            reply_markup=ADMIN_INLINE.back_to_steam().as_markup(),
            parse_mode='HTML'
        )
        return
    
    text = "📋 <b>Последние заказы Steam Points</b>\n\n"
    
    for order in orders:
        user = await DB.get_user(user_id=order.user_id)
        status_emoji = {
            "pending": "⏳",
            "processing": "🔄", 
            "completed": "✅",
            "failed": "❌",
            "cancelled": "🚫"
        }.get(order.status, "❓")
        
        text += f"{status_emoji} <b>Заказ #{order.order_id}</b>\n"
        text += f"👤 {user.user_name if user else 'Неизвестный'}\n"
        text += f"🎮 {order.steam_amount} очков\n"
        text += f"💰 {order.price_rub:.2f} ₽\n"
        text += f"📅 {order.created_at}\n\n"
    
    await call.message.edit_text(
        text,
        reply_markup=ADMIN_INLINE.steam_orders_menu().as_markup(),
        parse_mode='HTML'
    )


@adminRouter.callback_query(F.data == "steam_balance")
async def steam_balance(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Проверка баланса Steam API"""
    await state.clear()
    
    # Получаем конфигурацию Steam API
    steam_config = await DB.get_steam_config()
    if not steam_config:
        await DB.create_steam_config()
        steam_config = await DB.get_steam_config()
    
    if not steam_config.api_key:
        await call.message.edit_text(
            "🎮 <b>Steam API Баланс</b>\n\n"
            "❌ <b>API ключ не настроен</b>\n\n"
            "🔧 <b>Для получения баланса необходимо:</b>\n"
            "• Настроить API ключ в настройках Steam Points\n"
            "• Убедиться в правильности ключа\n"
            "• Проверить доступность API сервиса\n\n"
            "⚙️ <b>Перейдите в настройки для конфигурации</b>",
            reply_markup=ADMIN_INLINE.back_to_steam().as_markup(),
            parse_mode='HTML'
        )
        return
    
    # Показываем сообщение о загрузке
    await call.message.edit_text(
        "🎮 <b>Steam API Баланс</b>\n\n"
        "🔄 <b>Подключение к API...</b>\n"
        "⏳ Получаем актуальный баланс\n"
        "📊 Рассчитываем стоимость в рублях\n\n"
        "⏱️ <i>Пожалуйста, подождите...</i>",
        reply_markup=ADMIN_INLINE.back_to_steam().as_markup(),
        parse_mode='HTML'
    )
    
    # Получаем баланс через API
    try:
        balance = await DB.get_steam_api_balance()
        
        if balance is not None:
            # Форматируем баланс
            if balance >= 1000:
                balance_text = f"{balance:,.0f}"
            else:
                balance_text = f"{balance:.2f}"
            
            # balance уже в рублях! Нужно рассчитать очки для отображения
            steam_config = await DB.get_steam_config()
            if steam_config and steam_config.api_price_per_point:
                try:
                    api_price = float(steam_config.api_price_per_point)
                except (ValueError, TypeError):
                    api_price = 0.011  # Значение по умолчанию
            else:
                api_price = 0.011  # Значение по умолчанию
                
            if steam_config and steam_config.price_per_point:
                try:
                    admin_price = float(steam_config.price_per_point)
                except (ValueError, TypeError):
                    admin_price = 0.015  # Значение по умолчанию
            else:
                admin_price = 0.015  # Значение по умолчанию
                
            balance_points = balance / api_price if api_price > 0 else 0
            
            # Форматируем время последней проверки
            last_check = 'Только что'  # Упрощаем для избежания ошибок
            
            await call.message.edit_text(
                f"🎮 <b>Steam API Баланс</b>\n\n"
                f"💰 <b>Баланс:</b> {balance:.2f} ₽\n"
                f"💎 <b>Очки Steam:</b> {balance_points:,.0f}\n"
                f"� <b>API цена:</b> {api_price:.4f} ₽ за очко\n"
                f"� <b>Цена пользователей:</b> {admin_price:.4f} ₽ за очко\n\n"
                f"🕐 <b>Последняя проверка:</b> {last_check}\n\n"
                f"✅ <b>Статус:</b> Баланс получен успешно",
                reply_markup=ADMIN_INLINE.back_to_steam().as_markup(),
                parse_mode='HTML'
            )
        else:
            await call.message.edit_text(
                "🎮 <b>Steam API Баланс</b>\n\n"
                "❌ <b>Ошибка получения баланса</b>\n\n"
                "🔍 <b>Возможные причины:</b>\n"
                "• 🔑 Неверный API ключ\n"
                "• 🌐 Проблемы с API сервисом\n"
                "• 📡 Нет подключения к интернету\n"
                "• ⚙️ Неправильная конфигурация\n\n"
                "💡 <b>Рекомендации:</b>\n"
                "• Проверьте настройки API ключа\n"
                "• Убедитесь в стабильности интернета\n"
                "• Попробуйте позже",
                reply_markup=ADMIN_INLINE.back_to_steam().as_markup(),
                parse_mode='HTML'
            )
            
    except Exception as e:
        await call.message.edit_text(
            f"🎮 <b>Steam API Баланс</b>\n\n"
            f"❌ <b>Критическая ошибка</b>\n\n"
            f"🔧 <b>Детали ошибки:</b>\n"
            f"<code>{str(e)}</code>\n\n"
            f"💡 <b>Что делать:</b>\n"
            f"• Проверьте логи бота\n"
            f"• Обратитесь к разработчику\n"
            f"• Попробуйте перезапустить бота",
            reply_markup=ADMIN_INLINE.back_to_steam().as_markup(),
            parse_mode='HTML'
        )


@adminRouter.callback_query(F.data == "update_steam_price")
async def update_steam_price(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обновление цены Steam Points из API"""
    await state.clear()
    
    # Показываем сообщение о загрузке
    await call.message.edit_text(
        "🎮 <b>Обновление цены Steam Points</b>\n\n"
        "🔄 <b>Подключение к API...</b>\n"
        "⏳ Получаем актуальную цену\n"
        "📊 Обновляем настройки\n\n"
        "⏱️ <i>Пожалуйста, подождите...</i>",
        reply_markup=ADMIN_INLINE.back_to_steam_settings().as_markup(),
        parse_mode='HTML'
    )
    
    try:
        # Получаем цену из API
        new_price = await DB.get_steam_api_price()
        
        if new_price is not None:
            # Получаем конфигурацию для отображения
            steam_config = await DB.get_steam_config()
            
            # Форматируем время последней проверки
            last_check = steam_config.last_price_check or 'Никогда'
            if last_check != 'Никогда':
                try:
                    import datetime
                    timestamp = int(last_check)
                    last_check = datetime.datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M')
                except:
                    pass
            
            await call.message.edit_text(
                f"🎮 <b>Цена Steam Points обновлена</b>\n\n"
                f"💰 <b>Новая цена:</b> {new_price:.4f} ₽ за очко\n"
                f"📈 <b>Наценка:</b> {steam_config.commission_percent}%\n"
                f"💎 <b>Итоговая цена:</b> {new_price * (1 + steam_config.commission_percent/100):.4f} ₽ за очко\n\n"
                f"🕐 <b>Последнее обновление:</b> {last_check}\n\n"
                f"✅ <b>Статус:</b> Цена успешно обновлена",
                reply_markup=ADMIN_INLINE.back_to_steam_settings().as_markup(),
                parse_mode='HTML'
            )
        else:
            await call.message.edit_text(
                "🎮 <b>Обновление цены Steam Points</b>\n\n"
                "❌ <b>Ошибка получения цены</b>\n\n"
                "🔍 <b>Возможные причины:</b>\n"
                "• 🌐 Проблемы с API сервисом\n"
                "• 📡 Нет подключения к интернету\n"
                "• ⚙️ Неправильная конфигурация API\n\n"
                "💡 <b>Рекомендации:</b>\n"
                "• Проверьте настройки API URL\n"
                "• Убедитесь в стабильности интернета\n"
                "• Попробуйте позже",
                reply_markup=ADMIN_INLINE.back_to_steam_settings().as_markup(),
                parse_mode='HTML'
            )
            
    except Exception as e:
        await call.message.edit_text(
            f"🎮 <b>Обновление цены Steam Points</b>\n\n"
            f"❌ <b>Критическая ошибка</b>\n\n"
            f"🔧 <b>Детали ошибки:</b>\n"
            f"<code>{str(e)}</code>\n\n"
            f"💡 <b>Что делать:</b>\n"
            f"• Проверьте логи бота\n"
            f"• Обратитесь к разработчику\n"
            f"• Попробуйте перезапустить бота",
            reply_markup=ADMIN_INLINE.back_to_steam_settings().as_markup(),
            parse_mode='HTML'
        )
