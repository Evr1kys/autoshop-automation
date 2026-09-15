from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from tgbot.states.adminStates import AdminMainSettings
from tgbot.data.config import BotButtons, BotConfig, DB
from tgbot.data.config import BotTexts as BTs
from tgbot.data.loader import adminRouter, bot

import os
import asyncio
from datetime import datetime


class AdminNotificationStates(AdminMainSettings):
    """Состояния для работы с уведомлениями"""
    create_notification_title = "create_notification_title"
    create_notification_message = "create_notification_message"
    create_notification_file = "create_notification_file"


@adminRouter.callback_query(F.data == "notifications")
async def notifications_menu(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Главное меню уведомлений"""
    await state.clear()
    
    # Получаем статистику
    notifications = await DB.get_all_notifications()
    total_notifications = len(notifications)
    
    # Считаем общую статистику
    total_sent = sum(n['stats']['sent'] for n in notifications)
    total_pending = sum(n['stats']['pending'] for n in notifications)
    total_errors = sum(n['stats']['errors'] for n in notifications)
    
    text = f"""📢 <b>Управление уведомлениями</b>

📊 <b>Общая статистика:</b>
• Всего уведомлений: <code>{total_notifications}</code>
• Отправлено: <code>{total_sent}</code>
• В очереди: <code>{total_pending}</code>
• Ошибок: <code>{total_errors}</code>

<i>Здесь вы можете создавать уведомления для пользователей, которые покупали определенные товары, и обновлять файлы товаров.</i>"""

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Создать уведомление", callback_data="create_notification")],
        [InlineKeyboardButton(text="📋 Список уведомлений", callback_data="list_notifications")],
        [InlineKeyboardButton(text="📤 Отправить уведомления", callback_data="send_notifications")],
        [InlineKeyboardButton(text="⚙️ Настройки рассылки", callback_data="notification_settings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_panel")]
    ])
    
    await call.message.edit_text(text, reply_markup=markup)


@adminRouter.callback_query(F.data == "create_notification")
async def create_notification_select_product(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Выбор товара для создания уведомления"""
    await state.clear()
    
    # Получаем все позиции товаров
    positions = await DB.get_all_positions()
    
    if not positions:
        await call.answer("❌ Нет доступных товаров для создания уведомлений")
        return
    
    text = "📝 <b>Создание уведомления</b>\n\n🛍️ Выберите товар, для покупателей которого хотите создать уведомление:"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = []
    for pos in positions:
        # Получаем количество покупателей
        buyers = await DB.get_product_buyers(pos.pos_id)
        buyers_count = len(buyers)
        
        keyboard.append([InlineKeyboardButton(
            text=f"{pos.name} ({buyers_count} покупателей)",
            callback_data=f"select_product_notification:{pos.pos_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="notifications")])
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await call.message.edit_text(text, reply_markup=markup)


@adminRouter.callback_query(F.data.startswith("select_product_notification:"))
async def create_notification_title(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Ввод заголовка уведомления"""
    pos_id = int(call.data.split(":")[1])
    
    # Получаем информацию о товаре
    position = await DB.get_position(pos_id=pos_id)
    if not position:
        await call.answer("❌ Товар не найден")
        return
    
    # Получаем количество покупателей
    buyers = await DB.get_product_buyers(pos_id)
    buyers_count = len(buyers)
    
    await state.update_data(pos_id=pos_id, position_name=position.name, buyers_count=buyers_count)
    await state.set_state(AdminNotificationStates.create_notification_title)
    
    text = f"""📝 <b>Создание уведомления</b>

🛍️ <b>Товар:</b> {position.name}
👥 <b>Покупателей:</b> {buyers_count}

Введите <b>заголовок</b> уведомления:

<i>Например: "Обновление товара", "Новая версия файла" и т.д.</i>"""

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="create_notification")]
    ])
    
    await call.message.edit_text(text, reply_markup=markup)


@adminRouter.message(StateFilter(AdminNotificationStates.create_notification_title))
async def create_notification_message(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Ввод сообщения уведомления"""
    data = await state.get_data()
    title = msg.text[:100]  # Ограничиваем длину заголовка
    
    await state.update_data(title=title)
    await state.set_state(AdminNotificationStates.create_notification_message)
    
    text = f"""📝 <b>Создание уведомления</b>

🛍️ <b>Товар:</b> {data['position_name']}
👥 <b>Покупателей:</b> {data['buyers_count']}
📋 <b>Заголовок:</b> {title}

Введите <b>текст уведомления</b>:

<i>Это сообщение получат все пользователи, которые покупали данный товар.</i>"""

    await msg.answer(text)


@adminRouter.message(StateFilter(AdminNotificationStates.create_notification_message))
async def create_notification_file(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Запрос файла для обновления товара"""
    data = await state.get_data()
    message_text = msg.text
    
    await state.update_data(message=message_text)
    await state.set_state(AdminNotificationStates.create_notification_file)
    
    text = f"""📝 <b>Создание уведомления</b>

🛍️ <b>Товар:</b> {data['position_name']}
👥 <b>Покупателей:</b> {data['buyers_count']}
📋 <b>Заголовок:</b> {data['title']}
💬 <b>Сообщение:</b> {message_text[:100]}{'...' if len(message_text) > 100 else ''}

📎 <b>Отправьте файл для обновления товара</b> или нажмите "Пропустить", если файл не нужен:

<i>Если вы отправите файл, он заменит текущие экземпляры товара и будет прикреплен к уведомлению.</i>"""

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭️ Пропустить (без файла)", callback_data="skip_notification_file")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="create_notification")]
    ])
    
    await msg.answer(text, reply_markup=markup)


@adminRouter.callback_query(F.data == "skip_notification_file", StateFilter(AdminNotificationStates.create_notification_file))
async def create_notification_final(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Финальное создание уведомления без файла"""
    data = await state.get_data()
    
    try:
        # Создаем уведомление
        notification_id = await DB.create_product_notification(
            pos_id=data['pos_id'],
            title=data['title'],
            message=data['message']
        )
        
        # Получаем покупателей и добавляем в очередь
        buyers = await DB.get_product_buyers(data['pos_id'])
        if buyers:
            await DB.add_users_to_notification_queue(notification_id, buyers)
        
        await state.clear()
        
        text = f"""✅ <b>Уведомление создано!</b>

📋 <b>Заголовок:</b> {data['title']}
🛍️ <b>Товар:</b> {data['position_name']}
👥 <b>Получателей:</b> {len(buyers)}

Уведомление добавлено в очередь. Используйте "Отправить уведомления" для рассылки."""

        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Управление уведомлениями", callback_data="notifications")]
        ])
        
        await call.message.edit_text(text, reply_markup=markup)
        
    except Exception as e:
        await call.answer(f"❌ Ошибка создания уведомления: {str(e)}")


@adminRouter.message(StateFilter(AdminNotificationStates.create_notification_file), F.document)
async def create_notification_with_file(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Создание уведомления с файлом"""
    data = await state.get_data()
    
    try:
        # Скачиваем файл
        file_info = await bot.get_file(msg.document.file_id)
        file_name = msg.document.file_name or f"update_{data['pos_id']}.txt"
        file_path = f"temp/{file_name}"
        
        # Создаем папку temp если её нет
        os.makedirs("temp", exist_ok=True)
        
        await bot.download_file(file_info.file_path, file_path)
        
        # Создаем уведомление
        notification_id = await DB.create_product_notification(
            pos_id=data['pos_id'],
            title=data['title'],
            message=data['message'],
            file_path=file_path,
            file_id=msg.document.file_id
        )
        
        # Обновляем товар новым файлом
        items_count = await DB.update_product_file(data['pos_id'], file_path, msg.document.file_id)
        
        # Обновляем все покупки этого товара новым файлом
        purchases_updated = await DB.update_purchases_with_new_file(data['pos_id'], msg.document.file_id, data['title'])
        
        # Получаем покупателей и добавляем в очередь
        buyers = await DB.get_product_buyers(data['pos_id'])
        if buyers:
            await DB.add_users_to_notification_queue(notification_id, buyers)
        
        await state.clear()
        
        text = f"""✅ <b>Уведомление с файлом создано!</b>

📋 <b>Заголовок:</b> {data['title']}
🛍️ <b>Товар:</b> {data['position_name']}
👥 <b>Получателей:</b> {len(buyers)}
📦 <b>Обновлено товаров:</b> {items_count}
🛒 <b>Обновлено покупок:</b> {purchases_updated}

Товар и история покупок обновлены новым файлом, уведомление добавлено в очередь."""

        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Управление уведомлениями", callback_data="notifications")]
        ])
        
        await msg.answer(text, reply_markup=markup)
        
    except Exception as e:
        await msg.answer(f"❌ Ошибка создания уведомления: {str(e)}")


@adminRouter.callback_query(F.data == "list_notifications")
async def list_notifications(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Список всех уведомлений"""
    await state.clear()
    
    notifications = await DB.get_all_notifications()
    
    if not notifications:
        text = "📋 <b>Список уведомлений</b>\n\n❌ Уведомления не найдены."
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="notifications")]
        ])
        
        await call.message.edit_text(text, reply_markup=markup)
        return
    
    text = "📋 <b>Список уведомлений</b>\n\n"
    
    for i, notif_data in enumerate(notifications[:10], 1):  # Показываем первые 10
        notif = notif_data['notification']
        stats = notif_data['stats']
        
        status = "✅" if stats['pending'] == 0 else "⏳"
        text += f"{status} <b>{notif.title}</b>\n"
        text += f"   🛍️ {notif_data['position_name']}\n"
        text += f"   📊 {stats['sent']}/{stats['total']} отправлено\n"
        text += f"   📅 {notif.created_date}\n\n"
    
    if len(notifications) > 10:
        text += f"<i>... и еще {len(notifications) - 10} уведомлений</i>"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="notifications")]
    ])
    
    await call.message.edit_text(text, reply_markup=markup)


