from aiogram import F
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from aiogram.exceptions import TelegramBadRequest

from tgbot.data.loader import bot, userRouter, adminRouter, dp
from tgbot.data.config import BotButtons, BotConfig, BotImages, DB
from tgbot.data.config import BotTexts as BTs
from tgbot.utils import utils, models
from loguru import logger
from tgbot.utils.utils import safe_answer_with_photo, safe_send_photo
from tgbot.states import userStates

import asyncio
import os


@dp.callback_query(F.data == "NONE")
async def none_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()


async def check_user_subscription(user_id: int) -> tuple[bool, str]:
    """
    Проверяет подписку пользователя на обязательные каналы.
    Возвращает (подписан_на_все, текст_с_каналами)
    """
    # Проверка подписки временно отключена
    return True, ""


@userRouter.callback_query(F.data == "check_sub")
async def check_sub(call: CallbackQuery, state: FSMContext):
    await state.clear()
    settings = await DB.get_settings()
    BotTexts = await utils.get_language(call.from_user.id, DB)
    await call.message.delete()
    
    # 1. СНАЧАЛА ПРОВЕРЯЕМ ПОДПИСКУ НА КАНАЛЫ (точно как в /start)
    is_subscribed, channels_txt = await check_user_subscription(call.from_user.id)
    
    if not is_subscribed:
        # Если не подписан - показываем требование подписки
        return await call.message.answer(
            BotTexts.TEXTS.channels_error.format(urls_txt=channels_txt), 
            reply_markup=(await BotButtons.USERS_INLINE.sub_kb(
                BotTexts, bot, BotConfig.CHANNELS_FOR_SUBSCRIBE
            )).as_markup(),
            parse_mode='HTML'
        )
    
    # 2. ПРОВЕРЯЕМ СУЩЕСТВОВАНИЕ ПОЛЬЗОВАТЕЛЯ В БД
    user = await DB.get_user(user_id=call.from_user.id)
    
    # Если пользователь новый (не существует в базе данных)
    if not user:
        # Проверяем, включена ли мультиязычность
        if settings.multi_lang:
            # Показываем выбор языка
            kb = BotButtons.USERS_INLINE.first_time_choose_language().as_markup()
            return await call.message.answer(
                """🌍 <b>Выберите язык / Choose language / Оберіть мову</b>

🇷🇺 Русский - для русскоязычных пользователей
🇺🇸 English - for English speakers  
🇺🇦 Українська - для україномовних користувачів""",
                reply_markup=kb,
                parse_mode='HTML'
            )
        else:
            # Создаем пользователя с языком по умолчанию
            await DB.register_user(
                user_id=call.from_user.id,
                user_name=call.from_user.username or "",
                full_name=call.from_user.first_name or ""
            )
            
            # Обновляем язык
            await DB.update_user(call.from_user.id, language=settings.default_lang)
            
            # Получаем созданного пользователя
            user = await DB.get_user(user_id=call.from_user.id)
    
    # 3. ЕСЛИ ПОЛЬЗОВАТЕЛЬ СУЩЕСТВУЕТ, НО НЕ ВЫБРАЛ ЯЗЫК (для обратной совместимости)
    if settings.multi_lang and not user.language:
        return await call.message.answer(
            """🌍 <b>Выберите язык / Choose language / Оберіть мову</b>

🇷🇺 Русский - для русскоязычных пользователей
🇺🇸 English - for English speakers  
🇺🇦 Українська - для українськомовних користувачів""",
            reply_markup=BotButtons.USERS_INLINE.first_time_choose_language().as_markup(),
            parse_mode='HTML'
        )
    
    # 4. ЕСЛИ ПОЛЬЗОВАТЕЛЬ СУЩЕСТВУЕТ, НО НЕ ПРИНЯЛ ПОЛИТИКУ
    if not user.privacy_accepted:
        from tgbot.utils.utils import load_privacy_policy, split_text_to_pages
        
        privacy_text = load_privacy_policy()
        
        # Применяем форматирование Markdown -> HTML
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
        
        # Форматируем текст политики
        formatted_privacy = markdown_to_html(privacy_text)
        pages = split_text_to_pages(formatted_privacy, max_length=3800)
        
        if len(pages) > 1:
            page_text = f"""🔒 <b>Политика конфиденциальности</b>

📝 <i>Страница 1 из {len(pages)}</i>

{pages[0]}"""
            kb = BotButtons.USERS_INLINE.privacy_policy_with_navigation_kb(BotTexts, 0, len(pages)).as_markup()
        else:
            page_text = f"""🔒 <b>Политика конфиденциальности</b>

{formatted_privacy}"""
            kb = BotButtons.USERS_INLINE.privacy_policy_kb(BotTexts).as_markup()
        
        return await call.message.answer(
            page_text,
            reply_markup=kb,
            parse_mode="HTML"
        )
    
    # 5. ЕСЛИ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ - ПОКАЗЫВАЕМ ГЛАВНОЕ МЕНЮ
    await safe_answer_with_photo(
        call,
        BotImages.START_PHOTO,
        BotTexts.TEXTS.main_menu.format(username=call.from_user.mention_html()),
        reply_markup=await BotButtons.USERS_REPLY.main_menu(BotTexts, call.from_user.id, BotConfig.ADMINS)
    )            
    
 

