class Language:
    def __init__(self):
        self.language = "ua"
    
    class Buttons:
        buy = "💸 Придбати"
        profile = "👤 Профіль"
        support = "💎 Підтримка"
        faq = "❓ FAQ"
        topup_balance = "💰 Пополнить баланс"
        back = "◀ Назад"
        contests = "🎁 Розіграші"
        faq_chat_inl = "💎 Чат"
        faq_news_inl = "📩 Новинний канал"
        steam_points = "🎮 Steam Points"
        reviews = "⭐ Відгуки"
        
        # Legal documents
        legal_documents = "📋 Документи"
        terms_of_service = "📜 Умови користування"
        privacy_policy = "🔒 Політика конфіденційності"
        user_agreement = "📄 Користувацька угода"
        
        #  Inline
        send_payment_to_check = "✅ Надіслати платіж на перевірку"
        close = "❌ Закрити"
        activate_promo = "📢 Активувати промо"
        ref_system = "👥 Реферальна система"
        purchases_history = "🛒 Історія покупок"
        support_text = "🔗 Написати на підтримку"
        refill_link_inl = "💵 Перейти до оплати"
        refill_check_inl = "💎 Перевірити оплату"
        cancel = "❌ Скасувати"
        admin_panel = "⚙ Панель адміністратора"
        choose_action = "Виберіть дію"
        position_button_name = "{name} | {price}{curr} | {items}"
        nolimit = "Безліміт"
        pcs = "шт."
        contest_enter = '🎉 Брати участь у розіграші'
        you_not_completed_all_conditions = "❗ Ви не виконали всі умови! Виконано {count} з {count_conditions}"
        change_language = "🌐 Змінити мову"
        check_sub = "✅ Перевірити"
        
        # Privacy policy buttons
        privacy_accept_btn = "✅ Прийняти"
        privacy_decline_btn = "❌ Відхилити"
        

    class Texts:

        #######################################
        #  Min/Max Amount of refill (IN RUB)  #
        #                                     #
        min_amount = 5                        #
        max_amount = 100000                   #
        #                                     #
        #                                     #
        #######################################

        is_buy_text = "❌ Покупки тимчасово недоступні!"
        is_ban_text = f"❌ Ви були заблоковані в роботі!"
        is_work_text = f"❌ Робот знаходиться на тих. роботах!"
        is_refill_text = f"❌ Поповнення тимчасово недоступні!"
        is_ref_text = f"❗ Реферальна система тимчасово недоступна!"
        is_contests_text = f"❌ Розіграші тимчасово недоступні!"
        channels_error = """
<b>❌ Помилка!\n\nВи підписалися не на всі канали:

{urls_txt}</b>
    """

        nobody = "<code>Ніхто</code>"
        ref_s = ('реферал', 'рефералу', 'рефералів') # не трогать скобки
        day_s = ('день', 'дня', 'днів') # не трогать скобки
        member_s = ("учасник", "учасника", "учасників") # не трогать скобки
        winner_s = ("переможець", "переможця", "переможців") # не трогать скобки
        refill_s = ("поповнення", "поповнення", "поповнення") # не трогать скобки
        purchase_s = ("купівля", "купівлі", "купівель") # не трогать скобки
        channel_s = ('канал', 'каналу', 'каналів') # не трогать скобки
        person_s = ("людина", "людини", "людина")

        main_menu = """
<b>👩‍💻 {username}, Дякую що користуєтесь нашим Магазином

Головне меню:</b>"""
        
        privacy_policy_text = """
<b>🔒 Політика конфіденційності</b>

Ласкаво просимо до нашого магазину!

Для використання бота необхідно погодитися з нашою політикою конфіденційності та умовами користування.

<b>Ми збираємо наступні дані:</b>
• Ваш Telegram ID
• Ім'я користувача та ім'я
• Історію покупок та поповнень
• Реферальну інформацію

<b>Ми НЕ збираємо:</b>
• Дані банківських карт
• Паролі або приватні ключі
• Особисту переписку

<b>Ваші дані використовуються для:</b>
• Обробки замовлень
• Реферальної системи
• Технічної підтримки
• Покращення сервісу

Натискаючи кнопку "Погоджуюся", ви підтверджуєте, що ознайомилися і згодні з політикою конфіденційності."""
        
        privacy_accepted = "✅ Дякую! Тепер ви можете користуватися ботом."
        privacy_declined = "❌ Для використання бота необхідно погодитися з політикою конфіденційності."
        
        bot_will_not_respond = "❗ Бот не буде відповідати до припинення спаму."
        please_dont_spam = "❗ Будь ласка, не спамте."
        
        profile_text = """
<b>👤 Ваш Профіль:

💎 Користувач: {username}
🆔 ID: <code>{user_id}</code>

💰 Баланс: <code>{balance}{curr}</code>
💵 Усього поповнено: <code>{total_refill}{curr}</code>

📌 Дата реєстрації: <code>{reg_date}</code></b>"""
        support_is_not_provided = "<b>💎 На даний момент немає актуальної підтримки!</b>"
        support_text = "<b>💎 Щоб написати підтримку, натисніть кнопку знизу:</b>"
        choose_language = "<b>❗ Виберіть мову / Choose language:</b>"
        refill_check_no = "❌ Оплати не знайдено"
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
        choose_refill_method = "<b>💰 Виберіть спосіб поповнення:</b>"
        payment_comment_api = "Поповнення облікового запису {user_name} на суму {pay_amount}{curr} у роботі @{bot_name}"
        refill_was_rejected = "<b>❌ Ваше поповнення на {amount}{curr} було відхилено!</b>"
        send_receipt_photo = "<b>🧾 Надішліть фото чека перекладу:</b>"
        confirm_send_receipt_photo = "<b>❓ Ви впевнені, що хочете надіслати цей чек на перевірку?</b>"
        create_refill_text = """
<b>⭐ Поповнення через: <code>{paymentMethod}</code>
💰 Сума: <code>{pay_amount}{curr}</code>
🆔 ID платежу: <code>{pay_id}</code>
⌛ Ви повинні сплатити рахунок до <code>{under_date}</code>
💎 Щоб сплатити, натисніть кнопку внизу:</b>"""
        cancel_create_refill_text = """
<b>❗ У вас вже є активне поповнення:

⭐ Поповнення через: <code>{paymentMethod}</code>
💰 Сума: <code>{pay_amount}{curr}</code>
🆔 ID платежу: <code>{pay_id}</code>
⌛ Ви повинні сплатити рахунок до <code>{under_date}</code>
💎 Щоб сплатити, натисніть кнопку внизу:</b>"""
        create_refill_text_custom_pay_method = """
<b>⭐ Поповнення через: <code>{paymentMethod}</code>
💰 Сума: <code>{pay_amount}{curr}</code>
🆔 ID платежу: <code>{pay_id}</code>
⌛ Ви повинні сплатити рахунок до <code>{under_date}</code></b>

{custom_pay_method_text}"""
        cancel_create_refill_text_custom_pay_method = """
<b>❗ У вас вже є активне поповнення:

⭐ Поповнення через: <code>{paymentMethod}</code>
💰 Сума: <code>{pay_amount}{curr}</code>
🆔 ID платежу: <code>{pay_id}</code>
⌛ Ви повинні сплатити рахунок до <code>{under_date}</code></b>

{custom_pay_method_text}"""
        enter_amount_of_refill = "<b>❗ Введіть суму поповнення:</b>"
        choose_crypto = "<b>⚙️ Виберіть криптовалюту:</b>"
        error_refill = "❌ Помилка, поповнення вже відбулося!"
        success_refill_text = """
<b>⭐ Ви успішно поповнили баланс на суму <code>{amount}{curr}</code>
💎 Спосіб: <code>{way}</code>
🧾 Чек: <code>{receipt}</code></b>
"""
        yes_refill_ref = "<b>💎 Ваш реферал {name} поповнив баланс на <code>{amount}{cur}</code> і з цього вам зараховано <code>{ref_amount}{cur}</code></b>"
        yes_cancel_refill = "<b>❌ Поповнення скасовано</b>"
        no_int_amount = "<b>❗ Сума поповнення має бути числом!</b>"
        min_max_amount = "<b>❗ Сума поповнення повинна бути більшою або дорівнює <code>{min_amount}{curr}</code> але меншою або дорівнює <code>{max_amount}{curr}</code></b>"
        new_ref_lvl = "<b>💚 У вас є новий реферальний рівень, {new_lvl}! До {next_lvl} рівня залишилося {remain_refs} {convert_ref}</b>"
        max_ref_lvl = f"<b>💚 У вас є новий реферальний рівень, 3! Максимальний рівень!</b>"
        cur_max_lvl = f"💚 У вас є максимальний рівень!</b>"
        next_lvl_remain = "💚 До наступного рівня залишилося запросити <code>{remain_refs} {person_s}</code>.</b>"
        ref_text = """<b>💎 Реферальна система

🔗 Посилання:
{ref_link}

📔 Наша реферальная система дозволить вам заробити велику суму без вкладень. Вам необхідно лише давати своє посилання друзям і ви будете отримувати довічно <code> {ref_percent}%</code > з їх поповнень в боті.


⚙️ Вас запросив: {reffer}
💵 Всього зароблено <code>{ref_earn}{curr}</code> з рефералів
📌 Всього у вас <code>{ref_count}</code> {convert_ref}
🎲 Реферальний рівень: <code>{ref_lvl}</code>
{mss}"""
        yes_reffer = f"<b>❗ У Вас вже є рефер!</b>"
        invite_yourself = "<b>❗ Ви не можете запросити себе</b>"
        new_refferal = "<b>💎 У вас новий реферал! @{user_name} \n" \
                    "⚙️ Тепер у вас <code>{user_ref_count}</code> {convert_ref}!</b>"
        promo_act = "<b>📩 Для активації промо коду напишіть його назву</b>\n" \
                    "<b>⚙️ Приклад: promo2025</b>"
        no_uses_promocode = "<b>❌ Ви не встигли активувати промокод!</b>"
        no_promocode = "<b>❌ Промо коду <code > {promocode}< / code > не існує!</b>"
        yes_promocode = "<b>✅ Ви успішно активували промокод і отримали <code>{discount}{curr}</code>!</b>"
        yes_uses_promocode = "<b>❌ Ви вже активували цей промокод!</b>"
        no_cats = f"<b>❌ На жаль в даний момент немає категорій :(</b>"
        available_cats = f"<b>🛒 Доступні на даний момент категорії:</b>"
        current_cat = "<b>🚀 Поточна Категорія: <code>{name}</code>:</b>"
        no_products = f"❌ На жаль в даний момент немає товарів :("
        open_position_text = """
<b>💎 Категорія: <code>{cat_name}</code>

🛍️ Товар: <code>{pos_name}</code>
💰 Вартість: <code>{price}{cur}</code>
⚙️ Доступна : <code>{items}</code></b>

{desc}"""
        no_balance_for_buying = "❗ У вас недостатньо коштів для покупки. Поповніть баланс!"
        confirm_buy_products = """
<b>❓ Ви дійсно хочете купити товар(и)?</b>

- Товар: <code>{position_name}</code>
- Кількість: <code>{count}шт</code>
- Сума до покупки: <code>{price}{curr}</code>
"""
        enter_count_items_for_buy = """
<b>❗ Введіть кількість товарів для покупки</b>
⚠️ Від <code>1</code> до <code>{items}</code>

- Товар: <code>{pos_name}</code> - <code>{price}{curr}</code>
- Ваш баланс: <code>{balance}{curr}</code>
"""
        incorrect_data = "<b>❌ Дані були введені невірно</b>"
        data_was_edit = "<b>❗ Товар який ви хотіли купити, закінчився</b>"
        incorrect_count_items = "<b>❌ Невірна кількість товарів</b>"
        no_balance_on_account = "<b>❌ Недостатньо коштів на рахунку</b>"
        please_await_products = "<b>🔄 Чекайте, товари готуються</b>"
        successful_buying = """
<b>✅ Ви успішно купили товар (и)</b>

- Чек: <code>{receipt}</code>
- Товар: <code>{position_name} | {purchase_count}шт | {purchase_price}{curr}</code>
- Дата покупки: <code>{date}</code>
"""
        receipt_purchase = """
<b>⭐ Чек <code>{receipt}</code>:
📌 Товар: <code>{pos_name}</code>
💰 Сума: <code>{sum}{curr}</code>
🛒 Кількість: <code>{count}шт</code>
🎲 Дата: <code>{date}</code>
🔗 Вміст:</b>
        """
        last_10_purchases = "<b>🚀 Останні 10 покупок</b>"
        no_have_purchases = "❗ У вас немає ще не однієї покупки!"
        your_items = "<b>🛒 Ваші товари</b>"
        no_contests = "❌ Зараз не проходить жодного розіграшу!"
        choose_contest = "<b>🎉 Виберіть один з розіграшів:</b>"
        contest_text = """
<b>🎉 Розиграш #{contest_id}

💰 Сума: <code>{prize}{cur}</code>

🕒 Кінець через <code>{end_time}</code>

🎉 {winners_num} {winners}
👥 {members_num} {members}</b>"""
        conditions = "\n\n<b>❗ Умова: </b>\n\n"
        conditions_refills = '<b>💳 {num} {refills} - {status}</b>\n'
        conditions_purchases = '<b>🛒 {num} {purchases} - {status}</b>\n'
        conditions_channels = '<b>✨ Підписатися на {num} {channels_text}: \n\n{channels}</b>\n'
        u_win_the_contest = "<b>🎉 Вітаю, ви виграли в розіграші!\n💰 Приз у розмірі {prize}{cur} був виданий!</b>"
        u_didnt_have_time_to_enter_contest = "Ви не встигли взяти участь! 💥"
        success = "✅ Успішно"
        u_already_enter_contest = "❌ Ви вже берете участь!"
        contest_already_ended = "💥 Розіграш вже завершено!"


    class AdminTexts:
        ### Buttons:
        back = "◀ Назад"
        main_settings = "🖤 Загальні налаштування"
        extra_settings = "🎲 Доп. Налаштування"
        switchers = "❗ Вимикач"
        statistic = "📊 Статистика"
        find = "🔍 Шукати"
        products_manage = "💎 Управління товарами"
        mail = "📌 Розсилання"
        payments_systems = "💰 Платіжні системи"
        ad_buttons = "💫 Рекламні кнопки"
        mail_buttons = "🧩 Кнопки в розсилці"
        contests = "🎉 Розиграш"
        main_settings_values = {
            "faq": "FAQ",
            "support": "Тих. Підтримка",
            "ref_percent_1": "Реф. Відсоток 1 лвл",
            "ref_percent_2": "Реф. Відсоток 2 лвл",
            "ref_percent_3": "Реф. Відсоток 3 лвл",
            "currency": "Валюта бота",
            "default_lang": "Мова за замовчуванням",
            "chat": "Чат",
            "news": "Канал новин",
        }
        currencies = {
            "rub": "Рубель",
            "usd": "Долар",
            "eur": "Євро",
        }
        switchers_settings = {
            "tech_works": "Тих. Роботи",
            "buys": "Покупки",
            "refills": "Поповнення",
            "ref": "Реф. Система",
            "contests": "Розиграш",
            "multi_lang": "Багатомовність",
            "notify": "Увед. про нових користувачів",
            "sub": "Перевірка підписки",
            "keyboard": "Головне меню",
            
        }
        create_promocode = "💎 Створити промокод"
        delete_promocode = "🎲 Видалити промокод"
        edit_number_of_refs_for_ref_lvl_2 = "2️⃣ Змінити кількість рефералів для 2 лвла"
        edit_number_of_refs_for_ref_lvl_3 = "3️⃣ Змінити кількість рефералів для 3 лвла"
        add_category = "➕ | Категорію"
        edit_category = "⚙️ | Категорію"
        del_all_categories = "🗑️ | ВСІ категорії"
        add_subcategory = "➕ | Підкатегорію"
        edit_subcategory = "⚙️ | Підкатегорію"
        del_all_subcategories = "🗑️ | ВСІ Підкатегорії"
        add_position = "➕ | Позицію"
        edit_position = "⚙️ | Позицію"
        del_all_positions = "🗑️ | ВСІ Позиції"
        add_items = "➕ | Товары"
        del_item = "🗑️ | Товар"
        del_all_items = "🗑️ | ВСІ Товары"
        delete = "🗑️ Видалити"
        name = "📘 Назва"
        move = "🔁 Перемістити"
        select_this_category = "💎 Вибрати цю категорію"
        photo = "📸 Фото"
        text = "📝 Текст"
        file_ = "📁 Файл"
        price = "💰 Ціна"
        description = "📑 Опис"
        position_type_text = "🪙 Тип позиції"
        clear_items = "🗑️ Очистити товари"
        get_items = "🧾 Отримати перелік товарів"
        upload_items = "🔰 Завантажити товари"
        create = "➕ Створити"
        current_buttons = "📑 Поточні кнопки"
        open_category_button = "🌐 Кнопка відкриття категорії"
        open_subcategory_button = "🔰 Кнопка відкриття підкатегорії"
        open_position_button = "🛒 Кнопка відкриття позиції"
        open_contest_button = "🎉 Кнопка відкриття розіграшу"
        link_button = "🔗 Кнопка-посилання"
        mail_buttons_types = {
            "link": link_button,
            "category": open_category_button,
            "subcategory": open_subcategory_button,
            "position": open_position_button,
            "contest": open_contest_button
        }
        stop_upload_items = "❌ Закінчити завантаження товарів"
        profile = "👤 Профіль"
        receipt = "🧾 Чек"
        edit_balance = "💰 Редагувати баланс"
        unban = "⛔ Розблокувати"
        ban = "⛔ Заблокувати"
        send_message = "⭐ Надіслати повідомлення"
        add_balance = "➕ Видати баланс"
        minus_balance = "➖ Зняти баланс"
        edit_bal = "⚙️ Змінити баланс"
        get_users_and_their_balances = "Отримати користувачів та його баланс > 0"
        get_users_ids = "Отримати список ID користувачів"
        winners_count = "✨ Кількість переможців"
        prize = "💰 Приз"
        conditions = "🚀 Умови"
        members_count = "💥 Кількість учасників"
        contest_time = "⌚ Час розіграшу"
        end_contest_now = "❌ Закінчити розіграш зараз"
        start_contest = "⭐ Розпочати розіграш"
        purchases_count = "🛒 Кількість покупок"
        refills_count = "💳 Кількість поповнень"
        channels_ids_for_sub = "💎 ID Каналів для підписки |"
        edit_custom_pay_method_name = "⚙️ Змінити назву способу"
        edit_custom_pay_method_text = "📖 Змінити текст під час поповнення"
        edit_custom_pay_method_min_amount = "🚀 Змінити мінімальну суму для поповнення"
        edit_custom_pay_method_receipt = "Просити чек перед відправкою на перевірку | {status}"
        enable = "✅ Увімкнути"
        disable = "❌ Вимкнути"
        get_balance = "💰 Дізнатись баланс"
        show_info = "📌 Показати інформацію"
        
        ### Texts:
        new_refill_custom_pay_method_alert = """
<b>🧾 Користувач {username} [<code>{user_id}</code>] відправив платіж на перевірку:

Сума: <code>{amount}{curr}</code>

✅ - Схвалити платіж
❌ - Відхилити платіж</b>"""
        enter_new_name_for_custom_pay_method = "<b>⚙️ Введіть нову назву кастомного способу оплати. \nПоточне: {name}</b>"
        enter_new_min_for_custom_pay_method = "<b>⚙️ Введіть новий мінімум для кастомного способу оплати. Поточний: {min}{curr}</b>"
        enter_new_text_for_custom_pay_method = "<b>⚙️ Введіть новий текст кастомного способу оплати. \nПоточний: \n</b>{text}"
        payment_info_custom_pay_method = """
<b>{method}</b>

Статус: <code>{status}</code>
Мінімальна сума для поповнення: <code>{min}{curr}</code>
Перегляд поповнення:
{preview_refill}"""
        success = "<b>✅ Успішно!</b>"
        edit_number_of_refs_for_ref_lvl_alert = "<b>❗ Адміністратор {username} змінив кількість рефералів для рівня <code>{lvl}</code> на <code>{count} {convert}</code></b>"
        you_edit_number_of_refs_for_ref_lvl = "<b>✅ Ви змінили кількість рефералів для рівня <code>{lvl}</code> на <code>{count} {convert}</code></b>"
        this_promo_is_not_exits = "<b>❌ Такого промокоду немає! Спробуйте знову:</b>"
        this_promo_is_already_exists = "<b>❌ Промокод із такою назвою вже існує! Введіть іншу назву:</b>"
        promo_is_deleted_alert = "<b>❗ Адміністратор {username} видалив Промокод <code>{name}</code></b>"
        promo_is_deleted = "<b>✅ Промокод <code>{name}</code> успішно видалено!</b>"
        promo_is_created_alert = "<b>❗ Адміністратор {username} створив Промокод <code>{name}</code> з кількома використаннями <code>{uses}</code> та знижкою <code>{discount}{curr}</code></b>"
        promo_is_created = "<b>✅ Промокод <code>{name}</code> з кількома використаннями <code>{uses}</code> та знижкою <code>{discount}{curr}</code> був створений!</b>"
        value_is_no_number = "<b>❗ Значення має бути числом!:</b>"
        enter_discount_for_promo = "<b>❗ Введіть знижку (Гроші зарахуються після введення промокоду)</b>"
        now_enter_number_of_uses_for_promo = "<b>❗ Тепер введіть кількість використання промокоду:</b>"
        enter_new_number_of_refs_for_ref_lvl = "<b>❗ Введіть нову кількість рефералів для {lvl} рівня:</b>"
        enter_promo_name_for_delete = "<b>❗ Введіть назви промокоду для видалення:</b>"
        enter_promo_name_for_create = "<b>❗ Введіть назви нового промокоду:</b>"
        choose_action = "<b>❗ Виберіть дію:</b>"
        new_user_alert = "<b>💎 Зареєстровано нового користувача {name} [<code>{user_id}</code>]</b>"
        edit_main_setting = """
<b>Зміна <code>{action}</code>
Поточне значення:
{value}

Введіть нове значення:</b>
    """
        choose_new_currency = "<b>❗ Виберіть нову валюту бота: \n\nP.S. За зміни валюти ціни на товари конвертуються з поточної валюти на нову.</b>"
        choose_new_default_language = "<b>❗ Виберіть нову мову за замовчуванням:</b>"
        welcome_to_the_admin_panel = "<b>🎉 Ласкаво просимо до панелі адміністратора:</b>"
        main_settings_text = "<b>⚙️ Основні налаштування бота:</b>"
        choose_what_you_want_to_enable_disable = "<b>⚙️ Виберіть що хочете вимкнути / включити \n❌ - Викл. | ✅ - Вкл.</b>"
        refill_log = """
<b>💰 Відбулося поповнення балансу!
👤 Користувач: {user_mention} [<code>{user_id}</code>]
💵 Сума поповнення: <code>{pay_amount}{curr}</code>
🧾 Чек: <code>{pay_id}</code>
⚙️ Спосіб: <code>{way}</code>{external_id_info}</b>
    """
        products_manage_text = """
<b>⚙️ Виберіть, що хочете зробити:
<blockquote>➕ - Додати/Створити
⚙️ - Редактировать
🗑️ - Видалити</blockquote></b>
        """
        add_category_text = "<b>❗ Введіть назву для категорії:</b>"
        category_is_created_alert = "<b>❗ Адміністратор {username} створив категорію під назвою <code>{name}</code>!</b>"
        no_categories_available = "❌ Немає доступних категорій! Створіть хоча б одну!"
        select_category = "<b>❗ Виберіть категорію:</b>"
        category_text = """
<b>💎 Категорія: <code>{name}</code>
🆔 ID: <code>{cat_id}</code>
❗ Виберіть, що хочете змінити:</b>
        """
        enter_new_name_for_category = "<b>❗ Введіть нову назву для категорії <code>{name}</code></b>"
        category_is_edited_alert = "<b>❗ Адміністратор {username} змінив назву категорії з <code>{old_name}</code> на <code>{new_name}</code>!</b>"
        confirm_category_delete = "<b>❓ Ви впевнені, що бажаєте видалити категорію <code>{name}</code>?</b>"
        category_is_deleted_alert = "<b>❗ Адміністратор {username} видалив категорію під назвою <code>{name}</code>!</b>"
        del_all_categories_text = "<b>❓ Ви впевнені, що хочете видалити <u>ВСЕ</u> категорії?</b>"
        all_categories_are_deleted_alert = "<b>❗ Адміністратор {username} видалив <u>ВСЕ</u> категорії!</b>"
        enter_name_for_subcategory = "<b>❗ Введіть назви для підкатегорії:</b>"
        name_error = "<b>❌ Максимальна довжина назви <code>64</code> символу!</b>"
        description_error = "<b>❌ Максимальна довжина опису <code>2000</code> символу! Спробуйте ще раз: </b>"
        subcategory_is_created_alert = "<b>❗ Адміністратор {username} створив підкатегорію під назвою <code>{name}</code> у категорії <code>{cat_name}</code>!</b>"
        no_subcategories_available = "❌ Немає доступних підкатегорій! Створіть хоча б одну!"
        no_subcategories_available_in_this_category = "❌ Немає доступних підкатегорій у цій категорії! Створіть хоча б одну!"
        no_positions_available_in_this_category = "❌ Немає доступних позицій у цій категорії! Створіть хоча б одну!"
        no_positions_available = "❌ Немає доступних позицій! Створіть хоча б одну!"
        no_positions_available_in_this_subcategory = "❌ Немає доступних позицій у цій підкатегорії! Створіть хоча б одну!"
        select_subcategory = "<b>❗ Виберіть підкатегорію:</b>"
        subcategory_text = """
<b>💎 Підкатегорія: <code>{name}</code>
🆔 ID: <code>{sub_cat_id}</code>
🎲 Категорія: <code>{cat_name}</code> [<code>{cat_id}</code>]
❗ Виберіть, що хочете змінити:</b>
        """
        enter_new_name_for_subcategory = "<b>❗ Введіть нову назву для підкатегорії <code>{name}</code></b>"
        subcategory_is_edited_alert = "<b>❗ Адміністратор {username} змінив назву підкатегорії з <code>{old_name}</code> на <code>{new_name}</code>!</b>"
        confirm_subcategory_delete = "<b>❓ Ви впевнені, що бажаєте видалити підкатегорію <code>{name}</code>?</b>"
        subcategory_is_deleted_alert = "<b>❗ Адміністратор {username} видалив підкатегорію під назвою <code>{name}</code>!</b>"
        del_all_subcategories_text = "<b>❓ Ви впевнені, що хочете видалити <u>ВСЕ</u> підкатегорії?</b>"
        all_subcategories_are_deleted_alert = "<b>❗ Адміністратор {username} видалив <u>ВСЕ</u> підкатегорії!</b>"
        subcategory_has_been_moved_deleted_alert = "<b>❗ Адміністратор {username} перемістив підкатегорію <code>{sub_name}</code> з категорії <code>{old_cat_name}</code> до категорії <code>{new_cat_name}</code>!</b>"
        enter_position_name = "<b>❗ Введіть назву для позиції:</b>"
        enter_position_price = "<b>❗ Введіть ціну для позиції:</b>"
        enter_position_item_type = "<b>❗ Виберіть тип товару позиції \n\n<u>⚠️Примітка:</u> Після цього кроку змінити тип товару позиції неможливо!</b>"
        enter_position_description = "<b>❗ Введіть опис для позиції \nЩоб не ставити, надішліть <code>-</code></b>"
        enter_position_photo = "<b>❗Надішліть фото для позиції \nЩоб не ставити, відправте  <code>-</code></b>"
        enter_position_type = "<b>❗ Надішліть <code>+</code> якщо хочете щоб товар був нескінченним \nЯкщо не хочете, введіть <code>-</code></b>"
        position_type = {
            True: "Нескінченний товар",
            False: "Лімітований товар",
            "file": "Файл",
            "text": "Текст",
            "photo": "Фото"
        }
        position_is_created_alert = """<b>❗ Адміністратор {username} створив таку позицію:
💎 Категорія: <code>{cat_name}</code> [<code>{cat_id}</code>]
🎲 Підкатегорія: {subcategory}
📝 Назва: <code>{name}</code>
💰 Цена: <code>{price}{curr}</code>
🪙 Тип позиції: <code>{position_type}</code>
🔰 Тип товару позиції: <code>{item_type}</code>
🧾 Опис: <code>{description}</code></b>
        """
        select_position = "<b>❗ Виберіть позицію:</b>"
        position_text = """
<b>🌐 Позиція: <code>{pos_name}</code>
💎 Категорія: <code>{cat_name}</code> [<code>{cat_id}</code>]
🎲 Підкатегорія: {subcategory}
💰 Цена: <code>{price}{curr}</code>
🪙 Тип позиції: <code>{position_type}</code>
🔰 Тип товару позиції: <code>{item_type}</code>
🧾 Опис: <code>{description}</code>
🛒 Кількість товарів: <code>{items_count} шт.</code>
❗ Виберіть, що хочете змінити:</b>
        """
        enter_new_position_name = "<b>❗ Введіть нову назву для позиції:</b>"
        enter_new_position_price = "<b>❗ Введіть нову ціну для позиції:</b>"
        enter_new_position_description = "<b>❗ Введіть новий опис для позиції \nЩоб прибрати, відправте <code>-</code></b>"
        enter_new_position_photo = "<b>❗ Надішліть нове фото для позиції \nЩоб прибрати, відправте <code>-</code></b>"
        confirm_position_delete = "<b>❓ Ви впевнені, що бажаєте видалити позицію <code>{name}</code>?</b>"
        position_is_deleted_alert = "<b>❗ Адміністратор {username} видалив позицію під назвою <code>{name}</code>!</b>"
        confirm_position_items_delete = "<b>❓ Ви точно хочете очистити <u>ВСЕ</u> товари позиції {name}?</b>"
        position_items_is_deleted_alert = "<b>❗ Адміністратор {username} видалив <u>ВСЕ</u> товари позиції <code>{name}</code>!</b>"
        del_all_positions_text = "<b>❓ Ви впевнені, що хочете видалити <u>ВСЕ</u> позиції?</b>"
        all_positions_are_deleted_alert = "<b>❗ Адміністратор {username} видалив <u>ВСЕ</u> позиції!</b>"
        del_all_items_text = "<b>❓ Ви впевнені, що хочете видалити <u>ВСЕ</u> товари?</b>"
        all_items_are_deleted_alert = "<b>❗ Адміністратор {username} видалив <u>ВСЕ</u> товари!</b>"
        enter_name_for_create_ad_button = "<b>❗ Введіть назву для рекламної кнопки:</b>"
        enter_content_for_ad_button = "<b>❗ Введіть контент (повідомлення) кнопки:</b>"
        enter_photo_for_ad_button = "<b>❗ Надішліть фото кнопки, щоб пропустити введіть <code>-</code></b>"
        enter_links_buttons_for_ad_button = """<b>❗ Надішліть кнопки-посилання для цієї кнопки у форматі:
    
<code>Посилання #1|https://examle1.com
Посилання #2|https://example2.com</code>

❗ Щоб пропустити, введіть <code>-</code></b>"""
        ad_button_is_created_alert = "<b>❗ Адміністратор {username} створив рекламну кнопку <code>{name}</code>!</b>"
        ad_button_is_deleted_alert = "<b>❗ Адміністратор {username} видалив рекламну кнопку <code>{name}</code>!</b>"
        enter_name_for_delete_ad_button = "<b>❗ Введіть назву рекламної кнопки для видалення:</b>"
        enter_name_for_create_mail_button = "<b>❗ Введіть назву для кнопки у розсилці:</b>"
        select_button = "<b>❗ Виберіть кнопку:</b>"
        no_mail_buttons_available = "❗ Немає доступних кнопок! Створіть хоча б одну!"
        select_mail_button_type = "<b>❗ Виберіть тип кнопки:</b>"
        enter_link_for_mail_button = "<b>❗ Введіть посилання для кнопки у розсилці:</b>"
        select_contest = "<b>❗ Виберіть розіграш:</b>"
        enter_data_items = {
            "text": """<b>⚙️ Введіть дані товарів:
❗ Щоб відокремити товари, залишити порожній рядок між ними. Приклад:
❗ Ви можете скинути txt файл, де товари так само відокремлені один від одного.

<code>Товар #1...</code>

<code>Товар #2...</code>

<code>Товар #3...</code></b>""",
            "text_infinity": "<b>⚙️ Введіть дані товару</b>",
            "photo": """<b>⚙️ Надішліть фото товару (можна з підписом)

❗ Завантажуйте по одному</b>""",
            "file": """<b>⚙️ Надішліть файл товару (можна з підписом)

❗ Завантажуйте по одному</b>"""
        }
        products_add_wait = "<b>⌛ Чекайте, товари додаються...</b>"
        no_need_item_type_sent = "<b>❗ Надішліть потрібний тип товару!</b>"
        products_successful_added = "<b>✅ Товари в кількості <code>{count}шт</code> були успішно додані</b>"
        stop_upload_items_text = """<b>✅ Завантаження товарів було успішно завершено
⚙️ Завантажено товарів: <code>{count}шт</code></b>"""
        upload_items_error = "<b>❗ Щось пішло не так під час завантаження товарів! Спробуйте ще раз!</b>"
        list_of_items = "<b>🧾 Список товарів позиції <code>{name}</code></b>"
        get_list_of_items_error = "<b>❗ Щось пішло не так за спроби отримати список товарів! Спробуйте ще раз!</b>"
        position = "Позиція"
        item = "Товар"
        enter_item_id_for_delete = "<b>❗ Введіть ID товару для видалення:</b>"
        value_is_no_link = "<b>❗ Значення має бути посиланням! Спробуйте ще раз.:</b>"
        mail_button_text = """<b>✨ Кнопка: <code>{name}</code>
🌐 Значення: {data}
❗ Виберіть, що хочете змінити:</b>"""
        enter_new_mail_button_name = "<b>❗ Введіть нову назву для кнопки:</b>"
        confirm_mail_button_delete = "<b>❓ Ви впевнені, що хочете видалити кнопку розсилки <code>{name}</code>?</b>"
        enter_message_for_mail = "<b>❗ Введіть або надішліть повідомлення для розсилки:</b>"
        confirm_message_for_mail = "<b>❓ Чи впевнені, що хочете запустити розсилку з таким текстом?</b>"
        mail_started = "<b>✅ Розсилка запущена!</b>"
        mail_started_alert = "<b>❗ Адміністратор {username} запустив розсилку!</b>"
        success_mail_text = """<b>✅ Розсилка успішно завершена:
    
💎 Усього користувачів: <code>{all_users_count} чол.</code>
✅ Успішно надіслано: <code>{success_users_count} чол.</code>
❌ Бот заблоковано: <code>{failed_users_count} чол.</code></b>"""
        mail_error = "<b>❌ Під час розсилки сталася непередбачена помилка!</b>"
        select_what_you_want_to_find = "<b>⚙️ Виберіть, що хочете знайти:</b>"
        enter_user_profile = "<b>❗ Введіть ID, ім'я або @username користувача</b>"
        enter_receipt = "<b>❗ Введіть чек</b>"
        no_user_find = "<b>❗ Такого користувача немає! Перевірте ще раз дані!</b>"
        user_profile_found = """
<b>👤 Профіль:

💎 Користувач: {username}
🆔 ID: <code>{user_id}</code>

💰 Баланс: <code>{balance}{curr}</code>

💵 Усього поповнено: <code>{total_refill}{curr}</code>
🧾 Кількість поповнень: <code>{count_refills} шт.</code>

🛒 Кількість покупок: <code>{count_purchases} шт.</code>
💲 Покупок на суму: <code>{total_purchases}{curr}</code>

📌 Дата реєстрації: <code>{reg_date}</code>
🌐 Мова: <code>{language}</code>

👥 Рефералів: <code>{ref_count} чел</code>
🔰 Реферальний рівень: <code>{ref_lvl}</code>
🚚 Ким запрошено: <code>{ref_name}</code>
💸 Запрацював з рефералів: <code>{ref_earn}{curr}</code></b>
    """
        enter_sum_for_add_to_balance = "<b>💸 Введіть суму для додавання на баланс:</b>"
        enter_sum_for_minus_from_balance = "<b>💸 Введіть суму для віднімання з балансу:</b>"
        enter_sum_for_edit_balance = "<b>💸 Введіть новий баланс користувача:</b>"
        enter_sms_for_user = "<b>❗ Введіть повідомлення для користувача:</b>"
        new_balance_alert = "<b>❗ Адміністратор {username} змінив баланс користувача {user}!</b>"
        receipt_refill = """
<b>⭐ Чек <code>{receipt}</code>:

⚙️ Тип: <code>Поповненне</code>
💎 Користувач: {username}
📌 Спосіб: <code>{way}</code>
💰 Сума: <code>{sum}{curr}</code>
🎲 Дата: <code>{date}</code>
🔗 Посилання на оплату: {url}</b>
        """
        receipt_purchase = """
<b>⭐ Чек <code>{receipt}</code>:

⚙️ Тип: <code>Покупка</code>
💎 Користувач: {username}
📌 Товар: <code>{pos_name}</code>
💰 Сума: <code>{sum}{curr}</code>
🛒 Кількість: <code>{count}шт</code>
🎲 Дата: <code>{date}</code>
🔗 Вміст:</b>
        """
        new_purchase_alert = """
💰 Нова покупка!
👤 Користувач: <b>{user_name}</b> [<code>{user_id}</code>]
💵 Сума: <code>{amount}{curr}</code>
🧾 Чек: <code>{receipt}</code>
⚙️ Товар: <code>{pos_name} x{count}</code>"""
        no_receipt = "❗ Чек не знайдено, спробуйте ще раз:"
        select_payment = "<b>💰 Виберіть платіжну систему:</b>"
        payments_on_off = {
            True: "✅ Включено",
            False: "❌ Вимкнено",
        }
        payment_info = """
<b>{method}</b>

Статус: <code>{status}</code>"""
        balance_info = """
Платіжна система:
<b>{method}</b>

Баланс:
{balance}"""
        get_balance_error = "⚠️ Помилка при отриманні балансу! Можливо, ви не вставили дані для платіжної системи.!"
        payment_information_text = """
<b>{method}

💰 Поповнення:

За день: <code>{refills_count_for_day} шт.</code> (<code>{refills_for_day}{curr}</code>)
За тиждень: <code>{refills_count_for_week} шт.</code> (<code>{refills_for_week}{curr}</code>)
За місяць: <code>{refills_count_for_month} шт.</code> (<code>{refills_for_month}{curr}</code>)
За весь час: <code>{refills_count_for_all_time} шт.</code> (<code>{refills_for_all_time}{curr}</code>)

⚙ Інформація: 

{configs}
⭐ Виберіть, що хочете змінити:</b>
        """
        enter_new_value_for = "<b>❗ Введіть нове значення для {field}:</b>"
        stats_message = """
<b>📊 Статистика:</b>


<b>👤 Користувачі:</b>

👤 За день: <code>{users_day}</code>
👤 За тиждень: <code>{users_week}</code>
👤 За місяць: <code>{users_month}</code>
👤 За весь час: <code>{users_all}</code>

👤 Сумма балансов всех юзеров: <code>{users_money}{cur}</code>

<b>💸 Продажи:</b>

💸 За день: <code>{profit_count_day}шт</code> (<code>{profit_amount_day}{cur}</code>)
💸 За тиждень: <code>{profit_count_week}шт</code> (<code>{profit_amount_week}{cur}</code>)
💸 За місяць: <code>{profit_count_month}шт</code> (<code>{profit_amount_month}{cur}</code>)
💸 За весь час: <code>{profit_count_all}шт</code> (<code>{profit_amount_all}{cur}</code>)

<b>💰 Пополнения:</b>

💰 за день: <code>{refill_count_day}шт</code> (<code>{refill_amount_day}{cur}</code>)
💰 За тиждень: <code>{refill_count_week}шт</code> (<code>{refill_amount_week}{cur}</code>)
💰 За місяць: <code>{refill_count_month}шт</code> (<code>{refill_amount_month}{cur}</code>)
💰 За весь час: <code>{refill_count_all}шт</code> (<code>{refill_amount_all}{cur}</code>)

<b>⚙️ Адміни: </b>

⚙️ Усього адмінів: <code>{admins} чол.</code>
⚙️ Адміни: \n"""
        users_balances_txt_text = """Сума: {rub}₽ | {usd}$ | {eur}€

Усі користувачі та його баланси більше 0:

{users_balances}
        """
        all_users_and_their_balances="<b>⚙️ Усі користувачі та його баланси</b>"
        list_of_all_users_ids = "<b>⚙️ Список ID всіх користувачів</b>"
        sum_is_zero_and_no_users_with_balance = "❗ Сума балансів дорівнює 0, немає користувачів із балансом більше 0!"
        contest_is_start_successful = "🎉 Розіграш успішно запущено!"
        edit_contest_settings = """
<b>Зміна <code>{action}</code>
Поточне значення:
{value}

Введіть нове значення:</b>
    """
        contests_settings_values = {
            "winners_num": "Кількість переможців",
            "prize": "Приз",
            "members_num": "Кількість учасників",
            "end_time": "Час розіграшу",
            "purchases_num": "Кількість покупок",
            "refills_num": "Кількість поповнень",
            "channels_ids": "ID каналів для передплати"
        }
        enter_channels_ids = "<b>❗ Введіть ID каналів для передплати через кому. \nПриклад: -12345678910, -12423562345 \n\nВведіть <code>-</code> Якщо не хочете ставити. \n\nПоточне значення: {value}</b>"
        user_is_entered_contest_alert = "<b>❗ Користувач {user} [<code>{user_id}</code>] бере участь у розіграші на <code>{prize}{cur}</code></b>"
        contest_is_finished_and_members_are_zero_alert = "❗ У розіграші на {prize} {cur} ніхто не виграв, т.к. учасників 0!"
        contest_is_finished_alert = "❗ У розіграші на {prize} {cur} виграли:\n"
        prize_given = "\n\n❗ Приз було видано! ❗"