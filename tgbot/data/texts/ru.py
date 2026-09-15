class Language:
    def __init__(self):
        self.language = "ru"
    
    class Buttons:
        buy = "💸 Купить"
        profile = "👤 Профиль"
        support = "💎 Поддержка"
        faq = "❓ FAQ"
        topup_balance = "💰 Пополнить баланс"
        back = "◀ Назад"
        contests = "🎁 Розыгрыши"
        faq_chat_inl = "💎 Чат"
        faq_news_inl = "📩 Новостной"
        steam_points = "🎮 Steam Points"  # Новая кнопка
        reviews = "⭐ Отзывы"             # Новая кнопка
        
        # Legal documents
        legal_documents = "📋 Документы"
        terms_of_service = "📜 Условия пользования"
        privacy_policy = "🔒 Политика конфиденциальности"
        user_agreement = "📄 Пользовательское соглашение"

        #  Inline
        send_payment_to_check = "✅ Отправить платеж на проверку"
        close = "❌ Закрыть"
        activate_promo = "📢 Активировать промо"
        ref_system = "👥 Реферальная система"
        purchases_history = "🛒 История покупок"
        support_text = "🔗 Написать в поддержку"
        refill_link_inl = "💵 Перейти к оплате"
        refill_check_inl = "💎 Проверить оплату"
        cancel = "❌ Отменить"
        admin_panel = "⚙ Панель администратора"
        choose_action = "Выберите действие"
        position_button_name = "{name} | {price}{curr} | {items}"
        nolimit = "Безлимит"
        pcs = "шт."
        contest_enter = '🎉 Участвовать'
        you_not_completed_all_conditions = "❗ Вы не выполнили все условия! Выполнено {count} из {count_conditions}"
        change_language = "🌐 Изменить язык"
        check_sub = "✅ Проверить"
        
        # Privacy policy buttons
        privacy_accept_btn = "✅ Принять"
        privacy_decline_btn = "❌ Отклонить"
        
        # Reviews buttons
        write_review = "✍️ Написать отзыв"
        view_reviews = "👀 Посмотреть отзывы"
        my_reviews = "📝 Мои отзывы"
        leave_review_now = "⭐ Оставить отзыв"
        review_later = "⏰ Позже"
        rate_1_star = "⭐ 1 звезда"
        rate_2_stars = "⭐⭐ 2 звезды"
        rate_3_stars = "⭐⭐⭐ 3 звезды"
        rate_4_stars = "⭐⭐⭐⭐ 4 звезды"
        rate_5_stars = "⭐⭐⭐⭐⭐ 5 звезд"
        
        # Steam Points buttons
        steam_100 = "🎮 100 очков"
        steam_500 = "🎮 500 очков"
        steam_1000 = "🎮 1000 очков"
        steam_2500 = "🎮 2500 очков"
        steam_5000 = "🎮 5000 очков"
        steam_custom = "🎮 Другое количество"
        my_reviews = "📝 Мои отзывы"
        review_later = "⏰ Напомнить позже"
        leave_review_now = "✍️ Оставить отзыв сейчас"
        rate_1_star = "⭐"
        rate_2_stars = "⭐⭐"
        rate_3_stars = "⭐⭐⭐"
        rate_4_stars = "⭐⭐⭐⭐"
        rate_5_stars = "⭐⭐⭐⭐⭐"
        
        # Steam Points buttons
        steam_100 = "100 очков"
        steam_500 = "500 очков"
        steam_1000 = "1000 очков"
        steam_2500 = "2500 очков"
        steam_5000 = "5000 очков"
        steam_custom = "💎 Другое количество"
        steam_balance_check = "💰 Проверить баланс API"
        
        

    class Texts:

        #######################################
        #  Min/Max Amount of refill (IN RUB)  #
        #                                     #
        min_amount = 5                        #
        max_amount = 100000                   #
        #                                     #
        #                                     #
        #######################################

        is_buy_text = "❌ Покупки временно недоступны!"
        is_ban_text = f"❌ Вы были заблокированы в боте!"
        is_work_text = f"❌ Бот находиться на тех. работах!"
        is_refill_text = f"❌ Пополнения временно недоступны!"
        is_ref_text = f"❗ Реферальная система временно недоступна!"
        is_contests_text = f"❌ Розыгрыши временно недоступны!"
        channels_error = """
<b>❌ Ошибка!\n\nВы подписались не на все каналы:

{urls_txt}</b>
    """

        nobody = "<code>Никто</code>"
        ref_s = ('реферал', 'реферала', 'рефералов') # не трогать скобки
        day_s = ('день', 'дня', "дней") # не трогать скобки
        member_s = ("участник", "участника", "участников") # не трогать скобки
        winner_s = ("победитель", "победителя", "победителей") # не трогать скобки
        refill_s = ("пополнение", "пополнения", "пополнений") # не трогать скобки
        purchase_s = ("покупка", "покупки", "покупок") # не трогать скобки
        channel_s = ('канал', 'канала', 'каналов') # не трогать скобки
        person_s = ('человек', "человека", "человек")

        main_menu = """
<b>👩‍💻 {username}, Спасибо что пользуетесь нашим Магазином

Главное меню:</b>"""
        
        privacy_policy_text = """
<b>🔒 Политика конфиденциальности</b>

Добро пожаловать в наш магазин!

Для использования бота необходимо согласиться с нашей политикой конфиденциальности и условиями пользования.

<b>Мы собираем следующие данные:</b>
• Ваш Telegram ID
• Имя пользователя и имя
• История покупок и пополнений
• Реферальная информация

<b>Мы НЕ собираем:</b>
• Данные банковских карт
• Пароли или приватные ключи
• Личную переписку

<b>Ваши данные используются для:</b>
• Обработки заказов
• Реферальной системы
• Технической поддержки
• Улучшения сервиса

Нажимая кнопку "Согласен", вы подтверждаете, что ознакомились и согласны с политикой конфиденциальности."""
        
        privacy_accepted = "✅ Спасибо! Теперь вы можете пользоваться ботом."
        privacy_declined = "❌ Для использования бота необходимо согласиться с политикой конфиденциальности."
        
        bot_will_not_respond = "❗ Бот не будет отвечать до прекращения спама."
        please_dont_spam = "❗ Пожалуйста, не спамьте."
        
        profile_text = """
<b>👤 Ваш Профиль:

💎 Юзер: {username}
🆔 ID: <code>{user_id}</code>

💰 Баланс: <code>{balance}{curr}</code>
💵 Всего пополнено: <code>{total_refill}{curr}</code>

📌 Дата регистрации: <code>{reg_date}</code></b>"""
        support_is_not_provided = "<b>💎 На данный момент нет актуальной поддержки!</b>"
        support_text = "<b>💎 Чтобы написать поддержке, нажмите на кнопку снизу:</b>"
        choose_language = "<b>❗ Выберите язык / Choose language:</b>"
        refill_check_no = "❌ Оплата не найдена"
        payments_names = {
            "lolz": "💚 Lolzteam",
            "payok": "🟡 PayOK",
            "aaio": "💳 Aaio",
            'yoomoney': "🟣 ЮMoney",
            'lava': "⭐ Lava",
            'cryptoBot': "💡 CryptoBot",
            'crystalPay': "💎 CrystalPay",
            'cryptomus': "🖤 Cryptomus",
            'pal24': "🅿️ PAL24 СБП",
            'platega': "🏦 СБП"
        }
        choose_refill_method = "<b>💰 Выберите способ пополнения:</b>"
        payment_comment_api = "Пополнение аккаунта {user_name} на сумму {pay_amount}{curr} в боте @{bot_name}"
        refill_was_rejected = "<b>❌ Ваше пополнение на {amount}{curr} было отклонено!</b>"
        send_receipt_photo = "<b>🧾 Отправьте фото чека перевода:</b>"
        confirm_send_receipt_photo = "<b>❓ Вы уверены, что хотите отправить этот чек на проверку?</b>"
        create_refill_text = """
<b>⭐ Пополнение через: <code>{paymentMethod}</code>
💰 Сумма: <code>{pay_amount}{curr}</code>
🆔 ID платежа: <code>{pay_id}</code>
⌛ Вы должны оплатить счет до <code>{under_date}</code>
💎 Чтобы оплатить нажмите на кнопку внизу:</b>"""
        cancel_create_refill_text = """
<b>❗ У вас уже есть активное пополнение:

⭐ Пополнение через: <code>{paymentMethod}</code>
💰 Сумма: <code>{pay_amount}{curr}</code>
🆔 ID платежа: <code>{pay_id}</code>
⌛ Вы должны оплатить счет до <code>{under_date}</code>
💎 Чтобы оплатить нажмите на кнопку внизу:</b>"""
        create_refill_text_custom_pay_method = """
<b>⭐ Пополнение через: <code>{paymentMethod}</code>
💰 Сумма: <code>{pay_amount}{curr}</code>
🆔 ID платежа: <code>{pay_id}</code>
⌛ Вы должны оплатить счет до <code>{under_date}</code></b>

{custom_pay_method_text}"""
        cancel_create_refill_text_custom_pay_method = """
<b>❗ У вас уже есть активное пополнение:

⭐ Пополнение через: <code>{paymentMethod}</code>
💰 Сумма: <code>{pay_amount}{curr}</code>
🆔 ID платежа: <code>{pay_id}</code>
⌛ Вы должны оплатить счет до <code>{under_date}</code></b>

{custom_pay_method_text}"""
        enter_amount_of_refill = "<b>❗ Введите сумму пополнения:</b>"
        choose_crypto = "<b>⚙️ Выберите криптовалюту:</b>"
        error_refill = "❌ Ошибка, пополнение уже произошло!"
        success_refill_text = """
<b>⭐ Вы успешно пополнили баланс на сумму <code>{amount}{curr}</code>
💎 Способ: <code>{way}</code>
🧾 Чек: <code>{receipt}</code></b>
"""
        yes_refill_ref = "<b>💎 Ваш реферал {name} пополнил баланс на <code>{amount}{cur}</code> и с этого вам зачислено <code>{ref_amount}{cur}</code></b>"
        yes_cancel_refill = "<b>❌ Пополнение отменено</b>"
        no_int_amount = "<b>❗ Сумма пополнения должна быть числом!</b>"
        min_max_amount = "<b>❗ Сумма пополнения должна быть больше или равна <code>{min_amount}{curr}</code> но меньше или равна <code>{max_amount}{curr}</code></b>"
        new_ref_lvl = "<b>💚 У вас новый реферальный уровень, {new_lvl}! До {next_lvl} уровня осталось {remain_refs} {convert_ref}</b>"
        max_ref_lvl = f"<b>💚 У вас новый реферальный уровень, 3! Максимальный уровень!</b>"
        cur_max_lvl = f"💚 У вас максимальный уровень!</b>"
        next_lvl_remain = "💚 До следующего уровня осталось пригласить <code>{remain_refs} {person_s}</code>.</b>"
        ref_text = """<b>💎 Реферальная система

🔗 Ссылка:
{ref_link}

📔 Наша реферальная система позволит вам заработать крупную сумму без вложений. Вам необходимо лишь давать свою ссылку друзьям и вы будете получать пожизненно <code>{ref_percent}%</code> с их пополнений в боте.


⚙️ Вас пригласил: {reffer}
💵 Всего заработано <code>{ref_earn}{curr}</code> с рефералов
📌 Всего у вас <code>{ref_count}</code> {convert_ref}
🎲 Реферальный уровень: <code>{ref_lvl}</code>
{mss}"""
        yes_reffer = f"<b>❗ У вас уже есть рефер!</b>"
        invite_yourself = "<b>❗ Вы не можете пригласить себя</b>"
        new_refferal = "<b>💎 У вас новый реферал! @{user_name} \n" \
                    "⚙️ Теперь у вас <code>{user_ref_count}</code> {convert_ref}!</b>"
        promo_act = "<b>📩 Для активации промокода напишите его название</b>\n" \
                    "<b>⚙️ Пример: promo2025</b>"
        no_uses_promocode = "<b>❌ Вы не успели активировать промокод!</b>"
        no_promocode = "<b>❌ Промокода <code>{promocode}</code> не существует!</b>"
        yes_promocode = "<b>✅ Вы успешно активировали промокод и получили <code>{amount}{curr}</code>!</b>"
        yes_uses_promocode = "<b>❌ Вы уже активировали данный промокод!</b>"
        no_cats = f"<b>❌ К сожалению в данный момент нет категорий :(</b>"
        available_cats = f"<b>🛒 Доступные на данный момент категории:</b>"
        current_cat = "<b>🚀 Текущая категория: <code>{name}</code>:</b>"
        no_products = f"❌ К сожалению в данный момент нет товаров :("
        open_position_text = """
<b>💎 Категория: <code>{cat_name}</code>

🛍️ Товар: <code>{pos_name}</code>
💰 Стоимость: <code>{price}{cur}</code>
⚙️ Доступное кол-во: <code>{items}</code></b>

{desc}"""
        no_balance_for_buying = "❗ У вас недостаточно средств для покупки. Пополните баланс!"
        confirm_buy_products = """
<b>❓ Вы действительно хотите купить товар(ы)?</b>

- Товар: <code>{position_name}</code>
- Количество: <code>{count}шт</code>
- Сумма к покупке: <code>{price}{curr}</code>
"""
        enter_count_items_for_buy = """
<b>❗ Введите количество товаров для покупки</b>
⚠️ От <code>1</code> до <code>{items}</code>

- Товар: <code>{pos_name}</code> - <code>{price}{curr}</code>
- Ваш баланс: <code>{balance}{curr}</code>
"""
        incorrect_data = "<b>❌ Данные были введены неверно</b>"
        data_was_edit = "<b>❗ Товар который вы хотели купить, закончился</b>"
        incorrect_count_items = "<b>❌ Неверное количество товаров</b>"
        no_balance_on_account = "<b>❌ Недостаточно средств на счете</b>"
        please_await_products = "<b>🔄 Ждите, товары подготавливаются</b>"
        successful_buying = """
<b>✅ Вы успешно купили товар(ы)</b>

- Чек: <code>{receipt}</code>
- Товар: <code>{position_name} | {purchase_count}шт | {purchase_price}{curr}</code>
- Дата покупки: <code>{date}</code>
"""
        receipt_purchase = """
<b>⭐ Чек <code>{receipt}</code>:
📌 Товар: <code>{pos_name}</code>
💰 Сумма: <code>{sum}{curr}</code>
🛒 Количество: <code>{count}шт</code>
🎲 Дата: <code>{date}</code>
🔗 Содержимое:</b>
        """
        last_10_purchases = "<b>🚀 Последние 10 покупок</b>"
        no_have_purchases = "❗ У вас нет еще не одной покупки!"
        your_items = "<b>🛒 Ваши товары</b>"
        no_contests = "❌ Сейчас не проходит ни одного розыгрыша!"
        choose_contest = "<b>🎉 Выберите один из розыгрышей:</b>"
        contest_text = """
<b>🎉 Розыгрыш #{contest_id}

💰 Сумма: <code>{prize}{cur}</code>

🕒 Конец через <code>{end_time}</code>

🎉 {winners_num} {winners}
👥 {members_num} {members}</b>"""
        conditions = "\n\n<b>❗ Условия: </b>\n\n"
        conditions_refills = '<b>💳 {num} {refills} - {status}</b>\n'
        conditions_purchases = '<b>🛒 {num} {purchases} - {status}</b>\n'
        conditions_channels = '<b>✨ Подписаться на {num} {channels_text}: \n\n{channels}</b>\n'
        u_win_the_contest = "<b>🎉 Поздравляю, вы выиграли в розыгрыше! \n💰 Приз в размере {prize}{cur} был выдан!</b>"
        u_didnt_have_time_to_enter_contest = "Вы не успели принять участие! 💥"
        success = "✅ Успешно"
        u_already_enter_contest = "❌ Вы уже участвуете!"
        contest_already_ended = "💥 Розыгрыш уже завершен!"
        
        # ===== Тексты для системы отзывов =====
        review_system_title = """⭐ <b>Система отзывов</b>

Здесь вы можете:
• 📝 Оставить отзыв о купленных товарах
• 👀 Посмотреть отзывы других покупателей
• 📋 Управлять своими отзывами

Отзывы помогают другим покупателям сделать правильный выбор!"""
        
        no_reviews = "📭 <b>Пока нет отзывов</b>\n\nБудьте первым, кто оставит отзыв об этом товаре!"
        
        my_reviews_empty = """📝 <b>Мои отзывы</b>

У вас пока нет отзывов. Оставьте отзыв о купленных товарах!"""
        
        my_reviews_title = "📝 <b>Мои отзывы</b>"
        
        review_item = """⭐ <b>{rating}/5</b> | 📅 {date}
📦 <b>{product_name}</b>
💬 {review_text}
👍 Полезно: {helpful_count}

"""
        
        reviews_for_product = """📦 <b>{product_name}</b>
⭐ Средний рейтинг: <b>{avg_rating}/5</b>
📊 Всего отзывов: <b>{total_reviews}</b>

{reviews_list}"""
        
        review_prompt = """⭐ <b>Оставить отзыв</b>

Товар: <b>{product_name}</b>

Пожалуйста, оцените товар от 1 до 5 звезд:"""
        
        review_text_prompt = """⭐ <b>Оценка: {rating}</b>

Теперь напишите отзыв о товаре (или отправьте "-" чтобы пропустить):

📝 Минимум символов: {min_length}
📝 Максимум символов: {max_length}"""
        
        review_text_too_short = "❌ <b>Отзыв слишком короткий!</b>\n\nМинимум символов: {min_length}"
        
        review_text_too_long = "❌ <b>Отзыв слишком длинный!</b>\n\nМаксимум символов: {max_length}"
        
        review_submitted = """✅ <b>Отзыв отправлен!</b>

Ваша оценка: {rating} ⭐

Спасибо за отзыв! Он поможет другим покупателям."""
        
        review_already_exists = "❌ <b>Отзыв уже существует</b>\n\nВы уже оставили отзыв об этом товаре."
        
        purchase_completed = """✅ <b>Покупка завершена!</b>

📦 Товар: <b>{product_name}</b>
💰 Сумма: <b>{price:.2f} {currency}</b>
🧾 Чек: <code>{receipt}</code>

⭐ Хотите оставить отзыв о товаре?"""
        
        # ===== Тексты для Steam Points =====
        steam_points_description = """🎮 <b>Steam Points</b>

Пополните свой Steam аккаунт очками для покупки предметов в Steam!

✨ <b>Преимущества:</b>
• 🚀 Мгновенное пополнение
• 💰 Выгодные цены
• 🔒 Безопасные транзакции
• 🎯 Точное количество очков

Выберите количество очков для покупки:"""
        
        steam_points_amount = """🎮 <b>Steam Points</b>

📊 Количество: <b>{points} очков</b>
💰 Стоимость: <b>{price:.2f} {currency}</b>
📈 Курс: <b>{rate} {currency}/очко</b>

Теперь введите ссылку на ваш Steam профиль:"""
        
        steam_custom_amount = """🎮 <b>Пользовательское количество</b>

Введите количество Steam очков для покупки:

📏 Минимум: <b>{min_points}</b> очков
📏 Максимум: <b>{max_points}</b> очков
⚠️ Количество должно быть кратно 100"""
        
        steam_amount_invalid = """❌ <b>Некорректное количество!</b>

📏 Минимум: <b>{min_points}</b> очков
📏 Максимум: <b>{max_points}</b> очков
⚠️ Количество должно быть кратно 100"""
        
        steam_link_invalid = """❌ <b>Некорректная ссылка Steam!</b>

Пожалуйста, введите корректную ссылку на ваш Steam профиль:

✅ <code>https://steamcommunity.com/id/ваш_ник</code>
✅ <code>https://steamcommunity.com/profiles/76561198xxxxxxxxx</code>"""
        
        steam_insufficient_funds = """❌ <b>Недостаточно средств!</b>

💰 Ваш баланс: <b>{balance:.2f} {currency}</b>
💸 Требуется: <b>{required:.2f} {currency}</b>

Пополните баланс для продолжения."""
        
        steam_order_confirm = """🎮 <b>Подтверждение заказа</b>

🔗 Steam профиль: <code>{steam_link}</code>
📊 Количество: <b>{points} очков</b>
💰 Стоимость: <b>{price:.2f} {currency}</b>

Подтвердите заказ:"""
        
        steam_processing = """🔄 <b>Обработка заказа...</b>

Пополняем ваш Steam аккаунт на <b>{points} очков</b>

⏳ Пожалуйста, подождите..."""
        
        steam_success = """✅ <b>Steam Points успешно пополнены!</b>

🔗 Steam профиль: <code>{steam_link}</code>
📊 Получено: <b>{points} очков</b>
💰 Потрачено: <b>{total_cost:.2f} {currency}</b>
📈 Было очков: <b>{before_points}</b>
📈 Стало очков: <b>{after_points}</b>

🧾 Чек: <code>{receipt}</code>
📅 Дата: <b>{date}</b>

Спасибо за покупку! 🎮"""
        
        steam_error = """❌ <b>Ошибка при пополнении</b>

{error}

Попробуйте позже или обратитесь в поддержку."""
        
        steam_insufficient_balance = """❌ <b>Недостаточно средств на балансе API</b>

Пополнение временно недоступно. Попробуйте позже."""


    class AdminTexts:
        ### Buttons:
        back = "◀ Назад"
        main_settings = "🖤 Общие настройки"
        extra_settings = "🎲 Доп. настройки"
        switchers = "❗ Выключатели"
        statistic = "📊 Статистика"
        find = "🔍 Искать"
        products_manage = "💎 Управление товарами"
        mail = "📌 Рассылка"
        payments_systems = "💰 Платежные системы"
        ad_buttons = "💫 Рекламные кнопки"
        mail_buttons = "🧩 Кнопки в рассылке"
        contests = "🎉 Розыгрыши"
        reviews_management = "⭐ Управление отзывами"
        steam_management = "🎮 Steam Points"

        main_settings_values = {
            "faq": "FAQ",
            "support": "Тех. Поддержка",
            "ref_percent_1": "Реф. Процент 1 лвл",
            "ref_percent_2": "Реф. Процент 2 лвл",
            "ref_percent_3": "Реф. Процент 3 лвл",
            "currency": "Валюта бота",
            "default_lang": "Язык по умолчанию",
            "chat": "Чат",
            "news": "Новостной канал",
            "refill_commission_percent": "Комиссия за пополнение (%)",
        }
        currencies = {
            "rub": "Рубль",
            "usd": "Доллар",
            "eur": "Евро",
        }
        switchers_settings = {
            "tech_works": "Тех. Работы",
            "buys": "Покупки",
            "refills": "Пополнения",
            "ref": "Реф. Система",
            "contests": "Розыгрыши",
            "multi_lang": "Мульти язычность",
            "notify": "Увед. о новых юзерах",
            "sub": "Проверка подписки",
            "keyboard": "Главное меню",
            
        }
        create_promocode = "💎 Создать промокод"
        delete_promocode = "🎲 Удалить промокод"
        edit_number_of_refs_for_ref_lvl_2 = "2️⃣ Изменить кол-во рефералов для 2 лвла"
        edit_number_of_refs_for_ref_lvl_3 = "3️⃣ Изменить кол-во рефералов для 3 лвла"
        add_category = "➕ | Категорию"
        edit_category = "⚙️ | Категорию"
        del_all_categories = "🗑️ | ВСЕ Категории"
        add_subcategory = "➕ | Подкатегорию"
        edit_subcategory = "⚙️ | Подкатегорию"
        del_all_subcategories = "🗑️ | ВСЕ Подкатегории"
        add_position = "➕ | Позицию"
        edit_position = "⚙️ | Позицию"
        del_all_positions = "🗑️ | ВСЕ Позиции"
        add_items = "➕ | Товары"
        del_item = "🗑️ | Товар"
        del_all_items = "🗑️ | ВСЕ Товары"
        delete = "🗑️ Удалить"
        name = "📘 Название"
        move = "🔁 Переместить"
        select_this_category = "💎 Выбрать эту категорию"
        photo = "📸 Фото"
        text = "📝 Текст"
        file_ = "📁 Файл"
        price = "💰 Цена"
        description = "📑 Описание"
        position_type_text = "🪙 Тип позиции"
        clear_items = "🗑️ Очистить товары"
        get_items = "🧾 Получить список товаров"
        upload_items = "🔰 Загрузить товары"
        create = "➕ Создать"
        current_buttons = "📑 Текущие кнопки"
        open_category_button = "🌐 Кнопка открытия категории"
        open_subcategory_button = "🔰 Кнопка открытия подкатегории"
        open_position_button = "🛒 Кнопка открытия позиции"
        open_contest_button = "🎉 Кнопка открытия розыгрыша"
        link_button = "🔗 Кнопка-ссылка"
        mail_buttons_types = {
            "link": link_button,
            "category": open_category_button,
            "subcategory": open_subcategory_button,
            "position": open_position_button,
            "contest": open_contest_button
        }
        stop_upload_items = "❌ Закончить загрузку товаров"
        profile = "👤 Профиль"
        receipt = "🧾 Чек"
        edit_balance = "💰 Редактировать баланс"
        unban = "⛔ Разблокировать"
        ban = "⛔ Заблокировать"
        send_message = "⭐ Отправить сообщение"
        add_balance = "➕ Выдать баланс"
        minus_balance = "➖ Снять баланс"
        edit_bal = "⚙️ Изменить баланс"
        get_users_and_their_balances = "Получить юзеров и их баланс > 0"
        get_users_ids = "Получить список ID пользователей"
        winners_count = "✨ Кол-во победителей"
        prize = "💰 Приз"
        conditions = "🚀 Условия"
        members_count = "💥 Кол-во участников"
        contest_time = "⌚ Время розыгрыша"
        end_contest_now = "❌ Закончить розыгрыш сейчас"
        start_contest = "⭐ Начать розыгрыш"
        purchases_count = "🛒 Кол-во покупок"
        refills_count = "💳 Кол-во пополнений"
        channels_ids_for_sub = "💎 ID Каналов для подписки | Кол-во:"
        edit_custom_pay_method_name = "⚙️ Изменить название способа"
        edit_custom_pay_method_text = "📖 Изменить текст при пополнении"
        edit_custom_pay_method_min_amount = "🚀 Изменить минимальную сумму для пополнения"
        edit_custom_pay_method_receipt = "Просить чек перед отправкой на проверку | {status}"
        enable = "✅ Включить"
        disable = "❌ Выключить"
        get_balance = "💰 Узнать баланс"
        show_info = "📌 Показать информацию"
        
        ### Texts:
        new_refill_custom_pay_method_alert = """
<b>🧾 Пользователь {username} [<code>{user_id}</code>] отправил платеж на проверку:

Сумма: <code>{amount}{curr}</code>

✅ - Одобрить платеж
❌ - Отклонить платеж</b>"""
        enter_new_name_for_custom_pay_method = "<b>⚙️ Введите новое название для кастомного способа оплаты. \nТекущее: {name}</b>"
        enter_new_min_for_custom_pay_method = "<b>⚙️ Введите новый минимум для кастомного способа оплаты. \nТекущий: {min}{curr}</b>"
        enter_new_text_for_custom_pay_method = "<b>⚙️ Введите новый текст для кастомного способа оплаты. \nТекущий: \n</b>{text}"
        payment_info_custom_pay_method = """
<b>{method}</b>

Статус: <code>{status}</code>
Минимальная сумма для пополнения: <code>{min}{curr}</code>
Предпросмотр пополнения:
{preview_refill}"""
        success = "<b>✅ Успешно!</b>"
        edit_number_of_refs_for_ref_lvl_alert = "<b>❗ Администратор  {username} изменил кол-во рефералов для <code>{lvl}</code> уровня на <code>{count} {convert}</code></b>"
        you_edit_number_of_refs_for_ref_lvl = "<b>✅ Вы изменили кол-во рефералов для <code>{lvl}</code> уровня на <code>{count} {convert}</code></b>"
        this_promo_is_not_exits = "<b>❌ Такого промокода не существует! Попробуйте снова:</b>"
        this_promo_is_already_exists = "<b>❌ Промокод с таким названием уже существует! Введите другое название:</b>"
        promo_is_deleted_alert = "<b>❗ Администратор {username} удалил Промокод <code>{name}</code></b>"
        promo_is_deleted = "<b>✅ Промокод <code>{name}</code> успешно удалён!</b>"
        promo_is_created_alert = "<b>❗ Администратор {username} создал Промокод <code>{name}</code> с кол-вом использований <code>{uses}</code> и суммой <code>{amount}{curr}</code></b>"
        promo_is_created = "<b>✅ Промокод <code>{name}</code> с кол-вом использований <code>{uses}</code> и суммой <code>{amount}{curr}</code> был создан!</b>"
        value_is_no_number = "<b>❗ Значение должно быть числом! Попробуйте еще раз:</b>"
        enter_amount_for_promo = "<b>❗ Введите сумму (Деньги зачислятся после ввода промокода)</b>"
        now_enter_number_of_uses_for_promo = "<b>❗ Теперь введите кол-во использований промокода:</b>"
        enter_new_number_of_refs_for_ref_lvl = "<b>❗ Введите новое кол-во рефералов для {lvl} уровня:</b>"
        enter_promo_name_for_delete = "<b>❗ Введите названия промокода для удаления:</b>"
        enter_promo_name_for_create = "<b>❗ Введите названия нового промокода:</b>"
        choose_action = "<b>❗ Выберите действие:</b>"
        new_user_alert = "<b>💎 Зарегистрирован новый пользователь {name} [<code>{user_id}</code>]</b>"
        edit_main_setting = """
<b>Изменение <code>{action}</code>
Текущее значение: 
{value}

Введите новое значение:</b>
    """
        choose_new_currency = "<b>❗ Выберите новую валюту бота: \n\nP.S. При смене валюты цены на товары конвертируются из текущей валюты в новую.</b>"
        choose_new_default_language = "<b>❗ Выберите новый язык по умолчанию:</b>"
        welcome_to_the_admin_panel = "<b>🎉 Добро пожаловать в панель администратора:</b>"
        main_settings_text = "<b>⚙️ Основные настройки бота:</b>"
        choose_what_you_want_to_enable_disable = "<b>⚙️ Выберите что хотите выключить/включить \n❌ - Выкл. | ✅ - Вкл.</b>"
        refill_log = """
<b>💰 Произошло пополнение баланса!
👤 Пользователь: {user_mention} [<code>{user_id}</code>]
💵 Сумма пополнения: <code>{pay_amount}{curr}</code>
🧾 Чек: <code>{pay_id}</code>
⚙️ Способ: <code>{way}</code>{external_id_info}</b>
    """
        steam_points_purchase_log = """
<b>🎮 Покупка Steam Points!
👤 Пользователь: <a href="tg://user?id={user_id}">{full_name}</a> [<code>{user_id}</code>]
🔗 Steam профиль: <code>{steam_link}</code>
💎 Очки доставлены: <b>{points}</b>
💰 Стоимость: <b>{total_cost} {currency}</b>
📊 Баланс очков: {before_points} → {after_points}
🧾 Номер заказа: <code>{receipt}</code></b>
    """
        products_manage_text = """
<b>⚙️ Выберите что хотите сделать:
<blockquote>➕ - Добавить/Создать 
⚙️ - Редактировать 
🗑️ - Удалить</blockquote></b>
        """
        add_category_text = "<b>❗ Введите название для категории:</b>"
        category_is_created_alert = "<b>❗ Администратор {username} создал категорию с названием <code>{name}</code>!</b>"
        no_categories_available = "❌ Нет доступных категорий! Создайте хотя бы одну!"
        select_category = "<b>❗ Выберите категорию:</b>"
        category_text = """
<b>💎 Категория: <code>{name}</code>
🆔 ID: <code>{cat_id}</code>
❗ Выберите, что хотите изменить:</b>
        """
        enter_new_name_for_category = "<b>❗ Введите новое названия для категории <code>{name}</code></b>"
        category_is_edited_alert = "<b>❗ Администратор {username} изменил название категории с <code>{old_name}</code> на <code>{new_name}</code>!</b>"
        confirm_category_delete = "<b>❓ Вы уверены, что хотите удалить категорию <code>{name}</code>?</b>"
        category_is_deleted_alert = "<b>❗ Администратор {username} удалил категорию с названием <code>{name}</code>!</b>"
        del_all_categories_text = "<b>❓ Вы уверены, что хотите удалить <u>ВСЕ</u> категории?</b>"
        all_categories_are_deleted_alert = "<b>❗ Администратор {username} удалил <u>ВСЕ</u> категории!</b>"
        enter_name_for_subcategory = "<b>❗ Введите названия для подкатегории:</b>"
        name_error = "<b>❌ Максимальная длина названия <code>64</code> символа! Попробуйте еще раз:</b>"
        description_error = "<b>❌ Максимальная длина описания <code>2000</code> символов! Попробуйте еще раз:</b>"
        subcategory_is_created_alert = "<b>❗ Администратор {username} создал подкатегорию с названием <code>{name}</code> в категории <code>{cat_name}</code>!</b>"
        no_subcategories_available = "❌ Нет доступных подкатегорий! Создайте хотя бы одну!"
        no_subcategories_available_in_this_category = "❌ Нет доступных подкатегорий в этой категории! Создайте хотя бы одну!"
        no_positions_available_in_this_category = "❌ Нет доступных позиций в этой категории! Создайте хотя бы одну!"
        no_positions_available = "❌ Нет доступных позиций! Создайте хотя бы одну!"
        no_positions_available_in_this_subcategory = "❌ Нет доступных позиций в этой подкатегории! Создайте хотя бы одну!"
        select_subcategory = "<b>❗ Выберите подкатегорию:</b>"
        subcategory_text = """
<b>💎 Подкатегория: <code>{name}</code>
🆔 ID: <code>{sub_cat_id}</code>
🎲 Категория: <code>{cat_name}</code> [<code>{cat_id}</code>]
❗ Выберите, что хотите изменить:</b>
        """
        enter_new_name_for_subcategory = "<b>❗ Введите новое названия для подкатегории <code>{name}</code></b>"
        subcategory_is_edited_alert = "<b>❗ Администратор {username} изменил название подкатегории с <code>{old_name}</code> на <code>{new_name}</code>!</b>"
        confirm_subcategory_delete = "<b>❓ Вы уверены, что хотите удалить подкатегорию <code>{name}</code>?</b>"
        subcategory_is_deleted_alert = "<b>❗ Администратор {username} удалил подкатегорию с названием <code>{name}</code>!</b>"
        del_all_subcategories_text = "<b>❓ Вы уверены, что хотите удалить <u>ВСЕ</u> подкатегории?</b>"
        all_subcategories_are_deleted_alert = "<b>❗ Администратор {username} удалил <u>ВСЕ</u> подкатегории!</b>"
        subcategory_has_been_moved_deleted_alert = "<b>❗ Администратор {username} переместил подкатегорию <code>{sub_name}</code> из категории <code>{old_cat_name}</code> в категорию <code>{new_cat_name}</code>!</b>"
        enter_position_name = "<b>❗ Введите название для позиции:</b>"
        enter_position_price = "<b>❗ Введите цену для позиции:</b>"
        enter_position_item_type = "<b>❗ Выберите тип товара позиции \n\n<u>⚠️Примечание:</u> После этого шага изменить тип товара позиции невозможно!</b>"
        enter_position_description = "<b>❗ Введите описание для позиции \nЧтобы не ставить, отправьте <code>-</code></b>"
        enter_position_photo = "<b>❗ Отправьте фото для позиции \nЧтобы не ставить, отправьте <code>-</code></b>"
        enter_position_type = "<b>❗ Отправьте <code>+</code> если хотите чтоб товар был бесконечным \nЕсли не хотите введите <code>-</code></b>"
        position_type = {
            True: "Бесконечный товар",
            False: "Лимитированный товар",
            "file": "Файл",
            "text": "Текст",
            "photo": "Фото"
        }
        position_is_created_alert = """<b>❗ Администратор {username} создал позицию: 
💎 Категория: <code>{cat_name}</code> [<code>{cat_id}</code>]
🎲 Подкатегория: {subcategory}
📝 Название: <code>{name}</code>
💰 Цена: <code>{price}{curr}</code>
🪙 Тип позиции: <code>{position_type}</code>
🔰 Тип товара позиции: <code>{item_type}</code>
🧾 Описание: <code>{description}</code></b>
        """
        select_position = "<b>❗ Выберите позицию:</b>"
        position_text = """
<b>🌐 Позиция: <code>{pos_name}</code>
💎 Категория: <code>{cat_name}</code> [<code>{cat_id}</code>]
🎲 Подкатегория: {subcategory}
💰 Цена: <code>{price}{curr}</code>
🪙 Тип позиции: <code>{position_type}</code>
🔰 Тип товара позиции: <code>{item_type}</code>
🧾 Описание: <code>{description}</code>
🛒 Кол-во товаров: <code>{items_count} шт.</code>
❗ Выберите, что хотите изменить:</b>
        """
        enter_new_position_name = "<b>❗ Введите новое название для позиции:</b>"
        enter_new_position_price = "<b>❗ Введите новую цену для позиции:</b>"
        enter_new_position_description = "<b>❗ Введите новое описание для позиции \nЧтобы убрать, отправьте <code>-</code></b>"
        enter_new_position_photo = "<b>❗ Отправьте новое фото для позиции \nЧтобы убрать, отправьте <code>-</code></b>"
        confirm_position_delete = "<b>❓ Вы уверены, что хотите удалить позицию <code>{name}</code>?</b>"
        position_is_deleted_alert = "<b>❗ Администратор {username} удалил позицию с названием <code>{name}</code>!</b>"
        confirm_position_items_delete = "<b>❓ Вы точно хотите очистить <u>ВСЕ</u> товары позиции {name}?</b>"
        position_items_is_deleted_alert = "<b>❗ Администратор {username} удалил <u>ВСЕ</u> товары позиции <code>{name}</code>!</b>"
        del_all_positions_text = "<b>❓ Вы уверены, что хотите удалить <u>ВСЕ</u> позиции?</b>"
        all_positions_are_deleted_alert = "<b>❗ Администратор {username} удалил <u>ВСЕ</u> позиции!</b>"
        del_all_items_text = "<b>❓ Вы уверены, что хотите удалить <u>ВСЕ</u> товары?</b>"
        all_items_are_deleted_alert = "<b>❗ Администратор {username} удалил <u>ВСЕ</u> товары!</b>"
        enter_name_for_create_ad_button = "<b>❗ Введите название для рекламной кнопки:</b>"
        enter_content_for_ad_button = "<b>❗ Введите контент (сообщение) кнопки:</b>"
        enter_photo_for_ad_button = "<b>❗ Отправьте фото кнопки, чтобы пропустить введите <code>-</code></b>"
        enter_links_buttons_for_ad_button = """<b>❗ Отправьте кнопки-ссылки для этой кнопки в формате:
    
<code>Ссылка #1|https://examle1.com
Ссылка #2|https://example2.com</code>

❗ Чтобы пропустить введите <code>-</code></b>"""
        ad_button_is_created_alert = "<b>❗ Администратор {username} создал рекламную кнопку <code>{name}</code>!</b>"
        ad_button_is_deleted_alert = "<b>❗ Администратор {username} удалил рекламную кнопку <code>{name}</code>!</b>"
        enter_name_for_delete_ad_button = "<b>❗ Введите название рекламной кнопки для удаления:</b>"
        enter_name_for_create_mail_button = "<b>❗ Введите название для кнопки в рассылке:</b>"
        select_button = "<b>❗ Выберите кнопку:</b>"
        no_mail_buttons_available = "❗ Нет доступных кнопок! Создайте хотя бы одну!"
        select_mail_button_type = "<b>❗ Выберите тип кнопки:</b>"
        enter_link_for_mail_button = "<b>❗ Введите ссылку для кнопки в рассылке:</b>"
        select_contest = "<b>❗ Выберите розыгрыш:</b>"
        enter_data_items = {
            "text": """<b>⚙️ Введите данные товаров:
❗ Чтобы отделить товары, оставить между ними пустую строку. Пример:
❗ Вы можете скинуть txt файл, где товары так же отделены друг от друга.

<code>Товар #1...</code>

<code>Товар #2...</code>

<code>Товар #3...</code></b>""",
            "text_infinity": "<b>⚙️ Введите данные товара</b>",
            "photo": """<b>⚙️ Отправьте фото товара (можно с подписью)

❗ Загружайте по одному</b>""",
            "file": """<b>⚙️ Отправьте файл товара (можно с подписью)

❗ Загружайте по одному</b>"""
        }
        products_add_wait = "<b>⌛ Ждите, товары добавляются...</b>"
        no_need_item_type_sent = "<b>❗ Отправьте нужный тип товара!</b>"
        products_successful_added = "<b>✅ Товары в кол-ве <code>{count}шт</code> были успешно добавлены</b>"
        stop_upload_items_text = """<b>✅ Загрузка товаров была успешно завершена 
⚙️ Загружено товаров: <code>{count}шт</code></b>"""
        upload_items_error = "<b>❗ Что-то пошло не так при загрузке товаров! Попробуйте еще раз!</b>"
        list_of_items = "<b>🧾 Список товаров позиции <code>{name}</code></b>"
        get_list_of_items_error = "<b>❗ Что-то пошло не так при попытке получить список товаров! Попробуйте еще раз!</b>"
        position = "Позиция"
        item = "Товар"
        enter_item_id_for_delete = "<b>❗ Введите ID товара для удаления:</b>"
        value_is_no_link = "<b>❗ Значение должно быть ссылкой! Попробуйте ещё раз:</b>"
        mail_button_text = """<b>✨ Кнопка: <code>{name}</code>
🌐 Значение: {data}
❗ Выберите, что хотите изменить:</b>"""
        enter_new_mail_button_name = "<b>❗ Введите новое названия для кнопки:</b>"
        confirm_mail_button_delete = "<b>❓ Вы уверены, что хотите удалить кнопку в рассылке <code>{name}</code>?</b>"
        enter_message_for_mail = "<b>❗ Введите или перешлите сообщение для рассылки:</b>"
        confirm_message_for_mail = "<b>❓ Уверены, что хотите запустить рассылку с таким текстом?</b>"
        mail_started = "<b>✅ Рассылка запущена!</b>"
        mail_started_alert = "<b>❗ Администратор {username} запустил рассылку!</b>"
        success_mail_text = """<b>✅ Рассылка успешна завершена:
    
💎 Всего пользователей: <code>{all_users_count} чел.</code>
✅ Успешно отправлено: <code>{success_users_count} чел.</code>
❌ Бот заблокирован: <code>{failed_users_count} чел.</code></b>"""
        mail_error = "<b>❌ Во время рассылки произошла непредвиденная ошибка!</b>"
        select_what_you_want_to_find = "<b>⚙️ Выберите что хотите найти:</b>"
        enter_user_profile = "<b>❗ Введите ID, имя или @username пользователя</b>"
        enter_receipt = "<b>❗ Введите чек</b>"
        no_user_find = "<b>❗ Такого пользователя нет! Перепроверьте данные!</b>"
        user_profile_found = """
<b>👤 Профиль:

💎 Юзер: {username}
🆔 ID: <code>{user_id}</code>

💰 Баланс: <code>{balance}{curr}</code>

💵 Всего пополнено: <code>{total_refill}{curr}</code>
🧾 Кол-во пополнений: <code>{count_refills} шт.</code>

🛒 Кол-во покупок: <code>{count_purchases} шт.</code>
💲 Покупок на сумму: <code>{total_purchases}{curr}</code>

📌 Дата регистрации: <code>{reg_date}</code>
🌐 Язык: <code>{language}</code>

👥 Рефералов: <code>{ref_count} чел</code>
🔰 Реферальный уровень: <code>{ref_lvl}</code>
🚚 Кем приглашен: <code>{ref_name}</code>
💸 Заработал с рефералов: <code>{ref_earn}{curr}</code></b>
    """
        enter_sum_for_add_to_balance = "<b>💸 Введите сумму для добавления на баланс:</b>"
        enter_sum_for_minus_from_balance = "<b>💸 Введите сумму для вычитания с баланса:</b>"
        enter_sum_for_edit_balance = "<b>💸 Введите новый баланс пользователя:</b>"
        enter_sms_for_user = "<b>❗ Введите сообщения для пользователя:</b>"
        new_balance_alert = "<b>❗ Администратор {username} изменил баланс пользователю {user}!</b>"
        receipt_refill = """
<b>⭐ Чек <code>{receipt}</code>:

⚙️ Тип: <code>Пополнение</code>
💎 Юзер: {username}
📌 Способ: <code>{way}</code>
💰 Сумма: <code>{sum}{curr}</code>
🎲 Дата: <code>{date}</code>
🔗 Ссылка на оплату: {url}</b>
        """
        receipt_purchase = """
<b>⭐ Чек <code>{receipt}</code>:

⚙️ Тип: <code>Покупка</code>
💎 Юзер: {username}
📌 Товар: <code>{pos_name}</code>
💰 Сумма: <code>{sum}{curr}</code>
🛒 Количество: <code>{count}шт</code>
🎲 Дата: <code>{date}</code>
🔗 Содержимое:</b>
        """
        new_purchase_alert = """
💰 Новая покупка!
👤 Пользователь: <b>{user_name}</b> [<code>{user_id}</code>]
💵 Сумма: <code>{amount}{curr}</code>
🧾 Чек: <code>{receipt}</code>
⚙️ Товар: <code>{pos_name} x{count}</code>"""
        no_receipt = "❗ Чек не найден, попробуйте еще раз:"
        select_payment = "<b>💰 Выберите платежную систему:</b>"
        payments_on_off = {
            True: "✅ Включен",
            False: "❌ Выключен",
        }
        payment_info = """
<b>{method}</b>

Статус: <code>{status}</code>"""
        balance_info = """
Платежная система:
<b>{method}</b>

Баланс:
{balance}"""
        get_balance_error = "⚠️ Ошибка при получении баланса! Возможно вы не вставили данные для платежной системы!"
        payment_information_text = """
<b>{method}

💰 Пополнения:

За день: <code>{refills_count_for_day} шт.</code> (<code>{refills_for_day}{curr}</code>)
За неделю: <code>{refills_count_for_week} шт.</code> (<code>{refills_for_week}{curr}</code>)
За месяц: <code>{refills_count_for_month} шт.</code> (<code>{refills_for_month}{curr}</code>)
За все время: <code>{refills_count_for_all_time} шт.</code> (<code>{refills_for_all_time}{curr}</code>)

⚙ Информация: 

{configs}
⭐ Выберите, что хотите изменить:</b>
        """
        enter_new_value_for = "<b>❗ Введите новое значение для {field}:</b>"
        stats_message = """
<b>📊 Статистика:</b>


<b>👤 Юзеры:</b>

👤 За День: <code>{users_day}</code>
👤 За Неделю: <code>{users_week}</code>
👤 За Месяц: <code>{users_month}</code>
👤 За Всё время: <code>{users_all}</code>

👤 Сумма балансов всех юзеров: <code>{users_money}{cur}</code>

<b>💸 Продажи:</b>

💸 За День: <code>{profit_count_day}шт</code> (<code>{profit_amount_day}{cur}</code>)
💸 За Неделю: <code>{profit_count_week}шт</code> (<code>{profit_amount_week}{cur}</code>)
💸 За Месяц: <code>{profit_count_month}шт</code> (<code>{profit_amount_month}{cur}</code>)
💸 За Всё время: <code>{profit_count_all}шт</code> (<code>{profit_amount_all}{cur}</code>)

<b>💰 Пополнения:</b>

💰 За День: <code>{refill_count_day}шт</code> (<code>{refill_amount_day}{cur}</code>)
💰 За Неделю: <code>{refill_count_week}шт</code> (<code>{refill_amount_week}{cur}</code>)
💰 За Месяц: <code>{refill_count_month}шт</code> (<code>{refill_amount_month}{cur}</code>)
💰 За Всё время: <code>{refill_count_all}шт</code> (<code>{refill_amount_all}{cur}</code>)

<b>⚙️ Админы: </b>

⚙️ Всего админов: <code>{admins} чел</code>
⚙️ Админы: \n"""
        users_balances_txt_text = """Сумма: {rub}₽ | {usd}$ | {eur}€

Все юзеры и их балансы больше 0:

{users_balances}
        """
        all_users_and_their_balances="<b>⚙️ Все юзеры и их балансы</b>"
        list_of_all_users_ids = "<b>⚙️ Список ID всех пользователей</b>"
        sum_is_zero_and_no_users_with_balance = "❗ Сумма балансов равна 0, нет пользователей с балансом больше 0!"
        contest_is_start_successful = "🎉 Розыгрыш успешно запущен!"
        edit_contest_settings = """
<b>Изменение <code>{action}</code>
Текущее значение: 
{value}

Введите новое значение:</b>
    """
        contests_settings_values = {
            "winners_num": "Кол-во победителей",
            "prize": "Приз",
            "members_num": "Кол-во участников",
            "end_time": "Время розыгрыша",
            "purchases_num": "Кол-во покупок",
            "refills_num": "Кол-во пополнений",
            "channels_ids": "ID каналов для подписки"
        }
        enter_channels_ids = "<b>❗ Введите ID каналов для подписки через запятую. \nПример: -12345678910, -12423562345 \n\nВведите <code>-</code> Если не хотите ставить. \n\nТекущее значение: {value}</b>"
        user_is_entered_contest_alert = "<b>❗ Юзер {user} [<code>{user_id}</code>] участвует в розыгрыше на <code>{prize}{cur}</code></b>"
        contest_is_finished_and_members_are_zero_alert = "❗ В розыгрыше на {prize}{cur} никто не выиграл, т.к. участников 0!"
        contest_is_finished_alert = "❗ В розыгрыше на {prize}{cur} выиграли:\n"
        prize_given = "\n\n❗ Приз был выдан! ❗"
        
        # Новые тексты для системы отзывов
        review_system_title = "⭐ <b>Система отзывов</b>"
        purchase_completed = """
✅ <b>Покупка завершена!</b>

📦 Товар: <b>{product_name}</b>
💰 Сумма: <b>{price} {currency}</b>
🧾 Чек: <code>{receipt}</code>

Вы можете оставить отзыв о товаре для улучшения качества обслуживания."""
        
        review_prompt = """
⭐ <b>Оставьте отзыв о товаре</b>

📦 <b>{product_name}</b>

Ваш отзыв поможет другим покупателям и улучшит качество обслуживания.

Сначала выберите рейтинг:"""
        
        review_text_prompt = """
⭐ <b>Рейтинг: {rating} из 5</b>

Теперь напишите текст отзыва (необязательно):

Минимальная длина: {min_length} символов
Максимальная длина: {max_length} символов

Чтобы пропустить, отправьте <code>-</code>"""
        
        review_submitted = """
✅ <b>Отзыв успешно отправлен!</b>

⭐ Рейтинг: <b>{rating} из 5</b>

Спасибо за ваше мнение!"""
        
        review_already_exists = "❌ Вы уже оставляли отзыв на этот товар!"
        review_no_purchase = "❌ Вы можете оставлять отзывы только на купленные товары!"
        review_text_too_short = "❌ Отзыв слишком короткий! Минимальная длина: {min_length} символов"
        review_text_too_long = "❌ Отзыв слишком длинный! Максимальная длина: {max_length} символов"
        
        reviews_for_product = """
⭐ <b>Отзывы о товаре: {product_name}</b>

📊 Средний рейтинг: <b>{avg_rating}/5</b> ({total_reviews} отзывов)

{reviews_list}"""
        
        no_reviews = "📭 Пока нет отзывов об этом товаре. Будьте первым!"
        
        my_reviews_title = "📝 <b>Мои отзывы</b>"
        my_reviews_empty = "📭 Вы пока не оставляли отзывов"
        
        review_item = """
⭐ <b>{rating}/5</b> | <i>{date}</i>
📦 <b>{product_name}</b>
💬 {review_text}
👍 Полезно: {helpful_count}

---"""
        
        # Новые тексты для Steam Points
        steam_points_title = "🎮 <b>Steam Points</b>"
        steam_points_description = """
🎮 <b>Покупка очков Steam</b>

Steam Points - это внутриигровая валюта Steam, которую можно использовать для:
• 🛒 Покупки предметов в магазине Steam
• 🎨 Кастомизации профиля
• 🏆 Покупки наград для игр
• 💎 Украшения профиля

<b>Преимущества:</b>
⚡ Мгновенное зачисление
💰 Выгодные цены
🔒 Безопасная сделка
🎯 Автоматическая доставка

Выберите количество очков:"""
        
        steam_points_amount = """
🎮 <b>Количество: {points} очков</b>

💰 <b>Цена: {price} {currency}</b>
📈 <b>Курс: {rate} {currency} за очко</b>

Для продолжения введите ссылку на ваш Steam профиль:

<b>Принимаются ссылки вида:</b>
🔗 <code>https://steamcommunity.com/id/ваш_ник</code>
🔗 <code>https://steamcommunity.com/profiles/76561198000000000</code>"""
        
        steam_link_invalid = """
❌ <b>Неверная ссылка Steam!</b>

Убедитесь, что ссылка имеет один из форматов:
🔗 <code>https://steamcommunity.com/id/ваш_ник</code>
🔗 <code>https://steamcommunity.com/profiles/76561198000000000</code>

Попробуйте еще раз:"""
        
        steam_order_confirm = """
✅ <b>Подтверждение заказа</b>

🎮 <b>Steam профиль:</b> {steam_link}
💎 <b>Количество очков:</b> {points}
💰 <b>К оплате:</b> {price} {currency}

Подтвердите заказ:"""
        
        steam_processing = """
⏳ <b>Обработка заказа...</b>

🎮 Подключаемся к Steam API
💎 Покупаем {points} очков
⚡ Зачисляем на ваш аккаунт

Это может занять до 30 секунд..."""
        
        steam_success = """
✅ <b>Очки Steam успешно зачислены!</b>

🎮 <b>Steam профиль:</b> {steam_link}
💎 <b>Зачислено очков:</b> {points}
💰 <b>Стоимость:</b> {total_cost} {currency}
📊 <b>Очки до покупки:</b> {before_points}
📈 <b>Очки после покупки:</b> {after_points}

🧾 <b>Чек:</b> <code>{receipt}</code>
📅 <b>Дата:</b> {date}

Спасибо за покупку! 🎉"""
        
        steam_error = """
❌ <b>Ошибка при покупке Steam Points</b>

К сожалению, произошла ошибка при обработке заказа:
<code>{error}</code>

💰 Ваши средства не были списаны.
💬 Обратитесь в поддержку, если проблема повторяется."""
        
        steam_insufficient_balance = """
💳 <b>Недостаточно средств на балансе API</b>

К сожалению, на балансе сервиса недостаточно средств для покупки очков.
📞 Администратор уведомлен и пополнит баланс в ближайшее время.
💰 Ваши средства не были списаны."""
        
        steam_custom_amount = """
💎 <b>Введите количество очков</b>

Минимум: {min_points} очков
Максимум: {max_points} очков

Очки должны быть кратны 100."""
        
        steam_amount_invalid = """
❌ <b>Неверное количество очков!</b>

• Минимум: {min_points} очков
• Максимум: {max_points} очков  
• Должно быть кратно 100

Попробуйте еще раз:"""
        
        steam_insufficient_funds = """
💰 <b>Недостаточно средств!</b>

На вашем балансе: <b>{balance} {currency}</b>
Необходимо: <b>{required} {currency}</b>

Пополните баланс для продолжения."""
        
        # ===== Steam API уведомления админам =====
        steam_api_error = """
🎮❌ <b>Ошибка Steam API</b>

Произошла ошибка при работе со Steam Points API:
<code>{error}</code>

Проверьте настройки API и попробуйте еще раз."""
        
        steam_low_balance = """
🎮⚠️ <b>Низкий баланс Steam API</b>

Система Steam Points автоматически отключена!

💎 Текущий баланс: <b>{balance:.2f} очков</b>
📊 Порог отключения: <b>{threshold:.2f} очков</b>

💰 Пополните баланс API для продолжения работы."""
        
        steam_balance_restored = """
🎮✅ <b>Баланс Steam API восстановлен</b>

Система Steam Points автоматически включена!

💎 Текущий баланс: <b>{balance:.2f} очков</b>
📊 Порог включения: <b>{threshold:.2f} очков</b>

Система готова к работе."""
        
        # Discount system texts
        