@adminRouter.callback_query(F.data == "notification_settings")
async def notification_settings(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Настройки системы уведомлений"""
    await state.clear()
    
    text = f"""⚙️ <b>Настройки рассылки</b>

🔧 <b>Текущие настройки:</b>
• Задержка между сообщениями: <code>1 секунда</code>
• Размер пакета: <code>20 уведомлений</code>
• Интервал проверки: <code>30 секунд</code> (если есть уведомления)
• Интервал ожидания: <code>5 минут</code> (если нет уведомлений)

🛠️ <b>Доступные действия:</b>"""

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика отправки", callback_data="notification_stats")],
        [InlineKeyboardButton(text="🔄 Перезапустить очередь", callback_data="restart_notification_queue")],
        [InlineKeyboardButton(text="🗑️ Очистить ошибки", callback_data="clear_notification_errors")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="notifications")]
    ])
    
    await call.message.edit_text(text, reply_markup=markup)


@adminRouter.callback_query(F.data == "notification_stats")
async def notification_stats(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Подробная статистика уведомлений"""
    await state.clear()
    
    # Получаем детальную статистику
    notifications = await DB.get_all_notifications()
    
    if not notifications:
        await call.answer("❌ Нет данных для статистики")
        return
    
    total_notifications = len(notifications)
    total_sent = sum(n['stats']['sent'] for n in notifications)
    total_pending = sum(n['stats']['pending'] for n in notifications)
    total_errors = sum(n['stats']['errors'] for n in notifications)
    total_recipients = sum(n['stats']['total'] for n in notifications)
    
    # Вычисляем проценты
    success_rate = (total_sent / total_recipients * 100) if total_recipients > 0 else 0
    error_rate = (total_errors / total_recipients * 100) if total_recipients > 0 else 0
    
    text = f"""📊 <b>Подробная статистика</b>

📈 <b>Общие показатели:</b>
• Создано уведомлений: <code>{total_notifications}</code>
• Всего получателей: <code>{total_recipients}</code>
• Успешно отправлено: <code>{total_sent}</code> ({success_rate:.1f}%)
• В очереди: <code>{total_pending}</code>
• Ошибок доставки: <code>{total_errors}</code> ({error_rate:.1f}%)

📋 <b>Последние уведомления:</b>"""
    
    # Показываем последние 5 уведомлений
    for i, notif_data in enumerate(notifications[-5:], 1):
        notif = notif_data['notification']
        stats = notif_data['stats']
        status = "✅" if stats['pending'] == 0 else "⏳"
        
        text += f"\n{status} <b>{notif.title[:30]}{'...' if len(notif.title) > 30 else ''}</b>"
        text += f"\n   📊 {stats['sent']}/{stats['total']} • {notif.created_date}"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="notification_settings")]
    ])
    
    await call.message.edit_text(text, reply_markup=markup)


