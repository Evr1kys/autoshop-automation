from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from tgbot.data.config import DB
from tgbot.data.loader import bot, adminRouter
from tgbot.keyboards.admins import InlineButtons
from tgbot.data.config import BotTexts as BTs
import os

BotButtons = InlineButtons()

@adminRouter.callback_query(lambda call: call.data == "legal_documents")
async def legal_documents_menu(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Меню управления правовыми документами"""
    await state.clear()
    
    text = """📋 <b>Управление правовыми документами</b>

Здесь вы можете просмотреть и отредактировать документы:
• Условия пользования
• Политика конфиденциальность
• Пользовательское соглашение  
• FAQ

Выберите документ для просмотра:"""

    try:
        if call.message.text or call.message.caption:
            await call.message.edit_text(
                text=text,
                reply_markup=BotButtons.legal_documents_menu(BotTexts).as_markup()
            )
        else:
            await call.message.answer(
                text=text,
                reply_markup=BotButtons.legal_documents_menu(BotTexts).as_markup()
            )
    except Exception:
        await call.message.answer(
            text=text,
            reply_markup=BotButtons.legal_documents_menu(BotTexts).as_markup()
        )
    
    await call.answer()

@adminRouter.callback_query(lambda call: call.data.startswith("legal_doc:"))
async def show_legal_document(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Показ правового документа"""
    doc_type = call.data.split(":")[1]
    
    # Определяем файл и заголовок
    documents = {
        "terms": {
            "file": "terms_of_service.md", 
            "title": "📜 Условия пользования",
            "description": "Основные правила использования сервиса"
        },
        "privacy": {
            "file": "privacy_policy.md", 
            "title": "🔒 Политика конфиденциальности",
            "description": "Информация о обработке персональных данных"
        },
        "agreement": {
            "file": "user_agreement.md", 
            "title": "📄 Пользовательское соглашение",
            "description": "Договор между пользователем и сервисом"
        }
    }
    
    if doc_type not in documents:
        await call.answer("❌ Документ не найден")
        return
    
    doc_info = documents[doc_type]
    file_path = doc_info["file"]
    
    try:
        # Читаем содержимое файла
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Обрезаем содержимое для превью (первые 1000 символов)
            preview = content[:1000]
            if len(content) > 1000:
                preview += "\n\n... (показаны первые 1000 символов)"
            
            text = f"""📋 <b>{doc_info['title']}</b>

📝 <i>{doc_info['description']}</i>

📄 <b>Содержимое документа:</b>
<pre>{preview}</pre>

📊 <b>Информация о файле:</b>
• Файл: <code>{file_path}</code>
• Размер: {len(content)} символов
• Строк: {content.count(chr(10)) + 1}"""
            
        else:
            text = f"""📋 <b>{doc_info['title']}</b>

❌ <b>Файл не найден</b>

Файл <code>{file_path}</code> отсутствует в системе.
Создайте документ для отображения пользователям."""
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📤 Отправить полный документ", callback_data=f"send_doc:{doc_type}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="legal_documents")]
        ])
        
        try:
            if call.message.text or call.message.caption:
                await call.message.edit_text(text=text, reply_markup=markup)
            else:
                await call.message.answer(text=text, reply_markup=markup)
        except Exception:
            await call.message.answer(text=text, reply_markup=markup)
        
    except Exception as e:
        await call.answer(f"❌ Ошибка чтения файла: {str(e)}")

@adminRouter.callback_query(lambda call: call.data.startswith("send_doc:"))
async def send_full_document(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Отправка полного документа файлом"""
    doc_type = call.data.split(":")[1]
    
    documents = {
        "terms": "terms_of_service.md",
        "privacy": "privacy_policy.md", 
        "agreement": "user_agreement.md"
    }
    
    if doc_type not in documents:
        await call.answer("❌ Документ не найден")
        return
    
    file_path = documents[doc_type]
    
    try:
        if os.path.exists(file_path):
            from aiogram.types import FSInputFile
            document = FSInputFile(file_path)
            await call.message.answer_document(
                document=document,
                caption=f"📋 Полный текст документа: {file_path}"
            )
            await call.answer("✅ Документ отправлен")
        else:
            await call.answer("❌ Файл не найден")
            
    except Exception as e:
        await call.answer(f"❌ Ошибка отправки: {str(e)}")
