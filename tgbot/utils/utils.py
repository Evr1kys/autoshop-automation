from tgbot.data.config import BotConfig, BotTexts
from tgbot.utils.models import Contest
from rates import get_def_exchanges

import time
import random
import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta

# Обновление курсов валют
async def check_rates(db, bot) -> None:
    rate_usd_to_rub, rate_usd_to_eur, rate_eur_to_rub, rate_eur_to_usd, rate_rub_to_usd, rate_rub_to_eur = await get_def_exchanges()

    await db.update_rates(usd_rub=rate_usd_to_rub, usd_eur=rate_usd_to_eur, eur_rub=rate_eur_to_rub,
                          eur_usd=rate_eur_to_usd, rub_usd=rate_rub_to_usd, rub_eur=rate_rub_to_eur)


# Перевести из одной валюты в другую
async def get_exchange(amount: float, cur1: str, cur2: str, db) -> float | int:
    try:
        rate_usd_to_rub, rate_usd_to_eur, rate_eur_to_rub, rate_eur_to_usd, rate_rub_to_usd, rate_rub_to_eur = await db.get_rates()

        if amount == 0:
            return 0
        if cur1.upper() == 'RUB' and cur2.upper() == 'USD':
            return round(float(rate_rub_to_usd * amount), 2)
        elif cur1.upper() == 'RUB' and cur2.upper() == 'EUR':
            return round(float(rate_rub_to_eur * amount), 2)
        elif cur1.upper() == 'USD' and cur2.upper() == 'RUB':
            return round(float(rate_usd_to_rub * amount), 2)
        elif cur1.upper() == 'EUR' and cur2.upper() == 'RUB':
            return round(float(rate_eur_to_rub * amount), 2)
        elif cur1.upper() == 'USD' and cur2.upper() == 'EUR':
            return round(float(rate_usd_to_eur * amount), 2)
        elif cur1.upper() == 'EUR' and cur2.upper() == 'USD':
            return round(float(rate_eur_to_usd * amount), 2)
    except Exception as e:
        print(e)


# Рассылка сообщения админам
async def send_admins(phrase, bot, db, is_phrase=True, is_channel=True, photo=None, file_id=None, **kwargs) -> None:
        if not BotConfig.LOGS_CHANNEL:
            is_channel = False
        
        if is_channel:
            texts = await get_language(BotConfig.ADMINS[0], db)
            if is_phrase:
                message = texts.ADMIN_TEXTS.__getattribute__(phrase).format(**kwargs)
            else:
                message = phrase
            
            # Проверяем длину caption для фото и документов (максимум 1024 символа)
            if photo or file_id:
                if len(message) > 1020:  # Оставляем запас
                    # Отправляем медиа без caption
                    if photo:
                        await bot.send_photo(BotConfig.LOGS_CHANNEL, photo=photo)
                    if file_id:
                        await bot.send_document(BotConfig.LOGS_CHANNEL, document=file_id)
                    # Затем отправляем текст отдельным сообщением
                    await bot.send_message(BotConfig.LOGS_CHANNEL, text=message)
                else:
                    # Обычная отправка с caption
                    if photo:
                        await bot.send_photo(BotConfig.LOGS_CHANNEL, photo=photo, caption=message)
                    if file_id:
                        await bot.send_document(BotConfig.LOGS_CHANNEL, document=file_id, caption=message)
            else:
                await bot.send_message(BotConfig.LOGS_CHANNEL, text=message)
        else:
            # Импортируем DB здесь, чтобы избежать циклической зависимости
            from tgbot.data.config import DB
            for admin in BotConfig.ADMINS:
                texts = await get_language(admin, DB)
                if is_phrase:
                    message = texts.ADMIN_TEXTS.__getattribute__(phrase).format(**kwargs)
                else:
                    message = phrase
                
                # Проверяем длину caption для фото и документов (максимум 1024 символа)
                if photo or file_id:
                    if len(message) > 1020:  # Оставляем запас
                        # Отправляем медиа без caption
                        if photo:
                            await bot.send_photo(admin, photo=photo)
                        if file_id:
                            await bot.send_document(admin, document=file_id)
                        # Затем отправляем текст отдельным сообщением
                        await bot.send_message(admin, text=message)
                    else:
                        # Обычная отправка с caption
                        if photo:
                            await bot.send_photo(admin, photo=photo, caption=message)
                        if file_id:
                            await bot.send_document(admin, document=file_id, caption=message)
                else:
                    await bot.send_message(admin, text=message)