@userRouter.callback_query(F.data == "back_to_user_menu")
async def back_to_user_menu(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    
    # Удаляем текущее inline сообщение
    try:
        await call.message.delete()
    except:
        pass
    
    # Отправляем главное меню (с Reply клавиатурой)
    await safe_answer_with_photo(
        call,
        BotImages.START_PHOTO,
        BotTexts.TEXTS.main_menu.format(username=call.from_user.mention_html()),
        reply_markup=await BotButtons.USERS_REPLY.main_menu(BotTexts, call.from_user.id, BotConfig.ADMINS),
        parse_mode='HTML'
    )
    
    await call.answer()


@userRouter.message(Command("start"))
async def command_start(msg: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    
    # 1. СНАЧАЛА ПРОВЕРЯЕМ ПОДПИСКУ НА КАНАЛЫ
    is_subscribed, channels_txt = await check_user_subscription(msg.from_user.id)
    
    if not is_subscribed:
        # Если не подписан - показываем требование подписки
        BotTexts = await utils.get_language(msg.from_user.id, DB)
        await msg.answer(
            BotTexts.TEXTS.channels_error.format(urls_txt=channels_txt), 
            reply_markup=(await BotButtons.USERS_INLINE.sub_kb(
                BotTexts, bot, BotConfig.CHANNELS_FOR_SUBSCRIBE
            )).as_markup(),
            parse_mode='HTML'
        )
        return
    
    # 2. ПОЛУЧАЕМ НАСТРОЙКИ ДЛЯ ПРОВЕРКИ MULTI_LANG
    settings = await DB.get_settings()
    
    # 3. ПРОВЕРЯЕМ СУЩЕСТВОВАНИЕ ПОЛЬЗОВАТЕЛЯ В БД
    user = await DB.get_user(user_id=msg.from_user.id)
    
    # Если пользователь новый (не существует в базе данных)
    if not user:
        # Проверяем, включена ли мультиязычность
        if settings.multi_lang:
            # Показываем выбор языка
            kb = BotButtons.USERS_INLINE.first_time_choose_language().as_markup()
            await msg.answer(
                """🌍 <b>Выберите язык / Choose language / Оберіть мову</b>

🇷🇺 Русский - для русскоязычных пользователей
🇺🇸 English - for English speakers  
🇺🇦 Українська - для україномовних користувачів""",
                reply_markup=kb,
                parse_mode='HTML'
            )
            return
        else:
            # Создаем пользователя с языком по умолчанию
            ref_id = None
            if msg.text and len(msg.text.split()) > 1:
                ref_link = msg.text.split()[1]
                if ref_link.isdigit():
                    ref_id = int(ref_link)
            
            await DB.register_user(
                user_id=msg.from_user.id,
                user_name=msg.from_user.username or "",
                full_name=msg.from_user.first_name or ""
            )
            
            # Логируем нового пользователя
            logger.info(f"🆕 Новый пользователь зарегистрирован: {msg.from_user.full_name} (@{msg.from_user.username or 'Нет'}) - ID: {msg.from_user.id}")
            
            # Отправляем уведомление админам если включено
            if settings.is_notify:
                try:
                    await utils.send_admins(
                        "new_user_alert", bot, DB,
                        name=msg.from_user.full_name,
                        user_id=msg.from_user.id
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления о новом пользователе: {e}")
            
            # Обновляем язык и реферала
            update_data = {"language": settings.default_lang}
            if ref_id:
                update_data["ref_by"] = ref_id
            
            await DB.update_user(msg.from_user.id, **update_data)
            
            # Получаем созданного пользователя
            user = await DB.get_user(user_id=msg.from_user.id)
    
    # 4. ПОЛУЧАЕМ ТЕКСТЫ ДЛЯ ЯЗЫКА ПОЛЬЗОВАТЕЛЯ
    BotTexts = await utils.get_language(msg.from_user.id, DB)
    
    # 5. ПРОВЕРЯЕМ ПРИНЯТИЕ ПОЛИТИКИ КОНФИДЕНЦИАЛЬНОСТИ
    if not user.privacy_accepted:
        # Загружаем политику из файла и разбиваем на страницы
        from tgbot.utils.utils import load_privacy_policy, split_text_to_pages
        
        privacy_text = load_privacy_policy()
        
        # Применяем форматирование Markdown -> HTML
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
        
        # Форматируем текст политики
        formatted_privacy = markdown_to_html(privacy_text)
        pages = split_text_to_pages(formatted_privacy, max_length=3800)
        
        # Сохраняем страницы в состоянии
        await state.update_data(privacy_pages=pages)
        
        # Показываем первую страницу
        if len(pages) > 1:
            page_text = f"""� <b>Политика конфиденциальности</b>

📝 <i>Страница 1 из {len(pages)}</i>

{pages[0]}"""
            kb = BotButtons.USERS_INLINE.privacy_policy_with_navigation_kb(BotTexts, 0, len(pages)).as_markup()
        else:
            page_text = f"""🔒 <b>Политика конфиденциальности</b>

{formatted_privacy}"""
            kb = BotButtons.USERS_INLINE.privacy_policy_kb(BotTexts).as_markup()
        
        await msg.answer(page_text, reply_markup=kb, parse_mode='HTML')
        return
    
    # 5. ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ - ПОКАЗЫВАЕМ ГЛАВНОЕ МЕНЮ
    kb = await BotButtons.USERS_REPLY.main_menu(BotTexts, msg.from_user.id, BotConfig.ADMINS)
    message_text = BotTexts.TEXTS.main_menu.format(username=msg.from_user.mention_html())
    settings = await DB.get_settings()
    if settings.is_ref:
        if not command.args:
            await safe_answer_with_photo(msg, BotImages.START_PHOTO, message_text, kb)
        else:
            reffer = await DB.get_user(user_id=command.args)
            if reffer is None:
                await safe_answer_with_photo(msg, BotImages.START_PHOTO, message_text, kb)
            else:
                if user.ref_id is not None:
                    await msg.answer(BotTexts.TEXTS.yes_reffer)
                else:
                    if reffer.user_id == msg.from_user.id:
                        await msg.answer(BotTexts.TEXTS.invite_yourself)
                    else:
                        await DB.update_user(user_id=msg.from_user.id, ref_id=reffer.user_id, ref_user_name=reffer.user_name, ref_full_name=reffer.full_name)
                        await DB.update_user(user_id=reffer.user_id, ref_count=reffer.ref_count + 1)

                        await bot.send_message(chat_id=reffer.user_id, text=BotTexts.TEXTS.new_refferal.format(user_name=user.user_name,
                                                       user_ref_count=reffer.ref_count + 1,
                                                       convert_ref=utils.numeral_noun_declension(reffer.ref_count + 1, BotTexts.TEXTS.ref_s)))

                        text, new_lvl, next_lvl, remain_refs, ref_lvl, isNewLvl = None, 1, 1, 1, 1, False
                        if int(reffer.ref_count) + 1 == int(settings.ref_lvl_2):
                            remain_refs = settings.ref_lvl_3 - (reffer.ref_count + 1)
                            ref_lvl, new_lvl, next_lvl, isNewLvl = 2, 2, 3, True
                        elif int(reffer.ref_count) + 1 == int(settings.ref_lvl_3):
                            ref_lvl, new_lvl, next_lvl, isNewLvl = 3, 3, 3, True
                            text = BotTexts.TEXTS.max_ref_lvl
                        
                        if isNewLvl:
                            if text is None:
                                text = BotTexts.TEXTS.new_ref_lvl.format(new_lvl=new_lvl, next_lvl=next_lvl, remain_refs=remain_refs,
                                                           convert_ref=utils.numeral_noun_declension(remain_refs, BotTexts.TEXTS.ref_s))
                            await bot.send_message(chat_id=reffer.user_id, text=text)
                            await DB.update_user(user_id=reffer.user_id, ref_lvl=ref_lvl)

                        await safe_answer_with_photo(msg, BotImages.START_PHOTO, message_text, kb)
    else:
        await safe_answer_with_photo(msg, BotImages.START_PHOTO, message_text, kb)


@userRouter.callback_query(F.data == "privacy_accept")
async def privacy_accept_callback(call: CallbackQuery, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработчик принятия политики конфиденциальности"""
    user_id = call.from_user.id
    
    # Обновляем статус принятия политики
    await DB.update_user(user_id=user_id, privacy_accepted=True)
    
    # Отправляем подтверждение
    await call.answer(BotTexts.TEXTS.privacy_accepted, show_alert=True)
    
    # Показываем главное меню
    kb = await BotButtons.USERS_REPLY.main_menu(BotTexts, user_id, BotConfig.ADMINS)
    message_text = BotTexts.TEXTS.main_menu.format(username=call.from_user.mention_html())
    
    # Удаляем старое сообщение
    try:
        await call.message.delete()
    except:
        pass
    
    # Отправляем новое сообщение с Reply клавиатурой и фото если есть
    from tgbot.data.loader import bot
    from aiogram.types.input_file import FSInputFile
    import os
    
    if BotImages.START_PHOTO:
        # Проверяем, это локальный файл или file_id/URL
        if isinstance(BotImages.START_PHOTO, str) and os.path.exists(BotImages.START_PHOTO):
            photo = FSInputFile(BotImages.START_PHOTO)
        else:
            photo = BotImages.START_PHOTO
        await bot.send_photo(chat_id=user_id, photo=photo, caption=message_text, reply_markup=kb)
    else:
        await bot.send_message(chat_id=user_id, text=message_text, reply_markup=kb)


@userRouter.callback_query(F.data == "privacy_decline")
async def privacy_decline_callback(call: CallbackQuery, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработчик отклонения политики конфиденциальности"""
    await call.answer(BotTexts.TEXTS.privacy_declined, show_alert=True)
    
    # Сообщаем, что нужно принять политику для использования бота
    await call.message.edit_text(
        "❌ Для использования бота необходимо принять политику конфиденциальности.",
        reply_markup=BotButtons.USERS_INLINE.privacy_policy_kb(BotTexts).as_markup()
    )


@userRouter.message(F.text == BTs.Ru.BUTTONS.profile)
@userRouter.message(F.text == BTs.Ua.BUTTONS.profile)
@userRouter.message(F.text == BTs.En.BUTTONS.profile)
async def profile_open(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    user = await DB.get_user(user_id=msg.from_user.id)
    settings = await DB.get_settings()
    total_refill = user.total_refill
    if settings.currency == models.Currencies.rub:
        balance = user.balance_rub
        tr = total_refill
    elif settings.currency == models.Currencies.usd:
        balance = user.balance_usd
        tr = await utils.get_exchange(total_refill, 'RUB', 'USD', DB)
    else:
        balance = user.balance_eur
        tr = await utils.get_exchange(total_refill, 'RUB', 'EUR', DB)
    text = BotTexts.TEXTS.profile_text.format(
        username=msg.from_user.mention_html(),
        user_id=msg.from_user.id,
        balance=f"{balance:.2f}",
        curr=BotConfig.CURRENCIES[settings.currency.value]['sign'],
        total_refill=f"{tr:.2f}",
        reg_date=user.reg_date,
    )
    await safe_answer_with_photo(msg, BotImages.PROFILE_PHOTO, text, (await BotButtons.USERS_INLINE.profile_menu(BotTexts)).as_markup())


@userRouter.callback_query(F.data == "profile")
async def profile(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.delete()
    user = await DB.get_user(user_id=call.from_user.id)
    settings = await DB.get_settings()
    if settings.currency == models.Currencies.rub:
        balance = user.balance_rub
        tr = user.total_refill
    elif settings.currency == models.Currencies.usd:
        balance = user.balance_usd
        tr = await utils.get_exchange(user.total_refill, 'RUB', 'USD', DB)
    else:
        balance = user.balance_eur
        tr = await utils.get_exchange(user.total_refill, 'RUB', 'EUR', DB)
    text = BotTexts.TEXTS.profile_text.format(
        username=call.from_user.mention_html(),
        user_id=call.from_user.id,
        balance=f"{balance:.2f}",
        curr=BotConfig.CURRENCIES[settings.currency.value]['sign'],
        total_refill=f"{tr:.2f}",
        reg_date=user.reg_date,
    )
    await safe_answer_with_photo(call.message, BotImages.PROFILE_PHOTO, text, (await BotButtons.USERS_INLINE.profile_menu(BotTexts)).as_markup())


@userRouter.message(F.text == BTs.Ru.BUTTONS.support)
@userRouter.message(F.text == BTs.En.BUTTONS.support)
@userRouter.message(F.text == BTs.Ua.BUTTONS.support)
async def open_support(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    settings = await DB.get_settings()
    if settings.support and settings.support != "-":
        text = BotTexts.TEXTS.support_text
        kb = (await BotButtons.USERS_INLINE.support(BotTexts)).as_markup()
    else:
        text = BotTexts.TEXTS.support_is_not_provided
        kb = BotButtons.USERS_INLINE.close(BotTexts).as_markup()

    await safe_answer_with_photo(msg, BotImages.SUPPORT_PHOTO, text, kb)
        

@userRouter.callback_query(F.data == "support")
async def open_support_callback(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    settings = await DB.get_settings()
    if settings.support and settings.support != "-":
        text = BotTexts.TEXTS.support_text
        kb = (await BotButtons.USERS_INLINE.support(BotTexts)).as_markup()
    else:
        text = BotTexts.TEXTS.support_is_not_provided
        kb = BotButtons.USERS_INLINE.custom_button(BotTexts, "back_to_user_menu").as_markup()

    await call.message.delete()
    await safe_answer_with_photo(call.message, BotImages.SUPPORT_PHOTO, text, kb)


@userRouter.message(F.text == BTs.En.BUTTONS.faq)
@userRouter.message(F.text == BTs.Ru.BUTTONS.faq)
@userRouter.message(F.text == BTs.Ua.BUTTONS.faq)
async def open_faq(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    settings = await DB.get_settings()
    if settings.faq and settings.faq != "-":
        text = str(settings.faq)  # Приводим к строке
        # Проверяем длину текста и разбиваем на страницы если нужно
        pages = utils.split_text_to_pages(text, 4000)  # Для обычного сообщения лимит 4096
        
        if len(pages) == 1:
            # Если одна страница - показываем обычно
            kb = (await BotButtons.USERS_INLINE.faq(BotTexts)).as_markup()
            await safe_answer_with_photo(msg, BotImages.FAQ_PHOTO, text, kb, parse_mode="HTML")
        else:
            # Несколько страниц - показываем первую с простой навигацией
            await state.update_data(faq_pages=pages, faq_current_page=1)
            from aiogram.utils.keyboard import InlineKeyboardBuilder
            from aiogram.types import InlineKeyboardButton
            
            builder = InlineKeyboardBuilder()
            nav_buttons = []
            nav_buttons.append(InlineKeyboardButton(text=f"1/{len(pages)}", callback_data="current_page"))
            if len(pages) > 1:
                nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"faq_user_page:2"))
            builder.row(*nav_buttons)
            
            # Обычные кнопки FAQ
            settings_kb = await BotButtons.USERS_INLINE.faq(BotTexts)
            for row in settings_kb.export():
                builder.row(*row)
            
            await msg.answer(f"📋 <b>FAQ</b> (стр. 1/{len(pages)})\n\n{pages[0]}", reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        return
        
@userRouter.callback_query(F.data == "faq")
@userRouter.callback_query(F.data == "faq")
async def open_faq_callback(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    settings = await DB.get_settings()
    if settings.faq and settings.faq != "-":
        text = str(settings.faq)
        # Проверяем длину текста и разбиваем на страницы
        pages = utils.split_text_to_pages(text, 4000)
        
        if len(pages) == 1:
            # Одна страница - обычный режим
            kb = (await BotButtons.USERS_INLINE.faq(BotTexts)).as_markup()
            await call.message.delete()
            await safe_answer_with_photo(call.message, BotImages.FAQ_PHOTO, text, kb, parse_mode="HTML")
        else:
            # Несколько страниц - с навигацией
            await state.update_data(faq_pages=pages, faq_current_page=1)
            from aiogram.utils.keyboard import InlineKeyboardBuilder
            from aiogram.types import InlineKeyboardButton
            
            builder = InlineKeyboardBuilder()
            nav_buttons = []
            nav_buttons.append(InlineKeyboardButton(text=f"1/{len(pages)}", callback_data="current_page"))
            if len(pages) > 1:
                nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"faq_user_page:2"))
            builder.row(*nav_buttons)
            
            # Обычные кнопки FAQ
            settings_kb = await BotButtons.USERS_INLINE.faq(BotTexts)
            for row in settings_kb.export():
                builder.row(*row)
            
            await call.message.edit_text(f"📋 <b>FAQ</b> (стр. 1/{len(pages)})\n\n{pages[0]}", reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        return


@userRouter.callback_query(F.data.startswith("faq_user_page:"))
async def faq_user_page_navigation(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """
    Обработчик навигации по страницам FAQ для пользователей
    """
    page = int(call.data.split(":")[1])
    
    data = await state.get_data()
    pages = data.get('faq_pages', [])
    
    if not pages:
        # Если нет сохраненных страниц, получаем их заново
        settings = await DB.get_settings()
        if settings.faq and settings.faq != "-":
            text = str(settings.faq)
            pages = utils.split_text_to_pages(text, 4000)
            await state.update_data(faq_pages=pages)
        else:
            return
    
    # Проверяем корректность номера страницы
    if page < 1:
        page = 1
    elif page > len(pages):
        page = len(pages)
    
    await state.update_data(faq_current_page=page)
    
    # Создаем клавиатуру навигации
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    nav_buttons = []
    
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"faq_user_page:{page - 1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"{page}/{len(pages)}", callback_data="current_page"))
    
    if page < len(pages):
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"faq_user_page:{page + 1}"))
    
    builder.row(*nav_buttons)
    
    # Обычные кнопки FAQ
    settings_kb = await BotButtons.USERS_INLINE.faq(BotTexts)
    for row in settings_kb.export():
        builder.row(*row)
    
    # Показываем страницу
    await call.message.edit_text(
        text=f"📋 <b>FAQ</b> (стр. {page}/{len(pages)})\n\n{pages[page - 1]}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@userRouter.message(F.text == BTs.Ru.BUTTONS.legal_documents)
@userRouter.message(F.text == BTs.En.BUTTONS.legal_documents)
@userRouter.message(F.text == BTs.Ua.BUTTONS.legal_documents)
async def legal_documents_menu(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработчик кнопки '📋 Документы' из Reply клавиатуры"""
    await state.clear()
    
    # Создаем inline клавиатуру с документами
    kb = BotButtons.USERS_INLINE.legal_documents_user_menu(BotTexts).as_markup()
    
    await msg.answer(
        f"📋 <b>{BotTexts.BUTTONS.legal_documents}</b>\n\n"
        f"Выберите документ для просмотра:",
        reply_markup=kb,
        parse_mode='HTML'
    )


@userRouter.message(F.text == BTs.Ru.BUTTONS.topup_balance)
@userRouter.message(F.text == BTs.En.BUTTONS.topup_balance)
@userRouter.message(F.text == BTs.Ua.BUTTONS.topup_balance)
async def topup_balance(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    settings = await DB.get_settings()
    enabled_payments = await DB.get_enabled_payments()
    if settings.is_refill and enabled_payments:
        await safe_answer_with_photo(msg, BotImages.TOPUP_BALANCE_PHOTO, BotTexts.TEXTS.choose_refill_method, (await BotButtons.USERS_INLINE.get_refill_kb(BotTexts, enabled_payments)).as_markup())
    else:
        await msg.answer(BotTexts.TEXTS.is_refill_text, reply_markup=BotButtons.USERS_INLINE.close(BotTexts).as_markup())

    
@userRouter.message(F.text == BTs.Ru.BUTTONS.buy)
@userRouter.message(F.text == BTs.En.BUTTONS.buy)
@userRouter.message(F.text == BTs.Ua.BUTTONS.buy)
async def buy(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    settings = await DB.get_settings()
    if settings.is_buy:
        categories = await DB.get_all_categories()
        if categories:
            await safe_answer_with_photo(msg, BotImages.BUY_PHOTO, BotTexts.TEXTS.available_cats, BotButtons.USERS_INLINE.select_category(BotTexts, categories).as_markup())
        else:
            await msg.answer(BotTexts.TEXTS.no_cats,
                             reply_markup=BotButtons.USERS_INLINE.close(BotTexts).as_markup())
    else:
        await msg.answer(BotTexts.TEXTS.is_buy_text, reply_markup=BotButtons.USERS_INLINE.close(BotTexts).as_markup())
        
        
@userRouter.callback_query(F.data == "buy")
async def buy_callback(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    settings = await DB.get_settings()
    if settings.is_buy:
        categories = await DB.get_all_categories()
        await call.message.delete()
        if categories:
            await safe_answer_with_photo(call.message, BotImages.BUY_PHOTO, BotTexts.TEXTS.available_cats, BotButtons.USERS_INLINE.select_category(BotTexts, categories).as_markup())
        else:
            await call.message.answer(BotTexts.TEXTS.no_cats,
                             reply_markup=BotButtons.USERS_INLINE.close(BotTexts).as_markup())
    else:
        await call.message.answer(BotTexts.TEXTS.is_buy_text, reply_markup=BotButtons.USERS_INLINE.close(BotTexts).as_markup())


@userRouter.callback_query(F.data == "close")
async def close_callback(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.delete()


@userRouter.callback_query(F.data == "ref_system")
async def ref_system(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    settings = await DB.get_settings()
    if settings.is_ref:
        await state.clear()
        bot_name = (await bot.get_me()).username
        user = await DB.get_user(user_id=call.from_user.id)

        match settings.currency.value:
            case "rub":
                ref_earn = user.ref_earn_rub
            case "usd":
                ref_earn = user.ref_earn_usd
            case "eur":
                ref_earn = user.ref_earn_eur

        ref_lvl = user.ref_lvl
        if ref_lvl == 1:
            lvl = settings.ref_lvl_2
            ref_percent = settings.ref_percent_1
        elif ref_lvl == 2:
            lvl = settings.ref_lvl_3
            ref_percent = settings.ref_percent_2
        else:
            lvl = settings.ref_lvl_3
            ref_percent = settings.ref_percent_3

        remain_refs = lvl - user.ref_count

        if ref_lvl == 3:
            mss = BotTexts.TEXTS.cur_max_lvl
        else:
            mss = BotTexts.TEXTS.next_lvl_remain.format(remain_refs=remain_refs, person_s=utils.numeral_noun_declension(remain_refs, BotTexts.TEXTS.person_s))

        if user.ref_full_name:
            reffer = f"<a href='tg://user?id={user.ref_id}'>{user.ref_full_name}</a>"
        else:
            reffer = BotTexts.TEXTS.nobody

        msg = BotTexts.TEXTS.ref_text.format(ref_link=f"<code>https://t.me/{bot_name}?start={call.from_user.id}</code>", ref_percent=ref_percent, 
                                    reffer=reffer, ref_earn=ref_earn, curr=BotConfig.CURRENCIES[settings.currency.value]['sign'], 
                                    convert_ref=utils.numeral_noun_declension(user.ref_count, BotTexts.TEXTS.ref_s), ref_count=user.ref_count, 
                                    ref_lvl=ref_lvl, mss=mss)
        await call.message.delete()
        await call.message.answer(msg, reply_markup=BotButtons.USERS_INLINE.custom_button(BotTexts, "profile").as_markup())
    else:
        await call.answer(BotTexts.TEXTS.is_ref_text, True)


@userRouter.callback_query(F.data == "activate_promo")
async def activate_promo(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.delete()
    await call.message.answer(BotTexts.TEXTS.promo_act, reply_markup=BotButtons.USERS_INLINE.custom_button(BotTexts, "profile").as_markup())
    await state.set_state(userStates.UserPromocodes.enter_promo)


@userRouter.message(StateFilter(userStates.UserPromocodes.enter_promo))
async def enter_promo(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    curr = (await DB.get_settings()).currency
    promocode = await DB.get_promocode(name=msg.text)

    if promocode:
        await state.clear()
        user = await DB.get_user(user_id=msg.from_user.id)
        active_promo = await DB.get_active_promocode(user_id=msg.from_user.id, promocode_name=promocode.name)
        if promocode.uses == 0:
            await msg.answer(BotTexts.TEXTS.no_uses_promocode)
            await DB.delete_promocode(promocode.name)
        elif active_promo:
            await msg.answer(BotTexts.TEXTS.yes_uses_promocode)
        else:
            # active_promo is None
            match curr.value:
                case "rub":
                    main_discount = promocode.discount_rub
                case "usd":
                    main_discount = promocode.discount_usd
                case "eur":
                    main_discount = promocode.discount_eur

            await DB.update_user(msg.from_user.id, 
                                 balance_rub=user.balance_rub + float(promocode.discount_rub), 
                                 balance_eur=user.balance_eur + float(promocode.discount_eur), 
                                 balance_usd=user.balance_usd + float(promocode.discount_usd))
            await DB.update_promocode(promocode.name, uses=promocode.uses - 1)
            await DB.activate_promocode(msg.from_user.id, promocode.name)
            await msg.answer(BotTexts.TEXTS.yes_promocode.format(discount=main_discount,
                                                         curr=BotConfig.CURRENCIES[curr.value]['sign']))
    else:
        await msg.answer(BotTexts.TEXTS.no_promocode.format(promocode=msg.text))
        
        
def format_purchase_message(purchase, position, price, currency_sign, BotTexts):
    """Форматирует сообщение о покупке"""
    if purchase.pos_id == 0:
        # Steam Points заказ
        return f"""🎮 <b>Steam Points</b>

🧾 <b>Номер заказа:</b> <code>{purchase.receipt}</code>
💎 <b>Товар:</b> {purchase.item}
💰 <b>Стоимость:</b> {price:.2f} {currency_sign}
📅 <b>Дата:</b> {purchase.date}"""
    else:
        # Обычный товар
        return BotTexts.TEXTS.receipt_purchase.format(
            receipt=purchase.receipt,
            pos_name=position.name if position else "Неизвестный товар",
            sum=price,
            curr=currency_sign,
            count=purchase.count,
            date=purchase.date
        )

@userRouter.callback_query(F.data == "purchases_history")
async def purchases_history(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    purchases = await DB.get_last_purchases(call.from_user.id, 20)  # Увеличиваем лимит
    settings = await DB.get_settings()
    
    if not purchases:
        await call.answer(BotTexts.TEXTS.no_have_purchases)
        return
    
    # Сохраняем покупки в состоянии для навигации
    await state.update_data(purchases=purchases, current_index=0)
    
    # Показываем первую покупку
    await show_purchase(call, state, BotTexts, 0)

async def show_purchase(call: CallbackQuery, state: FSMContext, BotTexts, index: int):
    """Показывает покупку по индексу"""
    data = await state.get_data()
    purchases = data.get('purchases', [])
    settings = await DB.get_settings()
    
    if index >= len(purchases):
        await call.answer("Покупка не найдена")
        return
    
    purchase = purchases[index]
    
    # Определяем цену
    match settings.currency.value:
        case "rub":
            price = purchase.price_rub
        case "usd":
            price = purchase.price_usd
        case "eur":
            price = purchase.price_eur
    
    currency_sign = BotConfig.CURRENCIES[settings.currency.value]['sign']
    
    # Получаем информацию о товаре
    position = None
    if purchase.pos_id != 0:
        position = await DB.get_position(pos_id=purchase.pos_id)
    
    # Форматируем сообщение
    message_text = format_purchase_message(purchase, position, price, currency_sign, BotTexts)
    
    # Определяем, есть ли файл для показа
    has_file = False
    if position and position.item_type in ['photo', 'file'] and purchase.item:
        items = [item for item in purchase.item.split("\n") if item.strip()]
        if items and ":::" in items[0]:
            parts = items[0].split(":::")
            if len(parts) >= 2 and parts[1].strip() and len(parts[1].strip()) > 10:
                has_file = True
    
    # Создаем клавиатуру
    keyboard = BotButtons.USERS_INLINE.purchases_navigation(
        BotTexts, 
        current_index=index, 
        total_purchases=len(purchases),
        purchase_id=purchase.receipt if has_file else None
    )
    
    # Отправляем или редактируем сообщение
    if index == 0:
        await call.message.delete()
        await call.message.answer(message_text, parse_mode='HTML', reply_markup=keyboard)
    else:
        await call.message.edit_text(message_text, parse_mode='HTML', reply_markup=keyboard)
    
    # Обновляем текущий индекс
    await state.update_data(current_index=index)

@userRouter.callback_query(F.data.startswith("purchase_prev:"))
async def purchase_previous(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Переход к предыдущей покупке"""
    index = int(call.data.split(":")[1])
    await show_purchase(call, state, BotTexts, index)

@userRouter.callback_query(F.data.startswith("purchase_next:"))
async def purchase_next(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Переход к следующей покупке"""
    index = int(call.data.split(":")[1])
    await show_purchase(call, state, BotTexts, index)

@userRouter.callback_query(F.data.startswith("show_purchase_file:"))
async def show_purchase_file(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Показывает файл покупки"""
    receipt = call.data.split(":")[1]
    data = await state.get_data()
    purchases = data.get('purchases', [])
    
    # Находим покупку по receipt
    purchase = None
    for p in purchases:
        if p.receipt == receipt:
            purchase = p
            break
    
    if not purchase:
        await call.answer("Покупка не найдена")
        return
    
    # Получаем информацию о товаре
    position = None
    if purchase.pos_id != 0:
        position = await DB.get_position(pos_id=purchase.pos_id)
    
    if not position or position.item_type not in ['photo', 'file']:
        await call.answer("Файл недоступен")
        return
    
    # Отправляем файл
    items = [item for item in purchase.item.split("\n") if item.strip()]
    if items and ":::" in items[0]:
        parts = items[0].split(":::")
        if len(parts) >= 2:
            data_text, file_id = parts[0], parts[1].strip()
            if file_id and len(file_id) > 10:
                try:
                    if position.item_type == "photo":
                        await call.message.answer_photo(photo=file_id, caption=data_text, parse_mode="None")
                    else:
                        await call.message.answer_document(document=file_id, caption=data_text, parse_mode="None")
                except Exception as e:
                    await call.answer("⚠️ Файл недоступен")
            else:
                await call.answer("⚠️ Файл недоступен")
        else:
            await call.answer("⚠️ Файл поврежден")
    else:
        await call.answer("⚠️ Файл недоступен")

@userRouter.callback_query(F.data == "search_purchase_receipt")
async def search_purchase_receipt(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Поиск покупки по чеку"""
    await call.message.edit_text(
        "🔍 <b>Поиск покупки по чеку</b>\n\n"
        "Введите номер чека для поиска:\n"
        "Например: <code>1234567890</code>\n\n"
        "💡 <i>Номер чека указан в сообщении о покупке</i>",
        reply_markup=BotButtons.USERS_INLINE.custom_button(BotTexts, "purchases_history").as_markup(),
        parse_mode='HTML'
    )
    
    await state.set_state(userStates.UserPurchases.enter_receipt)

@userRouter.message(StateFilter(userStates.UserPurchases.enter_receipt))
async def process_receipt_search(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработка поиска по чеку"""
    receipt = msg.text.strip()
    
    if not receipt:
        await msg.answer("❌ Введите номер чека")
        return
    
    # Ищем покупку по чеку
    purchase = await DB.get_purchase(receipt=receipt, user_id=msg.from_user.id)
    
    if not purchase:
        await msg.answer(
            f"❌ <b>Покупка не найдена</b>\n\n"
            f"Чек <code>{receipt}</code> не найден в вашей истории покупок.\n\n"
            f"💡 <i>Проверьте правильность номера чека</i>",
            reply_markup=BotButtons.USERS_INLINE.custom_button(BotTexts, "purchases_history").as_markup(),
            parse_mode='HTML'
        )
        await state.clear()
        return
    
    # Получаем настройки для валюты
    settings = await DB.get_settings()
    
    # Определяем цену
    match settings.currency.value:
        case "rub":
            price = purchase.price_rub
        case "usd":
            price = purchase.price_usd
        case "eur":
            price = purchase.price_eur
    
    currency_sign = BotConfig.CURRENCIES[settings.currency.value]['sign']
    
    # Получаем информацию о товаре
    position = None
    if purchase.pos_id != 0:
        position = await DB.get_position(pos_id=purchase.pos_id)
    
    # Форматируем сообщение
    message_text = format_purchase_message(purchase, position, price, currency_sign, BotTexts)
    
    # Определяем, есть ли файл для показа
    has_file = False
    if position and position.item_type in ['photo', 'file'] and purchase.item:
        items = [item for item in purchase.item.split("\n") if item.strip()]
        if items and ":::" in items[0]:
            parts = items[0].split(":::")
            if len(parts) >= 2 and parts[1].strip() and len(parts[1].strip()) > 10:
                has_file = True
    
    # Создаем клавиатуру
    keyboard = BotButtons.USERS_INLINE.purchases_navigation(
        BotTexts, 
        current_index=0, 
        total_purchases=1,
        purchase_id=purchase.receipt if has_file else None
    )
    
    await msg.answer(
        f"✅ <b>Покупка найдена!</b>\n\n{message_text}",
        parse_mode='HTML',
        reply_markup=keyboard
    )
    
    await state.clear()

@userRouter.callback_query(F.data == "noop")
async def noop_handler(call: CallbackQuery):
    """Обработчик для неактивных кнопок"""
    await call.answer()

@userRouter.callback_query(F.data.startswith("first_language:"))
async def first_language_choose(call: CallbackQuery, state: FSMContext):
    """Обработчик выбора языка новыми пользователями"""
    await state.clear()
    
    # Проверяем, включена ли мультиязычность
    settings = await DB.get_settings()
    if not settings.multi_lang:
        await call.answer("Выбор языка отключен администратором", show_alert=True)
        return
    
    # Проверяем подписку перед созданием пользователя
    is_subscribed, channels_txt = await check_user_subscription(call.from_user.id)
    
    if not is_subscribed:
        # Если не подписан - показываем требование подписки
        lang = settings.default_lang.value
        
        match lang:
            case "ru":
                BotTexts = BTs.Ru
            case "en":
                BotTexts = BTs.En
            case "ua":
                BotTexts = BTs.Ua
            case _:
                BotTexts = BTs.Ru
        
        await call.message.edit_text(
            BotTexts.TEXTS.channels_error.format(urls_txt=channels_txt), 
            reply_markup=(await BotButtons.USERS_INLINE.sub_kb(
                BotTexts, bot, BotConfig.CHANNELS_FOR_SUBSCRIBE
            )).as_markup(),
            parse_mode='HTML'
        )
        await call.answer()
        return
    
    language = call.data.split(":")[1]
    
    # Создаем пользователя с выбранным языком
    await DB.register_user(
        user_id=call.from_user.id,
        user_name=call.from_user.username or "None",  
        full_name=call.from_user.full_name
    )
    
    # Логируем нового пользователя
    logger.info(f"🆕 Новый пользователь зарегистрирован: {call.from_user.full_name} (@{call.from_user.username or 'Нет'}) - ID: {call.from_user.id}")
    
    # Отправляем уведомление админам если включено
    settings = await DB.get_settings()
    if settings.is_notify:
        try:
            await utils.send_admins(
                "new_user_alert", bot, DB,
                name=call.from_user.full_name,
                user_id=call.from_user.id
            )
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о новом пользователе: {e}")
    
    # Обновляем язык и политику
    await DB.update_user(
        user_id=call.from_user.id, 
        language=language,
        privacy_accepted=False  # Политика еще не принята
    )
    
    # Определяем тексты для выбранного языка
    match language:
        case "ru":
            BotTexts = BTs.Ru
        case "en":
            BotTexts = BTs.En
        case "ua":
            BotTexts = BTs.Ua
        case _:
            BotTexts = BTs.Ru  # По умолчанию русский
    
    # Загружаем политику из файла и разбиваем на страницы
    from tgbot.utils.utils import load_privacy_policy, split_text_to_pages
    
    privacy_text = load_privacy_policy()
    pages = split_text_to_pages(privacy_text, max_length=3800)
    
    # Сохраняем страницы в состоянии
    await state.update_data(privacy_pages=pages)
    
    # Показываем первую страницу политики на выбранном языке
    if len(pages) > 1:
        page_text = f"""📋 <b>Политика конфиденциальности</b>

📝 <i>Страница 1 из {len(pages)}</i>

{pages[0]}"""
        kb = BotButtons.USERS_INLINE.privacy_policy_with_navigation_kb(BotTexts, 0, len(pages)).as_markup()
    else:
        page_text = privacy_text
        kb = BotButtons.USERS_INLINE.privacy_policy_kb(BotTexts).as_markup()
    
    try:
        await call.message.edit_text(page_text, reply_markup=kb, parse_mode='HTML')
    except:
        await call.message.answer(page_text, reply_markup=kb, parse_mode='HTML')
    
    await call.answer()


@userRouter.callback_query(F.data.startswith("privacy_page:"))
async def privacy_page_navigation(call: CallbackQuery, state: FSMContext):
    """Навигация по страницам политики конфиденциальности"""
    page_num = int(call.data.split(":")[1])
    
    user_data = await state.get_data()
    pages = user_data.get("privacy_pages", [])
    
    if not pages or page_num >= len(pages):
        await call.answer("❌ Страница не найдена")
        return
    
    # Получаем тексты для языка пользователя
    BotTexts = await utils.get_language(call.from_user.id, DB)
    
    page_text = f"""� <b>Политика конфиденциальности</b>

📝 <i>Страница {page_num + 1} из {len(pages)}</i>

{pages[page_num]}"""
    
    kb = BotButtons.USERS_INLINE.privacy_policy_with_navigation_kb(BotTexts, page_num, len(pages)).as_markup()
    
    try:
        await call.message.edit_text(page_text, reply_markup=kb, parse_mode='HTML')
    except:
        await call.message.answer(page_text, reply_markup=kb, parse_mode='HTML')
    
    await call.answer()


# Переключение языка
@userRouter.callback_query(F.data == "change_language")
async def change_language(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    if not (await DB.get_settings()).multi_lang:
        return
    await call.message.delete()
    await call.message.answer(BotTexts.TEXTS.choose_language, 
                              reply_markup=BotButtons.USERS_INLINE.choose_language(BotTexts).as_markup())


@userRouter.callback_query(F.data.startswith("change_language:"))
async def change_language_choose(call: CallbackQuery, state: FSMContext):
    await state.clear()
    if not (await DB.get_settings()).multi_lang:
        return
    language = call.data.split(":")[1]
    await DB.update_user(user_id=call.from_user.id, language=language)
    
    match language:
        case "ru":
            NewLanguage = BTs.Ru
        case "en":
            NewLanguage = BTs.En
        case "ua":
            NewLanguage = BTs.Ua
    
    await call.message.delete()
    await safe_answer_with_photo(call.message, BotImages.START_PHOTO, NewLanguage.TEXTS.main_menu.format(username=call.from_user.mention_html()), await BotButtons.USERS_REPLY.main_menu(NewLanguage, call.from_user.id, BotConfig.ADMINS))


# Хендлер для автоматического предложения написать отзыв после покупки
async def prompt_review_after_purchase(user_id: int, receipt: str, product_name: str, price: float, currency: str):
    """Предлагает написать отзыв после успешной покупки"""
    from tgbot.keyboards.new_buttons import REVIEW_BUTTONS
    from tgbot.utils.utils import get_language
    
    BotTexts = await get_language(user_id, DB)
    
    # Проверяем, включена ли система отзывов
    review_settings = await DB.get_review_settings()
    if not review_settings or not review_settings.review_system_enabled:
        return
    
    # Проверяем, что отзыв еще не написан
    existing_review = await DB.get_review_by_receipt(receipt)
    if existing_review:
        return
    
    await bot.send_message(
        chat_id=user_id,
        text=BotTexts.TEXTS.purchase_completed.format(
            product_name=product_name,
            price=f"{price:.2f}",
            currency=currency,
            receipt=receipt
        ),
        reply_markup=REVIEW_BUTTONS.review_prompt_buttons(BotTexts, receipt).as_markup(),
        parse_mode='HTML'
    )
    


@adminRouter.message(Command(commands=['admin', 'adm', 'a']))
@adminRouter.message(F.text == BTs.Ru.BUTTONS.admin_panel)
@adminRouter.message(F.text == BTs.En.BUTTONS.admin_panel)
@adminRouter.message(F.text == BTs.Ua.BUTTONS.admin_panel)
async def admin_panel(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await msg.answer(BotTexts.ADMIN_TEXTS.welcome_to_the_admin_panel,
                     reply_markup=BotButtons.ADMIN_INLINE.admin_panel(BotTexts).as_markup())
    
    
@adminRouter.callback_query(F.data == "admin_panel")
async def admin_panel_callback(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.delete()
    await call.message.answer(BotTexts.ADMIN_TEXTS.welcome_to_the_admin_panel,
                     reply_markup=BotButtons.ADMIN_INLINE.admin_panel(BotTexts).as_markup())