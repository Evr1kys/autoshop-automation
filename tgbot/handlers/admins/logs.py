from aiogram import F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from tgbot.data.loader import adminRouter
from tgbot.data.config import BotTexts as BTs
from tgbot.keyboards.admins import InlineButtons
from tgbot.utils.error_monitoring import get_all_log_files
import os
import zipfile
import tempfile
from datetime import datetime

ADMIN_INLINE = InlineButtons()

@adminRouter.callback_query(F.data == "system_logs")
async def system_logs_menu(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Главное меню логов системы"""
    await call.message.edit_text(
        "📊 <b>Логи системы</b>\n\n"
        "🔍 Здесь вы можете просматривать и скачивать логи работы системы\n\n"
        "📋 <b>Доступные категории:</b>\n"
        "📊 <i>Системные</i> - общие события системы\n"
        "🎮 <i>Steam API</i> - операции с Steam API\n" 
        "❌ <i>Ошибки Telegram</i> - ошибки отправки сообщений\n"
        "👥 <i>Операции пользователей</i> - действия пользователей\n\n"
        "💡 <i>Логи автоматически ротируются при достижении лимита размера</i>",
        reply_markup=ADMIN_INLINE.system_logs_menu().as_markup(),
        parse_mode='HTML'
    )

@adminRouter.callback_query(F.data == "logs_list")
async def logs_list(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Показать список всех доступных лог-файлов"""
    try:
        log_files = get_all_log_files()
        
        if not log_files:
            await call.message.edit_text(
                "📊 <b>Логи системы</b>\n\n"
                "❌ <b>Лог-файлы не найдены</b>\n\n"
                "Возможные причины:\n"
                "• Система логирования только запущена\n"
                "• Папка logs отсутствует\n"
                "• Нет прав на чтение файлов",
                reply_markup=ADMIN_INLINE.system_logs_menu().as_markup(),
                parse_mode='HTML'
            )
            return
            
        # Формируем текст со списком файлов
        text = "📊 <b>Список лог-файлов</b>\n\n"
        
        total_size = 0
        for log_file in log_files:
            total_size += log_file['size']
            
            # Размер файла
            if log_file['size'] < 1024:
                size_str = f"{log_file['size']} B"
            elif log_file['size'] < 1024*1024:
                size_str = f"{log_file['size']/1024:.1f} KB"
            else:
                size_str = f"{log_file['size']/(1024*1024):.1f} MB"
            
            # Время изменения
            time_str = log_file['modified'].strftime("%d.%m.%Y %H:%M")
            
            text += f"📄 <code>{log_file['name']}</code>\n"
            text += f"   📊 {size_str} | 🕐 {time_str}\n\n"
        
        # Общий размер
        if total_size < 1024*1024:
            total_size_str = f"{total_size/1024:.1f} KB"
        else:
            total_size_str = f"{total_size/(1024*1024):.1f} MB"
            
        text += f"💾 <b>Общий размер:</b> {total_size_str}\n"
        text += f"📁 <b>Файлов:</b> {len(log_files)}\n\n"
        text += "💡 <i>Нажмите на файл для скачивания</i>"
        
        await call.message.edit_text(
            text,
            reply_markup=ADMIN_INLINE.logs_list_keyboard(log_files).as_markup(),
            parse_mode='HTML'
        )
        
    except Exception as e:
        await call.message.edit_text(
            f"❌ <b>Ошибка получения списка логов:</b>\n\n"
            f"<code>{str(e)}</code>",
            reply_markup=ADMIN_INLINE.system_logs_menu().as_markup(),
            parse_mode='HTML'
        )

@adminRouter.callback_query(F.data.startswith("download_log:"))
async def download_log_file(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Скачать конкретный лог-файл"""
    log_filename = call.data.split(":", 1)[1]
    log_path = os.path.join("logs", log_filename)
    
    try:
        # Проверяем существование файла
        if not os.path.exists(log_path):
            await call.answer("❌ Файл не найден", show_alert=True)
            return
            
        # Проверяем размер файла
        file_size = os.path.getsize(log_path)
        max_size = 50 * 1024 * 1024  # 50MB лимит Telegram
        
        if file_size > max_size:
            await call.answer("❌ Файл слишком большой для отправки через Telegram (>50MB)", show_alert=True)
            return
            
        if file_size == 0:
            await call.answer("❌ Файл пустой", show_alert=True)
            return
            
        # Отправляем файл
        await call.message.edit_text(
            f"📤 <b>Отправка файла...</b>\n\n"
            f"📄 <code>{log_filename}</code>\n"
            f"📊 Размер: {file_size/1024:.1f} KB",
            parse_mode='HTML'
        )
        
        # Создаем FSInputFile и отправляем
        document = FSInputFile(log_path, filename=log_filename)
        await call.message.answer_document(
            document,
            caption=f"📊 <b>Лог-файл:</b> <code>{log_filename}</code>\n"
                   f"📅 <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                   f"📊 <b>Размер:</b> {file_size/1024:.1f} KB",
            parse_mode='HTML'
        )
        
        # Возвращаем к меню
        await call.message.edit_text(
            "✅ <b>Файл успешно отправлен!</b>",
            reply_markup=ADMIN_INLINE.system_logs_menu().as_markup(),
            parse_mode='HTML'
        )
        
    except Exception as e:
        await call.message.edit_text(
            f"❌ <b>Ошибка отправки файла:</b>\n\n"
            f"<code>{str(e)}</code>",
            reply_markup=ADMIN_INLINE.system_logs_menu().as_markup(),
            parse_mode='HTML'
        )

@adminRouter.callback_query(F.data == "download_all_logs")
async def download_all_logs(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Скачать все логи в архиве"""
    try:
        log_files = get_all_log_files()
        
        if not log_files:
            await call.answer("❌ Лог-файлы не найдены", show_alert=True)
            return
            
        # Подсчитываем общий размер
        total_size = sum(log_file['size'] for log_file in log_files)
        max_size = 50 * 1024 * 1024  # 50MB лимит Telegram
        
        await call.message.edit_text(
            f"📦 <b>Создание архива...</b>\n\n"
            f"📁 Файлов: {len(log_files)}\n"
            f"📊 Общий размер: {total_size/(1024*1024):.1f} MB\n\n"
            f"⏳ Пожалуйста, подождите...",
            parse_mode='HTML'
        )
        
        # Создаем временный архив
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for log_file in log_files:
                    if os.path.exists(log_file['path']):
                        zip_file.write(log_file['path'], log_file['name'])
            
            # Проверяем размер архива
            archive_size = os.path.getsize(temp_path)
            
            if archive_size > max_size:
                await call.message.edit_text(
                    f"❌ <b>Архив слишком большой для отправки</b>\n\n"
                    f"📊 Размер архива: {archive_size/(1024*1024):.1f} MB\n"
                    f"🚫 Лимит Telegram: {max_size/(1024*1024):.0f} MB\n\n"
                    f"💡 Попробуйте скачать файлы по отдельности",
                    reply_markup=ADMIN_INLINE.system_logs_menu().as_markup(),
                    parse_mode='HTML'
                )
                return
            
            # Отправляем архив
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"system_logs_{timestamp}.zip"
            
            document = FSInputFile(temp_path, filename=archive_name)
            await call.message.answer_document(
                document,
                caption=f"📦 <b>Архив логов системы</b>\n"
                       f"📅 <b>Дата создания:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                       f"📁 <b>Файлов в архиве:</b> {len(log_files)}\n"
                       f"📊 <b>Размер архива:</b> {archive_size/1024:.1f} KB",
                parse_mode='HTML'
            )
            
            # Возвращаем к меню
            await call.message.edit_text(
                "✅ <b>Архив успешно создан и отправлен!</b>",
                reply_markup=ADMIN_INLINE.system_logs_menu().as_markup(),
                parse_mode='HTML'
            )
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        await call.message.edit_text(
            f"❌ <b>Ошибка создания архива:</b>\n\n"
            f"<code>{str(e)}</code>",
            reply_markup=ADMIN_INLINE.system_logs_menu().as_markup(),
            parse_mode='HTML'
        )