@adminRouter.callback_query(F.data == "restart_notification_queue")
async def restart_notification_queue(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Перезапуск очереди уведомлений"""
    await state.clear()
    
    try:
        # Получаем количество неотправленных уведомлений
        pending_notifications = await DB.get_pending_notifications(100)
        pending_count = len(pending_notifications)
        
        text = f"""🔄 <b>Статус очереди уведомлений</b>

📋 <b>Информация:</b>
• Уведомлений в очереди: <code>{pending_count}</code>

💡 <b>Для управления уведомлениями используйте:</b>
• "Отправить уведомления" - ручная отправка всех уведомлений
• notification_worker.py - автоматическое фоновое выполнение

<i>Уведомления можно отправлять вручную или автоматически через worker</i>"""
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="� Отправить сейчас", callback_data="send_notifications")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="notification_settings")]
        ])
        
        await call.message.edit_text(text, reply_markup=markup)
        
    except Exception as e:
        await call.answer(f"❌ Ошибка: {str(e)}")


@adminRouter.callback_query(F.data == "clear_notification_errors")
async def clear_notification_errors(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Очистка ошибок в уведомлениях"""
    await state.clear()
    
    try:
        # Получаем количество уведомлений с ошибками
        notifications = await DB.get_all_notifications()
        error_count = sum(n['stats']['errors'] for n in notifications)
        
        if error_count == 0:
            await call.answer("✅ Нет ошибок для очистки")
            return
        
        text = f"""🗑️ <b>Очистка ошибок</b>

⚠️ <b>Найдено ошибок:</b> <code>{error_count}</code>

<i>Уведомления с ошибками обычно связаны с:</i>
• Заблокированными ботами
• Удаленными аккаунтами пользователей
• Временными проблемами сети

💡 <b>Рекомендация:</b> Ошибки автоматически помечаются системой и не требуют вмешательства. Повторная отправка может привести к спаму."""
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="notification_settings")]
        ])
        
        await call.message.edit_text(text, reply_markup=markup)
        
    except Exception as e:
        await call.answer(f"❌ Ошибка: {str(e)}")


