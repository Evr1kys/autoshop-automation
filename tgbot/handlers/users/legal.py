from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext

from tgbot.data.config import DB, BotImages
from tgbot.data.loader import bot, userRouter
from tgbot.keyboards.users import InlineButtons
from tgbot.data.config import BotTexts as BTs
from tgbot.utils.utils import load_privacy_policy, load_terms_of_service, load_user_agreement
from aiogram.exceptions import TelegramBadRequest
import os

BotButtons = InlineButtons()

@userRouter.message(lambda message: message.text and any([
    "📋 Документы" in message.text, 
    "📋 Documents" in message.text, 
    "📋 Документи" in message.text
]))
async def user_legal_documents_reply(message: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработка Reply кнопки документов"""
    await state.clear()
    
    text = """📋 <b>Правовые документы</b>

Здесь вы можете ознакомиться с важными документами нашего сервиса:

• 📜 <b>Условия пользования</b> - основные правила использования сервиса
• 🔒 <b>Политика конфиденциальности</b> - как мы обрабатываем ваши данные  
• 📄 <b>Пользовательское соглашение</b> - договор между вами и сервисом

Выберите документ для просмотра:"""

    # Отправляем с изображением если оно есть
    if BotImages.DOCUMENTS_PHOTO:
        try:
            # Используем FSInputFile для локальных изображений
            documents_photo = FSInputFile(BotImages.DOCUMENTS_PHOTO)
            await message.answer_photo(
                photo=documents_photo,
                caption=text,
                reply_markup=BotButtons.legal_documents_user_menu(BotTexts).as_markup(),
                parse_mode='HTML'
            )
        except Exception:
            # Если не удалось отправить фото, отправляем обычное сообщение
            await message.answer(
                text=text,
                reply_markup=BotButtons.legal_documents_user_menu(BotTexts).as_markup(),
                parse_mode='HTML'
            )
    else:
        await message.answer(
            text=text,
            reply_markup=BotButtons.legal_documents_user_menu(BotTexts).as_markup(),
            parse_mode='HTML'
        )

@userRouter.callback_query(lambda call: call.data == "user_legal_menu")
async def user_legal_documents_menu(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Меню правовых документов для пользователей"""
    await state.clear()
    
    text = """📋 <b>Правовые документы</b>

Здесь вы можете ознакомиться с важными документами нашего сервиса:

• 📜 <b>Условия пользования</b> - основные правила использования сервиса
• 🔒 <b>Политика конфиденциальности</b> - как мы обрабатываем ваши данные  
• 📄 <b>Пользовательское соглашение</b> - договор между вами и сервисом

Выберите документ для просмотра:"""

    # Создаем клавиатуру
    keyboard_markup = BotButtons.legal_documents_user_menu(BotTexts).as_markup()
    
    # ПРОСТАЯ И НАДЕЖНАЯ ЛОГИКА
    success = False
    
    # Сначала пытаемся отредактировать существующее сообщение
    try:
        # Проверяем есть ли у сообщения caption (значит это сообщение с фото)
        if hasattr(call.message, 'caption') and call.message.caption is not None:
            await call.message.edit_caption(
                caption=text,
                reply_markup=keyboard_markup,
                parse_mode='HTML'
            )
            success = True
        # Иначе пытаемся отредактировать как текстовое сообщение
        elif hasattr(call.message, 'text') and call.message.text is not None:
            await call.message.edit_text(
                text=text,
                reply_markup=keyboard_markup,
                parse_mode='HTML'
            )
            success = True
    except Exception:
        pass  # Игнорируем ошибки редактирования
    
    # Если редактирование не удалось - удаляем старое и отправляем новое с изображением
    if not success:
        try:
            await call.message.delete()
        except:
            pass  # Игнорируем ошибки удаления
        
        # Отправляем новое сообщение с изображением
        if BotImages.DOCUMENTS_PHOTO and os.path.exists(BotImages.DOCUMENTS_PHOTO):
            try:
                documents_photo = FSInputFile(BotImages.DOCUMENTS_PHOTO)
                await bot.send_photo(
                    chat_id=call.from_user.id,
                    photo=documents_photo,
                    caption=text,
                    reply_markup=keyboard_markup,
                    parse_mode='HTML'
                )
            except Exception:
                # Fallback - отправляем без изображения
                await bot.send_message(
                    chat_id=call.from_user.id,
                    text=text,
                    reply_markup=keyboard_markup,
                    parse_mode='HTML'
                )
        else:
            # Отправляем без изображения
            await bot.send_message(
                chat_id=call.from_user.id,
                text=text,
                reply_markup=keyboard_markup,
                parse_mode='HTML'
            )
    
    await call.answer()


@userRouter.callback_query(lambda call: call.data.startswith("user_legal:"))
async def show_user_legal_document(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Показ правового документа пользователю"""
    doc_type = call.data.split(":")[1]
    
    # Определяем файл и заголовок
    documents = {
        "terms": {
            "file": "terms_of_service.md", 
            "title": "📜 Условия пользования",
            "description": "Основные правила использования нашего сервиса"
        },
        "privacy": {
            "file": "privacy_policy.md", 
            "title": "🔒 Политика конфиденциальности",
            "description": "Информация о том, как мы обрабатываем ваши персональные данные"
        },
        "agreement": {
            "file": "user_agreement.md", 
            "title": "📄 Пользовательское соглашение",
            "description": "Договор между пользователем и нашим сервисом"
        }
    }
    
    if doc_type not in documents:
        await call.answer("❌ Документ не найден")
        return
    
    doc_info = documents[doc_type]
    doc_name = doc_info["title"]  # Имя документа для отладки
    
    try:
        # Используем функции загрузки из utils.py
        if doc_type == "terms":
            content = load_terms_of_service()
        elif doc_type == "privacy":
            content = load_privacy_policy()
        elif doc_type == "agreement":
            content = load_user_agreement()
        else:
            content = None
        

        
        # Проверяем, что контент загружен успешно и это не сообщение об ошибке
        if content and len(content) > 100 and not content.strip().startswith('❌'):
            # Улучшенная конвертация Markdown в HTML
            def markdown_to_html(text):
                import re
                
                # Сначала обрабатываем жирный текст **text** -> <b>text</b>
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                
                # Курсив *text* -> <i>text</i> (но только если это не часть жирного текста)
                text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
                
                # Заголовки - используем более точные регулярные выражения
                text = re.sub(r'^##### (.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
                text = re.sub(r'^#### (.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
                text = re.sub(r'^### (.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
                text = re.sub(r'^## (.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
                text = re.sub(r'^# (.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
                
                return text
            
            content = markdown_to_html(content)
            
            # Проверяем корректность HTML тегов
            def validate_html_tags(text):
                """Проверяет и исправляет некорректные HTML теги"""
                import re
                
                # Подсчитываем открывающие и закрывающие теги
                open_b_tags = len(re.findall(r'<b>', text))
                close_b_tags = len(re.findall(r'</b>', text))
                open_i_tags = len(re.findall(r'<i>', text))
                close_i_tags = len(re.findall(r'</i>', text))
                
                # Если есть незакрытые теги <b>, добавляем закрывающие
                while open_b_tags > close_b_tags:
                    text += '</b>'
                    close_b_tags += 1
                
                # Если есть незакрытые теги <i>, добавляем закрывающие
                while open_i_tags > close_i_tags:
                    text += '</i>'
                    close_i_tags += 1
                
                return text
            
            content = validate_html_tags(content)
            
            # Для пользователей показываем полный документ, но разбиваем на части если он слишком длинный
            # Учитываем заголовок и описание (~200 символов)
            max_content_length = 3500  # Оставляем место для заголовка и навигации
            header_text = f"""📋 <b>{doc_info['title']}</b>

📝 <i>{doc_info['description']}</i>

"""
            
            # Сначала проверяем, нужно ли разбивать
            total_with_header = len(header_text) + len(content)
            
            if total_with_header > 4000:  # Лимит Telegram минус запас
                # Используем функцию разбиения из utils.py для лучшего разделения
                from tgbot.utils.utils import split_text_to_pages
                parts = split_text_to_pages(content, max_content_length)
                
                # Отправляем первую часть
                text = f"""{header_text}<b>Часть 1 из {len(parts)}:</b>

{parts[0]}"""
                
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                if len(parts) > 1:
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="➡️ Следующая часть", callback_data=f"doc_part:{doc_type}:1")],
                        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_legal_menu")]
                    ])
                else:
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_legal_menu")]
                    ])
                
                # Сохраняем части документа в состоянии для навигации
                await state.update_data({f"doc_parts_{doc_type}": parts})
                
            else:
                text = f"""{header_text}{content}"""
                
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="◀️ Назад", callback_data="user_legal_menu")]
                ])
            
        else:
            # Условие проверки контента не прошло - отлаживаем
            text = f"""📋 <b>{doc_info['title']}</b>

❌ <b>Документ временно недоступен</b>

Извините, запрашиваемый документ временно недоступен. 
Обратитесь в поддержку для получения актуальной информации."""
            
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Назад", callback_data="user_legal_menu")]
            ])
        
        try:
            if call.message.text or call.message.caption:
                await call.message.edit_text(text=text, reply_markup=markup, parse_mode='HTML')
            else:
                await call.message.answer(text=text, reply_markup=markup, parse_mode='HTML')
        except Exception:
            await call.message.answer(text=text, reply_markup=markup, parse_mode='HTML')
        
        await call.answer()
        
    except Exception as e:
        print(f"❌ ОШИБКА В ОБРАБОТЧИКЕ ДОКУМЕНТА: {e}")
        import traceback
        traceback.print_exc()
        
        # Показываем подробную ошибку пользователю
        error_text = f"""📋 <b>Ошибка загрузки документа</b>

❌ <b>Произошла техническая ошибка</b>

Детали: {str(e)}

Обратитесь в техподдержку."""
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        error_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="user_legal_menu")]
        ])
        
        try:
            await call.message.edit_text(text=error_text, reply_markup=error_markup, parse_mode='HTML')
        except:
            try:
                await call.message.answer(text=error_text, reply_markup=error_markup, parse_mode='HTML')
            except:
                pass
        
        try:
            await call.answer("❌ Ошибка загрузки документа")
        except Exception:
            pass  # Игнорируем ошибки при отправке ответа

@userRouter.callback_query(lambda call: call.data.startswith("doc_part:"))
async def show_document_part(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Навигация по частям документа"""
    _, doc_type, part_num = call.data.split(":")
    part_num = int(part_num)
    
    user_data = await state.get_data()
    doc_parts = user_data.get(f"doc_parts_{doc_type}")
    
    if not doc_parts or part_num >= len(doc_parts):
        await call.answer("❌ Часть документа не найдена")
        return
    
    documents = {
        "terms": "📜 Условия пользования",
        "privacy": "🔒 Политика конфиденциальности", 
        "agreement": "📄 Пользовательское соглашение"
    }
    
    title = documents.get(doc_type, "Документ")
    
    text = f"""📋 <b>{title}</b>

<b>Часть {part_num + 1} из {len(doc_parts)}:</b>

{doc_parts[part_num]}"""
    
    # Создаем кнопки навигации
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []
    
    # Кнопки навигации
    nav_buttons = []
    if part_num > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"doc_part:{doc_type}:{part_num-1}"))
    if part_num < len(doc_parts) - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Следующая", callback_data=f"doc_part:{doc_type}:{part_num+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    # Кнопка назад
    buttons.append([InlineKeyboardButton(text="◀️ Назад к меню", callback_data="user_legal_menu")])
    
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    try:
        if call.message.text or call.message.caption:
            await call.message.edit_text(text=text, reply_markup=markup, parse_mode='HTML')
        else:
            await call.message.answer(text=text, reply_markup=markup, parse_mode='HTML')
    except Exception:
        await call.message.answer(text=text, reply_markup=markup, parse_mode='HTML')
    
    await call.answer()


# PDF функции удалены - оставляем только просмотр документов