# Получение текущего unix-времени
def get_unix(full: bool = False) -> float | int:
    if full:
        return time.time_ns()
    else:
        return int(time.time())


# Получение текущей даты
def get_date() -> str:
    this_date = datetime.today().replace(microsecond=0)
    this_date = this_date.strftime("%d.%m.%Y %H:%M:%S")

    return this_date


# Получение даты из unix timestamp
def get_date_from_unix(unix_timestamp: int) -> str:
    """Конвертирует unix timestamp в читаемую дату"""
    try:
        date_obj = datetime.fromtimestamp(unix_timestamp)
        return date_obj.strftime("%d.%m.%Y %H:%M:%S")
    except (ValueError, OSError):
        return "Неверная дата"


# Склонение слов в зависимости от числа
def numeral_noun_declension(number: int, words: tuple) -> str:
    nominative_singular, genetive_singular, nominative_plural = words
    return (
        (number in range(5, 20)) and nominative_plural or
        (1 in (number, (diglast := number % 10))) and nominative_singular or
        ({number, diglast} & {2, 3, 4}) and genetive_singular or nominative_plural
    )
    
    
# Разбив списка на несколько частей
def split_messages(get_list: list, count: int) -> list[list]:
    return [get_list[i:i + count] for i in range(0, len(get_list), count)]


# Получение списка каналов из строки
def get_channels(channels):
    try:
        if channels is None or channels == "-":
            return []
        
        channels = str(channels)
        if "," in channels:
            channels = channels.split(",")
        else:
            if len(channels) >= 1:
                channels = [channels]
            else:
                channels = []
        while "" in channels:
            channels.remove("")
        while " " in channels:
            channels.remove(" ")

        channels = list(map(int, channels))

        return channels
    except Exception as err:
        print(err)
        return []
    

# Получение читаемого формата времени для конца розыгрыша
def get_time_for_end_contest(contest: Contest, day_s: str) -> str:
    contest_time = contest.end_time - time.time()
    today = datetime.today()
    new_time = today + timedelta(seconds=contest_time)
    end_time = str(new_time - today).split(".")[0]
    if "days" in end_time or "day" in end_time:
        if "days" in end_time:
            end_time = end_time.replace(
                "days",
                numeral_noun_declension(int(end_time.split(" days")[0]), day_s)    
            )
        else:
            end_time = end_time.replace(
                "day",
                numeral_noun_declension(int(end_time.split(" day")[0]), day_s)    
            )
    return end_time