@adminRouter.callback_query(F.data == "send_notifications")
async def send_notifications(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Отправка всех уведомлений"""
    await state.clear()
    
    # Получаем неотправленные уведомления
    pending_notifications = await DB.get_pending_notifications(50)  # Увеличиваем лимит
    
    if not pending_notifications:
        await call.answer("✅ Все уведомления уже отправлены!")
        return
    
    await call.message.edit_text(f"� <b>Отправляю {len(pending_notifications)} уведомлений...</b>")
    
    sent_count = 0
    error_count = 0
    
    for queue_item, notification in pending_notifications:
        try:
            # Формируем сообщение
            message_text = f"📢 <b>{notification.title}</b>\n\n{notification.message}"
            
            if notification.file_id:
                # Отправляем с файлом
                await bot.send_document(
                    chat_id=queue_item.user_id,
                    document=notification.file_id,
                    caption=message_text,
                    parse_mode="HTML"
                )
            else:
                # Отправляем только текст
                await bot.send_message(
                    chat_id=queue_item.user_id,
                    text=message_text,
                    parse_mode="HTML"
                )
            
            # Отмечаем как отправленное
            await DB.mark_notification_sent(queue_item.queue_id)
            sent_count += 1
            
            # Задержка между отправками
            await asyncio.sleep(0.5)
            
        except Exception as e:
            # Отмечаем с ошибкой
            await DB.mark_notification_sent(queue_item.queue_id, str(e))
            error_count += 1
    
    text = f"""✅ <b>Отправка завершена!</b>

📊 <b>Результаты:</b>
• Успешно отправлено: <code>{sent_count}</code>
• Ошибок: <code>{error_count}</code>

{f'❌ Ошибки: заблокированные боты или удаленные аккаунты' if error_count > 0 else '🎉 Все уведомления успешно доставлены!'}"""

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Отправить еще раз", callback_data="send_notifications")],
        [InlineKeyboardButton(text="📢 Управление уведомлениями", callback_data="notifications")]
    ])
    
    await call.message.edit_text(text, reply_markup=markup)