from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.data import config as config_file
from tgbot import utils


class InlineButtons:

    def custom_button(self, texts, callback_data, name=None):
        if not name:
            name = texts.BUTTONS.back
        return InlineKeyboardBuilder().button(text=name, callback_data=callback_data)
    
    def admin_panel(self, texts):
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.main_settings, callback_data="main_settings"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.extra_settings, callback_data="extra_settings"),
        )
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.switchers, callback_data="switchers"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.find, callback_data="find"),
        )
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.statistic, callback_data="stats"))
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.products_manage, callback_data="products_manage"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.payments_systems, callback_data="payments"),
        )
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.mail, callback_data="mail_start")
        )
        # Кнопка для управления Steam Points
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.steam_management, callback_data="steam_management")
        )
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.mail_buttons, callback_data="mail_buttons"),
        )
        builder.row(
            InlineKeyboardButton(text="📢 Уведомления", callback_data="notifications"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.ad_buttons, callback_data="ad_buttons")
        )
        builder.row(
            InlineKeyboardButton(text="🧹 Очистить невалидных пользователей", callback_data="clean_invalid_users")
        )
        builder.row(
            InlineKeyboardButton(text="📋 Документы", callback_data="legal_documents"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.contests, callback_data="contests_admin")
        )
        builder.row(
            InlineKeyboardButton(text="📊 Логи системы", callback_data="system_logs")
        )
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="back_to_user_menu"))
        return builder
    
    async def switchers_kb(self, texts):
        builder = InlineKeyboardBuilder()
        settings = await config_file.DB.get_settings()
        builder.row(
            InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.switchers_settings['tech_works']} | {'✅' if settings.is_work else '❌'}", callback_data="switchers:is_work"),
            InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.switchers_settings['buys']} | {'✅' if settings.is_buy else '❌'}", callback_data="switchers:is_buy"),
        )
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.switchers_settings['refills']} | {'✅' if settings.is_refill else '❌'}", callback_data="switchers:is_refill"))
        builder.row(
            InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.switchers_settings['ref']} | {'✅' if settings.is_ref else '❌'}", callback_data="switchers:is_ref"),
            InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.switchers_settings['contests']} | {'✅' if settings.contests_is_on else '❌'}", callback_data="switchers:contests_is_on"),
        )
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.switchers_settings['notify']} | {'✅' if settings.is_notify else '❌'}", callback_data="switchers:is_notify"))
        builder.row(
            InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.switchers_settings['keyboard']} | {settings.keyboard.value}", callback_data="switchers:keyboard"),
            InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.switchers_settings['sub']} | {'✅' if settings.is_sub else '❌'}", callback_data="switchers:is_sub"),
        )
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.switchers_settings['multi_lang']} | {'✅' if settings.multi_lang else '❌'}", callback_data="switchers:multi_lang"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder
    
    async def main_settings(self, texts):
        builder = InlineKeyboardBuilder()
        settings = await config_file.DB.get_settings()
        builder.row(
            InlineKeyboardButton(text=f"FAQ | {'❌' if settings.faq is None or settings.faq in ['-', 'None'] else '✅'}", callback_data="main_settings:faq"),
            InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.main_settings_values['support']} | {'❌' if settings.support is None or settings.support in ['-', 'None'] else '✅'}", callback_data="main_settings:support"),
        )
        builder.row(
            InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.main_settings_values['chat']} | {'❌' if settings.chat is None or settings.chat in ['-', 'None'] else '✅'}", callback_data="main_settings:chat"),
            InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.main_settings_values['news']} | {'❌' if settings.news is None or settings.news in ['-', 'None'] else '✅'}", callback_data="main_settings:news"),
        )
        # Добавляем кнопку загрузки FAQ из файла
        builder.row(InlineKeyboardButton(text="📝 Загрузить FAQ из файла", callback_data="load_faq_from_file"))
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.main_settings_values['ref_percent_1']} | {settings.ref_percent_1}%", callback_data="main_settings:ref_percent:1"))
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.main_settings_values['ref_percent_2']} | {settings.ref_percent_2}%", callback_data="main_settings:ref_percent:2"))
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.main_settings_values['ref_percent_3']} | {settings.ref_percent_3}%", callback_data="main_settings:ref_percent:3"))
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.main_settings_values['default_lang']} | {(next((language for language in config_file.BotConfig.LANGUAGES if language['language'] == settings.default_lang.value), None))['name']}", callback_data="main_settings:default_lang"))
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.main_settings_values['currency']} | {config_file.BotConfig.CURRENCIES[settings.currency.value]['sign']}", callback_data="main_settings:currency"))
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.main_settings_values['refill_commission_percent']} | {settings.refill_commission_percent}%", callback_data="main_settings:refill_commission_percent"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder
    
    def currencies_kb(self, texts):
        builder = InlineKeyboardBuilder()
        currencies = config_file.BotConfig.CURRENCIES
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.currencies['rub']} | {currencies['rub']['text']} | {currencies['rub']['sign']}",
                                callback_data="edit_main_setting:rub"))
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.currencies['usd']} | {currencies['usd']['text']} | {currencies['usd']['sign']}",
                                callback_data="edit_main_setting:usd"))
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.currencies['eur']} | {currencies['eur']['text']} | {currencies['eur']['sign']}",
                                callback_data="edit_main_setting:eur"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="main_settings"))
        return builder

    async def langs_kb(self, texts):
        builder = InlineKeyboardBuilder()
        for lang in config_file.BotConfig.LANGUAGES:
            builder.row(InlineKeyboardButton(text=lang['name'], callback_data=f"edit_main_setting:{lang['language']}"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="main_settings"))
        return builder
    
    async def extra_settings_kb(self, texts):
        builder = InlineKeyboardBuilder()
        settings = await config_file.DB.get_settings()
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.create_promocode, callback_data="extra_settings:promo_create"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.delete_promocode, callback_data="extra_settings:promo_delete"),
        )
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.edit_number_of_refs_for_ref_lvl_2} | {settings.ref_lvl_2}", 
                                         callback_data="extra_settings:ref_lvl:2"))
        builder.row(InlineKeyboardButton(text=f"{texts.ADMIN_TEXTS.edit_number_of_refs_for_ref_lvl_3} | {settings.ref_lvl_3}",
                                         callback_data="extra_settings:ref_lvl:3"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder 

    def products_manage(self, texts):
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.add_category, callback_data=f"add_category"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.edit_category, callback_data=f"edit_category"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.del_all_categories, callback_data=f"del_all_categories"),
        )
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.add_subcategory, callback_data=f"add_subcategory"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.edit_subcategory, callback_data=f"edit_subcategory"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.del_all_subcategories, callback_data=f"del_all_subcategories"),
        )
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.add_position, callback_data=f"add_position"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.edit_position, callback_data=f"edit_position"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.del_all_positions, callback_data=f"del_all_positions"),
        )
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.add_items, callback_data=f"add_items"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.del_item, callback_data=f"del_item"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.del_all_items, callback_data=f"del_all_items"),
        )
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder
    
    def category_select_menu(self, texts, categories):
        builder = InlineKeyboardBuilder()
        for category in categories:
            builder.row(InlineKeyboardButton(text=category.name, callback_data=f"select_category:{category.cat_id}"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder
    
    def subcategory_select_menu(self, texts, subcategories, is_for_add_position=False, is_for_edit_position=False, positions=None):
        builder = InlineKeyboardBuilder()
        for subcategory in subcategories:
            builder.row(InlineKeyboardButton(text=subcategory.name, callback_data=f"select_subcategory:{subcategory.sub_cat_id}"))
        if is_for_edit_position:
            builder = self.position_select_menu(texts, positions, builder)
        if is_for_add_position:
            builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.select_this_category, callback_data=f"select_category:{subcategories[0].cat_id}:this"))
        if not is_for_edit_position:
            builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder
    
    def position_select_menu(self, texts, positions, builder=None):
        if not builder:
            builder = InlineKeyboardBuilder()
        for position in positions:
            builder.row(InlineKeyboardButton(text=position.name, callback_data=f"select_position:{position.pos_id}"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder

    def category_edit(self, texts, category_id, is_sub=False):
        builder = InlineKeyboardBuilder()
        if is_sub:
            builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.name, callback_data=f"edit_subcategory:{category_id}:name"))
            builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.delete, callback_data=f"edit_subcategory:{category_id}:delete"))
            builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.move, callback_data=f"edit_subcategory:{category_id}:move"))
        else:
            builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.name, callback_data=f"edit_category:{category_id}:name"))
            builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.delete, callback_data=f"edit_category:{category_id}:delete"))

        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder
    
    def position_edit(self, texts, position_id):
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.price, callback_data=f"position_edit:{position_id}:price"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.name, callback_data=f"position_edit:{position_id}:name")
        )
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.description, callback_data=f"position_edit:{position_id}:description"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.photo, callback_data=f"position_edit:{position_id}:photo"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.position_type_text, callback_data=f"position_edit:{position_id}:position_type"),
        )
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.delete, callback_data=f"position_edit:{position_id}:delete"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.move, callback_data=f"position_edit:{position_id}:move")
        )
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.clear_items, callback_data=f"position_edit:{position_id}:clear_items"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.upload_items, callback_data=f"position_edit:{position_id}:upload_items")
        )
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.get_items, callback_data=f"position_edit:{position_id}:get_items"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="edit_position"))
        return builder
    
    def position_edit_paginated(self, texts, position_id, current_page, total_pages):
        """Клавиатура для редактирования позиции с пагинацией"""
        builder = InlineKeyboardBuilder()
        
        # Основные кнопки редактирования (только на первой странице)
        if current_page == 0:
            builder.row(
                InlineKeyboardButton(text=texts.ADMIN_TEXTS.price, callback_data=f"position_edit:{position_id}:price"),
                InlineKeyboardButton(text=texts.ADMIN_TEXTS.name, callback_data=f"position_edit:{position_id}:name")
            )
            builder.row(
                InlineKeyboardButton(text=texts.ADMIN_TEXTS.description, callback_data=f"position_edit:{position_id}:description"),
                InlineKeyboardButton(text=texts.ADMIN_TEXTS.photo, callback_data=f"position_edit:{position_id}:photo"),
                InlineKeyboardButton(text=texts.ADMIN_TEXTS.position_type_text, callback_data=f"position_edit:{position_id}:position_type"),
            )
            builder.row(
                InlineKeyboardButton(text=texts.ADMIN_TEXTS.delete, callback_data=f"position_edit:{position_id}:delete"),
                InlineKeyboardButton(text=texts.ADMIN_TEXTS.move, callback_data=f"position_edit:{position_id}:move")
            )
            builder.row(
                InlineKeyboardButton(text=texts.ADMIN_TEXTS.clear_items, callback_data=f"position_edit:{position_id}:clear_items"),
                InlineKeyboardButton(text=texts.ADMIN_TEXTS.upload_items, callback_data=f"position_edit:{position_id}:upload_items")
            )
            builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.get_items, callback_data=f"position_edit:{position_id}:get_items"))
        
        # Кнопки навигации (если больше одной страницы)
        if total_pages > 1:
            nav_buttons = []
            if current_page > 0:
                nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"position_page:{position_id}:{current_page-1}"))
            if current_page < total_pages - 1:
                nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"position_page:{position_id}:{current_page+1}"))
            
            if nav_buttons:
                builder.row(*nav_buttons)
            
            # Индикатор страницы
            builder.row(InlineKeyboardButton(text=f"📄 {current_page + 1}/{total_pages}", callback_data="noop"))
        
        # Кнопка "Назад"
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="edit_position"))
        return builder

    def confirm(self, callback_data1, callback_data2):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="✅", callback_data=callback_data1),
                    InlineKeyboardButton(text="❌", callback_data=callback_data2))
        return builder
    
    def position_item_types(self, texts):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.photo, callback_data=f"select_position_type:photo"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.text, callback_data=f"select_position_type:text"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.file_, callback_data=f"select_position_type:file"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="products_manage"))
        return builder
    
    def ad_buttons_actions(self, texts):
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.create, callback_data="ad_buttons:create"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.delete, callback_data="ad_buttons:delete"),
        )
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder
    
    def mail_buttons_actions(self, texts):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.create, callback_data="mail_buttons:create"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.current_buttons, callback_data="mail_buttons:current"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder
    
    def mail_button_types(self, texts):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.open_category_button, callback_data="mail_button_type:category"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.open_subcategory_button, callback_data="mail_button_type:subcategory"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.open_position_button, callback_data="mail_button_type:position"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.open_contest_button, callback_data="mail_button_type:contest"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.link_button, callback_data="mail_button_type:link"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="mail_buttons"))
        return builder

    def mail_buttons(self, texts, buttons):
        builder = InlineKeyboardBuilder()
        for button in buttons:
            builder.row(InlineKeyboardButton(text=f"{button.name} | {texts.ADMIN_TEXTS.mail_buttons_types[button.button_type.split('|')[0]]}",
                                             callback_data=f"edit_mail_button:{button.button_id}"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="mail_buttons"))
        return builder
    
    def mail_buttons_edit(self, texts, button_id):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.name, callback_data=f"mail_button_edit:{button_id}:name"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.delete, callback_data=f"mail_button_edit:{button_id}:delete"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="mail_buttons:current"))
        return builder
    
    async def buttons_for_mail(self, texts):
        builder = InlineKeyboardBuilder()
        buttons = await config_file.DB.get_mail_buttons()
        for button in buttons:
            button_type, value = button.button_type.split("|")
            if button_type == "link":
                builder.row(InlineKeyboardButton(text=button.name, url=value.strip()))
            elif button_type == "category":
                builder.row(InlineKeyboardButton(text=button.name, callback_data=f"mail_category_open:{value}"))
            elif button_type == "subcategory":
                builder.row(InlineKeyboardButton(text=button.name, callback_data=f"mail_subcategory_open:{value}"))
            elif button_type == "position":
                builder.row(InlineKeyboardButton(text=button.name, callback_data=f"mail_position_open:{value}"))
            else:
                # contest
                builder.row(InlineKeyboardButton(text=button.name, callback_data=f"mail_contest_open:{value}"))
        return builder
    
    def find_settings(self, texts):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.profile, callback_data="find:profile"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.receipt, callback_data="find:receipt"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder

    def user_profile_actions(self, texts, user_id, is_ban):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.edit_balance, callback_data=f"user_edit:balance:{user_id}"))
        if is_ban:
            builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.unban, callback_data=f"user_edit:unban:{user_id}"))
        else:
            builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.ban, callback_data=f"user_edit:ban:{user_id}"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.send_message, callback_data=f"user_edit:sms:{user_id}"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="find:profile"))
        return builder
    
    def edit_balance(self, texts, user_id):
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.add_balance, callback_data=f"user_edit:add_balance:{user_id}"),
            InlineKeyboardButton(text=texts.ADMIN_TEXTS.minus_balance, callback_data=f"user_edit:minus_balance:{user_id}")
        )
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.edit_bal, callback_data=f"user_edit:edit_balance:{user_id}"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data=f"user_edit:back:{user_id}"))
        return builder
    
    async def payments_settings(self, texts, payments: dict):
        builder = InlineKeyboardBuilder()
        for payment in payments.items():
            builder.add(
                InlineKeyboardButton(
                    text=f"[{'✅' if payment[1] else '❌'}] {texts.TEXTS.payments_names[payment[0]]}",
                    callback_data=f"payments:{payment[0]}",
                )
            )
        settings = await config_file.DB.get_settings()
        builder.add(InlineKeyboardButton(
            text=f"[{'✅' if settings.is_custom_pay_method_on else '❌'}] {settings.custom_pay_method}",
            callback_data=f"payments:custom_pay_method"
            
        ))
        builder.adjust(2)
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder
    
    def payments_settings_info(self, texts, method, status, custom_pay_method_is_receipt_on = None):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.disable if status else texts.ADMIN_TEXTS.enable,
                                         callback_data=f"payment_action:{method}:enable_or_disable"))
        if method == "custom_pay_method":
            builder.row(InlineKeyboardButton(
                text=texts.ADMIN_TEXTS.edit_custom_pay_method_receipt.format(status="✅" if custom_pay_method_is_receipt_on else '❌'),
                callback_data="payment_action:custom_pay_method:receipt"
            ))
            builder.row(InlineKeyboardButton(
                text=texts.ADMIN_TEXTS.edit_custom_pay_method_name,
                callback_data="payment_action:custom_pay_method:name"
            ))
            builder.row(InlineKeyboardButton(
                text=texts.ADMIN_TEXTS.edit_custom_pay_method_text,
                callback_data="payment_action:custom_pay_method:text"
            ))
            builder.row(InlineKeyboardButton(
                text=texts.ADMIN_TEXTS.edit_custom_pay_method_min_amount,
                callback_data="payment_action:custom_pay_method:min"
            ))
        else:
            builder.row(
                InlineKeyboardButton(text=texts.ADMIN_TEXTS.get_balance, callback_data=f"payment_action:{method}:balance"),
                InlineKeyboardButton(text=texts.ADMIN_TEXTS.show_info, callback_data=f"payment_action:{method}:info")
            )
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="payments"))
        return builder
    
    def payments_info(self, texts, payments_config, method):
        builder = InlineKeyboardBuilder()
        for cfg in payments_config:
            builder.add(
                InlineKeyboardButton(
                    text=cfg.text, 
                    callback_data=f"payment_action:{method}:edit_cfg:{cfg.field}"
                )
            )
        builder.adjust(2)
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data=f"payments:{method}"))
        return builder

    def stats_inl(self, texts):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.get_users_and_their_balances, 
                                         callback_data="get_users_and_their_balances"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.get_users_ids, 
                                         callback_data="get_users_ids"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder
    
    async def contests_inl(self, texts):
        builder = InlineKeyboardBuilder()
        settings = await config_file.DB.get_contests_settings()
        cur = config_file.BotConfig.CURRENCIES[(await config_file.DB.get_settings()).currency.value]['sign']
        
        builder.row(InlineKeyboardButton(text=f'{texts.ADMIN_TEXTS.winners_count} | {settings.winners_num}',
                                         callback_data="edit_contest_settings:winners_num"))
        builder.row(InlineKeyboardButton(text=f'{texts.ADMIN_TEXTS.prize} | {settings.prize}{cur}',
                                         callback_data="edit_contest_settings:prize"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.conditions, callback_data="edit_contest_settings:conditions"))
        builder.row(InlineKeyboardButton(text=f'{texts.ADMIN_TEXTS.members_count} | {settings.members_num}',
                                         callback_data="edit_contest_settings:members_num"))
        builder.row(InlineKeyboardButton(text=f'{texts.ADMIN_TEXTS.contest_time} | {settings.end_time}',
                                         callback_data="edit_contest_settings:end_time"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.end_contest_now, callback_data="cancel_contest_now"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.start_contest, callback_data='start_contest'))

        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data='admin_panel'))
        return builder
    
    async def contests_conditions_inl(self, texts):
        builder = InlineKeyboardBuilder()
        settings = await config_file.DB.get_contests_settings()
        
        builder.row(InlineKeyboardButton(text=f'{texts.ADMIN_TEXTS.purchases_count} | {settings.purchases_num}',
                                         callback_data="edit_contest_settings:purchases_num"))
        builder.row(InlineKeyboardButton(text=f'{texts.ADMIN_TEXTS.refills_count} | {settings.refills_num}',
                                         callback_data="edit_contest_settings:refills_num"))
        builder.row(InlineKeyboardButton(text=f'{texts.ADMIN_TEXTS.channels_ids_for_sub} {len(utils.utils.get_channels(settings.channels_ids))}',
                                         callback_data="edit_contest_settings:channels_ids"))
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="contests_admin"))
        return builder
    
    def choose_contest(self, texts, contests, is_for_cancel = False):
        builder = InlineKeyboardBuilder()
        for contest in contests:
            end_time = utils.utils.get_time_for_end_contest(contest, texts.TEXTS.day_s)
            builder.row(InlineKeyboardButton(
                text=f"#{contest.contest_id} 🎉 | {contest.prize}{config_file.BotConfig.CURRENCIES[contest.currency.value]['sign']} | {end_time}",
                callback_data=f"cancel_contest_confirm:{contest.contest_id}:yes" if is_for_cancel else f"choose_contest:{contest.contest_id}"
            ))
            
        return builder
    
    def legal_documents_menu(self, texts):
        """Меню управления правовыми документами"""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.terms_of_service, callback_data="legal_doc:terms"),
            InlineKeyboardButton(text=texts.BUTTONS.privacy_policy, callback_data="legal_doc:privacy")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.user_agreement, callback_data="legal_doc:agreement")
        )
        builder.row(InlineKeyboardButton(text=texts.ADMIN_TEXTS.back, callback_data="admin_panel"))
        return builder

    def faq_pagination(self, texts, current_page, total_pages, action="faq"):
        """
        Создает клавиатуру для навигации по страницам FAQ
        """
        builder = InlineKeyboardBuilder()
        
        # Кнопки навигации
        nav_buttons = []
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"faq_page:{action}:{current_page - 1}"))
        
        nav_buttons.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="current_page"))
        
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"faq_page:{action}:{current_page + 1}"))
        
        if nav_buttons:
            builder.row(*nav_buttons)
        
        # Кнопка назад
        builder.row(InlineKeyboardButton(text=texts.BUTTONS.back, callback_data="main_settings"))
        return builder

    # ===== Новые методы для управления отзывами и Steam Points =====
    
    # Удалено: все методы управления отзывами
    
    def steam_management(self):
        """Кнопки управления Steam Points"""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="steam_settings"),
            InlineKeyboardButton(text="📋 Заказы", callback_data="steam_orders")
        )
        builder.row(
            InlineKeyboardButton(text="📊 Статистика", callback_data="steam_stats"),
            InlineKeyboardButton(text="💰 Баланс API", callback_data="steam_balance")
        )
        builder.row(
            InlineKeyboardButton(text="🔄 Вкл/Выкл", callback_data="toggle_steam_status")
        )
        builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel"))
        return builder
    
    def steam_settings(self):
        """Настройки Steam Points"""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="💰 Цена за очко", callback_data="change_steam_price"),
            InlineKeyboardButton(text="📈 Комиссия", callback_data="change_steam_commission")
        )
        builder.row(
            InlineKeyboardButton(text="🔄 Обновить цену", callback_data="update_steam_price"),
            InlineKeyboardButton(text="🔑 API ключ", callback_data="change_steam_api_key")
        )
        builder.row(
            InlineKeyboardButton(text="🔄 Статус", callback_data="toggle_steam_status")
        )
        builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="steam_management"))
        return builder
    
    def back_to_steam_settings(self):
        """Кнопка возврата к настройкам Steam"""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="⬅️ К настройкам", callback_data="steam_settings"))
        return builder
    
    def back_to_steam(self):
        """Кнопка возврата к Steam панели"""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="⬅️ К Steam", callback_data="steam_management"))
        return builder
    
    
    def back_to_admin(self):
        """Кнопка возврата к админ панели"""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="⬅️ Админ панель", callback_data="admin_panel"))
        return builder
    
    def steam_orders_menu(self):
        """Меню заказов Steam"""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="🔄 Обновить", callback_data="steam_orders"),
            InlineKeyboardButton(text="⏳ В обработке", callback_data="pending_steam_orders")
        )
        builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="steam_management"))
        return builder
    
    def system_logs_menu(self):
        """Меню логов системы"""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="📋 Список логов", callback_data="logs_list"),
            InlineKeyboardButton(text="⬇️ Скачать все", callback_data="download_all_logs")
        )
        builder.row(
            InlineKeyboardButton(text="📊 Системные", callback_data="download_log:system.log"),
            InlineKeyboardButton(text="🎮 Steam API", callback_data="download_log:steam_api.log")
        )
        builder.row(
            InlineKeyboardButton(text="❌ Ошибки Telegram", callback_data="download_log:telegram_errors.log"),
            InlineKeyboardButton(text="👥 Операции пользователей", callback_data="download_log:user_operations.log")
        )
        builder.row(InlineKeyboardButton(text="⬅️ Админ панель", callback_data="admin_panel"))
        return builder
    
    def logs_list_keyboard(self, log_files):
        """Клавиатура со списком лог-файлов"""
        builder = InlineKeyboardBuilder()
        
        for log_file in log_files:
            # Эмодзи в зависимости от типа файла
            if 'system' in log_file['name']:
                emoji = "📊"
            elif 'steam' in log_file['name']:
                emoji = "🎮"
            elif 'telegram' in log_file['name']:
                emoji = "❌"
            elif 'user' in log_file['name']:
                emoji = "👥"
            else:
                emoji = "📄"
                
            # Размер файла в читаемом формате
            size_mb = log_file['size'] / (1024 * 1024)
            if size_mb < 1:
                size_str = f"{log_file['size'] / 1024:.1f} KB"
            else:
                size_str = f"{size_mb:.1f} MB"
                
            button_text = f"{emoji} {log_file['name']} ({size_str})"
            builder.row(InlineKeyboardButton(text=button_text, callback_data=f"download_log:{log_file['name']}"))
        
        builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="system_logs"))
        return builder



# Создаем экземпляр класса для использования в других модулях
ADMIN_INLINE = InlineButtons()