# Закончить розыгрыш
async def end_contest(contest: Contest, db, bot):
    currency = contest.currency.value
    cur = BotConfig.CURRENCIES[currency]['sign']
    all_members = await db.get_contest_members_id(contest.contest_id)
        
    winners_num = contest.winners_num
    
    if winners_num > len(all_members):
        winners_num = len(all_members)
        
    winners_ids = []
    if len(all_members) == 0:
        await db.delete_contest(contest.contest_id)
        return await send_admins("contest_is_finished_and_members_are_zero_alert", bot, db,
            prize=contest.prize,
            cur=cur
        )

    if winners_num == 1:
        random.shuffle(all_members)
        winners_ids.append(random.choice(all_members))
    else:
        while len(winners_ids) <= (winners_num - 1):
            random.shuffle(all_members)
            winner_id = random.choice(all_members)
            if winner_id in winners_ids:
                continue
            else:
                winners_ids.append(winner_id)
    
    await db.delete_contest(contest.contest_id)
    for winner in winners_ids:
        user = await db.get_user(user_id=winner)
        
        member = await bot.get_chat(winner)
        await send_admins("contest_is_finished_alert", bot, db, prize=contest.prize, cur=cur)
        await send_admins(f"<b><a href='tg://user?id={member.id}'>{member.full_name}</a> [<code>{member.id}</code>]</b>", bot, db, False)
        await send_admins("prize_given", bot, db)
        match currency:
            case "rub":
                balance_rub = user.balance_rub + contest.prize
                balance_usd = user.balance_usd + await get_exchange(contest.prize, "RUB", "USD", db)
                balance_eur = user.balance_eur + await get_exchange(contest.prize, "RUB", "EUR", db)
            case "usd":
                balance_usd = user.balance_usd + contest.prize
                balance_rub = user.balance_rub + await get_exchange(contest.prize, "USD", "RUB", db)
                balance_eur = user.balance_eur + await get_exchange(contest.prize, "USD", "EUR", db)
            case "eur":
                balance_eur = user.balance_eur + contest.prize
                balance_rub = user.balance_rub + await get_exchange(contest.prize, "EUR", "RUB", db)
                balance_usd = user.balance_usd + await get_exchange(contest.prize, "EUR", "USD", db)
    
        await db.update_user(user_id=winner,balance_rub=balance_rub, 
                             balance_usd=balance_usd, balance_eur=balance_eur)
        try:
            texts = await get_language(winner, db)
            await bot.send_message(winner, texts.TEXTS.u_win_the_contest.format(
                prize=contest.prize, cur=cur
            ))
        except:
            pass


# Проверка розыгрышей на конец
async def check_contests(db, bot) -> None:
    while True:
        await asyncio.sleep(3)
        contests = await db.get_all_contests()
        if not contests:
            continue
        for contest in contests:
            contest_id = contest.contest_id
            now_time = time.time()
            members = await db.get_contest_members_id(contest_id)
            if len(members) == contest.members_num:
                await end_contest(contest, db, bot)
            elif contest.end_time < now_time:
                await end_contest(contest, db, bot)
            else:
                continue
            



# Получение класса языка для пользователя
async def get_language(user_id: int, db) -> BotTexts.Ru | BotTexts.En | BotTexts.Ua:
    settings = await db.get_settings()
    lang = settings.default_lang.value
    if settings.multi_lang:
        user = await db.get_user(user_id=user_id)
        if user:
            lang = user.language.value
        
    match lang:
        case "ru":
            return BotTexts.Ru
        case "en":
            return BotTexts.En
        case "ua":
            return BotTexts.Ua
        
        
# Проверка обновлений 
async def check_updates() -> None:
    async with aiohttp.ClientSession() as session:
        ress = await session.get(f'https://sites.google.com/view/tosa-projects/главная-страница')
        res = await ress.text()
        soup = bs(res, "html.parser")
        res2 = soup.findAll('p', class_='zfr3Q CDt4Ke')
        ress = str(res2[1])
        res3 = ress.split("Актуальная версия: ")[1]
        current_version = res3.split('</span></p>')[0]
        if BotConfig.BOT_VERSION != current_version:
            msg = f"""
<b>❗❗❗ Обновление AutoShop'а ❗❗❗

🧩 Ваша текущая версия: <code>{BotConfig.BOT_VERSION}</code>
⭐ Новая версия: <code>{current_version}</code>

https://lolz.live/threads/4980786/
https://lolz.live/threads/4980786/
https://lolz.live/threads/4980786/

<u>Данное оповещение видят только администраторы бота!</u></b>
                """
            await send_admins(msg, bot, db, False)
            
            
# Автоматическая очистка ежедневной статистики после 00:00
async def clear_stats_day(db) -> None:
    await db.update_settings(profit_day=get_unix())
    

# Автоматическая очистка еженедельной статистики в понедельник 00:00
async def clear_stats_week(db) -> None:
    await db.update_settings(profit_week=get_unix())


def split_text_to_pages(text: str, max_length: int = 3500) -> list[str]:
    """
    Разбивает длинный текст на страницы с учетом лимита Telegram
    Оптимальный размер для документов с учетом заголовков
    """
    if len(text) <= max_length:
        return [text]
    
    pages = []
    current_page = ""
    
    # Разбиваем по абзацам
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        # Если один абзац слишком длинный, разбиваем по предложениям
        if len(paragraph) > max_length:
            sentences = paragraph.split('. ')
            for i, sentence in enumerate(sentences):
                if i < len(sentences) - 1:
                    sentence += '. '
                
                if len(current_page + sentence) > max_length:
                    if current_page:
                        pages.append(current_page.strip())
                        current_page = sentence
                    else:
                        # Если даже одно предложение слишком длинное
                        words = sentence.split(' ')
                        for word in words:
                            if len(current_page + word + ' ') > max_length:
                                if current_page:
                                    pages.append(current_page.strip())
                                    current_page = word + ' '
                                else:
                                    pages.append(word)
                            else:
                                current_page += word + ' '
                else:
                    current_page += sentence
        else:
            # Обычный абзац
            if len(current_page + paragraph + '\n\n') > max_length:
                if current_page:
                    pages.append(current_page.strip())
                    current_page = paragraph + '\n\n'
                else:
                    pages.append(paragraph)
            else:
                current_page += paragraph + '\n\n'
    
    if current_page.strip():
        pages.append(current_page.strip())
    
    return pages


async def safe_send_photo(message_or_call, photo, text, reply_markup=None, parse_mode="HTML"):
    """
    Безопасная отправка фото с учетом ограничений Telegram на длину caption (1024 символа)
    Если photo пустое или None, отправляет только текст
    Автоматически обрабатывает локальные файлы через FSInputFile
    """
    from aiogram.types.input_file import FSInputFile
    import os
    
    # Если это CallbackQuery, то берем message из него
    if hasattr(message_or_call, 'message'):
        message = message_or_call.message
    else:
        message = message_or_call
    
    # Если фото не указано или пустое, отправляем только текст
    if not photo or photo.strip() == "":
        return await message.answer(
            text=text, 
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    
    max_caption_length = 1020  # Оставляем небольшой запас
    
    try:
        # Определяем тип фото (локальный файл, URL или file_id)
        photo_input = photo
        if os.path.exists(photo):
            # Локальный файл - используем FSInputFile
            photo_input = FSInputFile(photo)
        elif photo.startswith(('http://', 'https://')):
            # HTTP URL - используем как есть
            photo_input = photo
        # Иначе считаем что это file_id - используем как есть
        
        if len(text) <= max_caption_length:
            # Текст помещается в caption
            return await message.answer_photo(
                photo=photo_input, 
                caption=text, 
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        else:
            # Текст слишком длинный для caption, сокращаем его
            # Обрезаем до максимальной длины caption с добавлением "..."
            truncated_text = text[:max_caption_length-3] + "..."
            return await message.answer_photo(
                photo=photo_input, 
                caption=truncated_text, 
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
    except Exception as e:
        # Если ошибка с фото, отправляем только текст
        print(f"Ошибка отправки фото: {e}")
        return await message.answer(
            text=text, 
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )


def load_privacy_policy() -> str:
    """
    Загружает политику конфиденциальности из файла privacy_policy.md
    """
    import os
    
    try:
        # Список возможных путей для поиска файла
        possible_paths = [
            # 1. В папке legal_docs относительно текущей рабочей директории
            os.path.join(os.getcwd(), 'legal_docs', 'privacy_policy.md'),
            # 2. Относительно текущей рабочей директории
            os.path.join(os.getcwd(), 'privacy_policy.md'),
            # 3. Относительно корня проекта (3 уровня вверх от utils.py)
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'legal_docs', 'privacy_policy.md'),
            # 4. Относительно корня проекта (3 уровня вверх от utils.py)
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'privacy_policy.md'),
            # 5. Прямо в текущей директории
            'privacy_policy.md'
        ]
        
        content = None
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✅ Файл privacy_policy.md найден по пути: {path}")
                break
        
        if content:
            return content.strip()  # Убираем BOM и лишние пробелы
        else:
            print("❌ Файл privacy_policy.md не найден ни по одному из путей:")
            for path in possible_paths:
                print(f"  - {path}")
            return """🔒 <b>Политика конфиденциальности</b>

❌ <b>Документ временно недоступен</b>

Извините, файл с политикой конфиденциальности временно недоступен. 
Обратитесь в поддержку для получения актуальной информации."""
            
    except Exception as e:
        print(f"Ошибка загрузки политики конфиденциальности: {e}")
        return """🔒 <b>Политика конфиденциальности</b>

❌ <b>Ошибка загрузки документа</b>

Произошла ошибка при загрузке политики конфиденциальности. 
Обратитесь в техподдержку."""


def load_terms_of_service() -> str:
    """
    Загружает условия пользования из файла terms_of_service.md
    """
    import os
    
    try:
        # Список возможных путей для поиска файла
        possible_paths = [
            # 1. В папке legal_docs относительно текущей рабочей директории
            os.path.join(os.getcwd(), 'legal_docs', 'terms_of_service.md'),
            # 2. Относительно текущей рабочей директории
            os.path.join(os.getcwd(), 'terms_of_service.md'),
            # 3. Относительно корня проекта (3 уровня вверх от utils.py)
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'legal_docs', 'terms_of_service.md'),
            # 4. Относительно корня проекта (3 уровня вверх от utils.py)
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'terms_of_service.md'),
            # 5. Прямо в текущей директории
            'terms_of_service.md'
        ]
        
        content = None
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✅ Файл terms_of_service.md найден по пути: {path}")
                break
        
        if content:
            return content.strip()  # Убираем BOM и лишние пробелы
        else:
            print("❌ Файл terms_of_service.md не найден ни по одному из путей:")
            for path in possible_paths:
                print(f"  - {path}")
            return """📜 <b>Условия пользования</b>

❌ <b>Документ временно недоступен</b>

Извините, файл с условиями пользования временно недоступен. 
Обратитесь в поддержку для получения актуальной информации."""
            
    except Exception as e:
        print(f"Ошибка загрузки условий пользования: {e}")
        return """📜 <b>Условия пользования</b>

❌ <b>Ошибка загрузки документа</b>

Произошла ошибка при загрузке условий пользования. 
Обратитесь в техподдержку."""


def load_user_agreement() -> str:
    """
    Загружает пользовательское соглашение из файла user_agreement.md
    """
    import os
    
    try:
        # Список возможных путей для поиска файла
        possible_paths = [
            # 1. В папке legal_docs относительно текущей рабочей директории
            os.path.join(os.getcwd(), 'legal_docs', 'user_agreement.md'),
            # 2. Относительно текущей рабочей директории
            os.path.join(os.getcwd(), 'user_agreement.md'),
            # 3. Относительно корня проекта (3 уровня вверх от utils.py)
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'legal_docs', 'user_agreement.md'),
            # 4. Относительно корня проекта (3 уровня вверх от utils.py)
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'user_agreement.md'),
            # 5. Прямо в текущей директории
            'user_agreement.md'
        ]
        
        content = None
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✅ Файл user_agreement.md найден по пути: {path}")
                break
        
        if content:
            return content.strip()  # Убираем BOM и лишние пробелы
        else:
            print("❌ Файл user_agreement.md не найден ни по одному из путей:")
            for path in possible_paths:
                print(f"  - {path}")
            return """📄 <b>Пользовательское соглашение</b>

❌ <b>Документ временно недоступен</b>

Извините, файл с пользовательским соглашением временно недоступен. 
Обратитесь в поддержку для получения актуальной информации."""
            
    except Exception as e:
        print(f"Ошибка загрузки пользовательского соглашения: {e}")
        return """📄 <b>Пользовательское соглашение</b>

❌ <b>Ошибка загрузки документа</b>

Произошла ошибка при загрузке пользовательского соглашения. 
Обратитесь в техподдержку."""


async def safe_answer_with_photo(message_context, photo, text, reply_markup=None, parse_mode="HTML"):
    """
    Универсальная функция для отправки сообщений с фото или без него
    message_context может быть Message или CallbackQuery
    """
    # Определяем, что у нас: Message или CallbackQuery
    if hasattr(message_context, 'message'):
        # Это CallbackQuery
        message = message_context.message
        chat_id = message.chat.id
        bot_instance = message.bot
    else:
        # Это Message
        message = message_context
        chat_id = message.chat.id
        bot_instance = message.bot
    
    # Если фото не указано или пустое, отправляем только текст
    if not photo or photo.strip() == "":
        return await bot_instance.send_message(
            chat_id=chat_id,
            text=text, 
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    
    # Если есть фото, пытаемся отправить с фото
    try:
        from aiogram.types.input_file import FSInputFile
        import os
        
        # Определяем тип фото (локальный файл, URL или file_id)
        photo_input = photo
        if os.path.exists(photo):
            # Локальный файл - используем FSInputFile
            photo_input = FSInputFile(photo)
        elif photo.startswith(('http://', 'https://')):
            # HTTP URL - используем как есть
            photo_input = photo
        # Иначе считаем что это file_id - используем как есть
        
        max_caption_length = 1020
        if len(text) <= max_caption_length:
            return await bot_instance.send_photo(
                chat_id=chat_id,
                photo=photo_input, 
                caption=text, 
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        else:
            # Текст слишком длинный, отправляем отдельно
            await bot_instance.send_photo(chat_id=chat_id, photo=photo_input)
            return await bot_instance.send_message(
                chat_id=chat_id,
                text=text, 
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
    except Exception as e:
        # Если ошибка с фото, отправляем только текст
        print(f"Ошибка отправки фото: {e}")
        return await bot_instance.send_message(
            chat_id=chat_id,
            text=text, 
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )


# ===== Steam API автоматические функции =====

async def check_steam_api_status(db, bot) -> None:
    """Автоматическая проверка статуса Steam API и обновление данных"""
    try:
        from tgbot.utils.error_monitoring import log_steam_api_event
        
        steam_config = await db.get_steam_config()
        if not steam_config or not steam_config.is_enabled:
            return
        
        # Проверяем и обновляем цену
        await update_steam_price(db, bot)
        
        # Проверяем баланс API
        await check_steam_balance(db, bot)
        
        log_steam_api_event("Курсы Steam API успешно обновлены")
        
    except Exception as e:
        from tgbot.utils.error_monitoring import log_steam_api_event
        log_steam_api_event(f"Ошибка проверки Steam API: {e}", "error")
        
        # Уведомляем админов об ошибке
        try:
            await send_admins("steam_api_error", bot, db, error=str(e))
        except:
            pass


async def update_steam_price(db, bot) -> float | None:
    """Обновляет ТОЛЬКО api_price_per_point из API, НЕ трогает цену администратора"""
    try:
        from tgbot.utils.error_monitoring import log_steam_api_event
        
        # Получаем API цену (это НЕ меняет цену для пользователей!)
        api_price = await db.get_steam_api_price()
        if api_price:
            log_steam_api_event(f"API цена Steam Points обновлена: {api_price:.6f} ₽ за очко")
            return api_price
        else:
            log_steam_api_event("Не удалось обновить API цену Steam Points", "warning")
            return None
    except Exception as e:
        from tgbot.utils.error_monitoring import log_steam_api_event
        log_steam_api_event(f"Ошибка обновления API цены Steam: {e}", "error")
        return None


async def check_steam_balance(db, bot) -> float | None:
    """Проверяет баланс Steam API и автоматически отключает систему при низком балансе"""
    try:
        from tgbot.utils.error_monitoring import log_steam_api_event
        
        balance = await db.get_steam_api_balance()
        steam_config = await db.get_steam_config()
        
        if balance is None:
            log_steam_api_event("Не удалось получить баланс Steam API", "warning")
            return None
        
        # Проверяем, нужно ли отключить систему при низком балансе
        if (steam_config.auto_disable_on_low_balance and 
            balance < steam_config.low_balance_threshold):
            
            # Отключаем систему Steam Points
            await db.update_steam_config(is_enabled=False)
            
            # Уведомляем админов
            try:
                await send_admins(
                    "steam_low_balance", bot, db,
                    balance=balance,
                    threshold=steam_config.low_balance_threshold
                )
                log_steam_api_event(f"Steam API отключен: баланс {balance} ниже порога {steam_config.low_balance_threshold}", "error")
            except Exception as e:
                log_steam_api_event(f"Ошибка отправки уведомления о низком балансе: {e}", "error")
                
        else:
            # Balance уже в рублях, логируем только важные изменения
            api_price = steam_config.api_price_per_point or 0.005
            balance_points = balance / api_price if api_price > 0 else 0
            log_steam_api_event(f"Баланс Steam API: {balance:.2f} ₽ ({balance_points:.0f} очков)")
        
        return balance
        
    except Exception as e:
        from tgbot.utils.error_monitoring import log_steam_api_event
        log_steam_api_event(f"Ошибка проверки баланса Steam API: {e}", "error")
        return None


async def enable_steam_if_balance_sufficient(db, bot) -> bool:
    """Включает Steam API если баланс достаточный и система была отключена автоматически"""
    try:
        from tgbot.utils.error_monitoring import log_steam_api_event
        
        steam_config = await db.get_steam_config()
        if not steam_config:
            return False
            
        # Проверяем баланс только если система выключена и включено авто-управление
        if not steam_config.is_enabled and steam_config.auto_disable_on_low_balance:
            balance = await db.get_steam_api_balance()
            
            if balance and balance >= steam_config.low_balance_threshold * 1.2:  # 20% запас
                # Включаем систему
                await db.update_steam_config(is_enabled=True)
                
                # Уведомляем админов
                try:
                    await send_admins(
                        "steam_balance_restored", bot, db,
                        balance=balance,
                        threshold=steam_config.low_balance_threshold
                    )
                    log_steam_api_event(f"Steam API включен: баланс {balance} восстановлен")
                except Exception as e:
                    log_steam_api_event(f"Ошибка отправки уведомления о восстановлении баланса: {e}", "error")
                
                return True
        
        return False
        
    except Exception as e:
        from tgbot.utils.error_monitoring import log_steam_api_event
        log_steam_api_event(f"Ошибка при попытке включить Steam API: {e}", "error")
        return False


def safe_html_text(text: str) -> str:
    """
    Безопасная обработка HTML текста - удаляет потенциально проблемные теги
    """
    if not text:
        return ""
    
    import html
    import re
    
    # Экранируем HTML символы
    safe_text = html.escape(text, quote=False)
    
    # Удаляем незакрытые или некорректные blockquote теги
    safe_text = re.sub(r'<blockquote[^>]*>(?![^<]*</blockquote>)', '', safe_text, flags=re.IGNORECASE)
    safe_text = re.sub(r'</blockquote>(?![^<]*<blockquote)', '', safe_text, flags=re.IGNORECASE)
    
    # Удаляем другие потенциально проблемные теги
    dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form']
    for tag in dangerous_tags:
        safe_text = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', '', safe_text, flags=re.IGNORECASE | re.DOTALL)
        safe_text = re.sub(rf'<{tag}[^>]*>', '', safe_text, flags=re.IGNORECASE)
    
    return safe_text