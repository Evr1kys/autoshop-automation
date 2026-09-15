from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot import utils
from tgbot.data import config as config_file

class InlineButtons:
    async def profile_menu(self, texts):
        builder = InlineKeyboardBuilder()
        settings = await config_file.DB.get_settings()
        
        # Добавляем кнопку пополнения, если включена
        if settings.is_refill:
            enabled_payments = await config_file.DB.get_enabled_payments()
            if enabled_payments:
                builder.row(
                    InlineKeyboardButton(
                        text=texts.BUTTONS.topup_balance,
                        callback_data="refill"
                    )
                )
        
        # Добавляем кнопку розыгрышей, если включена
        if settings.contests_is_on:
            builder.row(
                InlineKeyboardButton(
                    text=texts.BUTTONS.contests,
                    callback_data="contests"
                )
            )
        
        if settings.is_ref:
            builder.row(
                InlineKeyboardButton(
                    text=texts.BUTTONS.ref_system,
                    callback_data="ref_system"
                )
            )
            
        builder.row(
            InlineKeyboardButton(
                text=texts.BUTTONS.activate_promo,
                callback_data="activate_promo"),
            InlineKeyboardButton(
                text=texts.BUTTONS.purchases_history,
                callback_data="purchases_history",
            )
        )
        

        
        # Кнопка документов
        builder.row(
            InlineKeyboardButton(
                text=texts.BUTTONS.legal_documents,
                callback_data="user_legal_menu"
            )
        )
        
        if settings.multi_lang:
            builder.row(
                InlineKeyboardButton(
                    text=texts.BUTTONS.change_language,
                    callback_data="change_language",
                )
            )
        builder.row(InlineKeyboardButton(
            text=texts.BUTTONS.back,
            callback_data="back_to_user_menu"
        ))
        return builder

    async def support(self, texts):
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text=texts.BUTTONS.support_text,
                url=(await config_file.DB.get_settings()).support
            )
        )
        builder.row(InlineKeyboardButton(
            text=texts.BUTTONS.back,
            callback_data="back_to_user_menu"
        ))
        return builder

    async def faq(self, texts):
        builder = InlineKeyboardBuilder()
        settings = await config_file.DB.get_settings()
        
        if settings.news and settings.news != "-":
            builder.row(
                InlineKeyboardButton(
                    text=texts.BUTTONS.faq_news_inl,
                    url=settings.news
                )
            )
        if settings.chat and settings.chat != "-":
            builder.row(
                InlineKeyboardButton(
                    text=texts.BUTTONS.faq_chat_inl,
                    url=settings.chat
                )
            )
        builder.row(InlineKeyboardButton(
            text=texts.BUTTONS.back,
            callback_data="back_to_user_menu"
        ))
        return builder

    def close(self, texts):
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text=texts.BUTTONS.close,
                callback_data="close",
            )
        )
        return builder

    async def get_refill_kb(self, texts, payments):
        builder = InlineKeyboardBuilder()
        for payment in payments:
            builder.row(
                InlineKeyboardButton(
                    text=texts.TEXTS.payments_names[payment],
                    callback_data=f"refill:{payment}",
                )
            )
        settings = await config_file.DB.get_settings()
        if settings.is_custom_pay_method_on:
            builder.row(InlineKeyboardButton(
                text=settings.custom_pay_method,
                callback_data="refill:custom_pay_method",
            ))
        builder.adjust(2)
        builder.row(InlineKeyboardButton(
            text=texts.BUTTONS.back,
            callback_data="back_to_user_menu"
        ))
        return builder

    def custom_button(self, texts, callback_data, name=None):
        if not name:
            name = texts.BUTTONS.back
        return InlineKeyboardBuilder().button(text=name, callback_data=callback_data)

    def refill_inl(self, texts, way, amount, url, pay_id, second_amount):
        builder = InlineKeyboardBuilder()
        builder.button(text=texts.BUTTONS.refill_link_inl, url=url)
        builder.row(InlineKeyboardButton(text=texts.BUTTONS.refill_check_inl, callback_data=f"check_pay:{way}:{amount}:{pay_id}:{second_amount}"))
        builder.row(InlineKeyboardButton(text=texts.BUTTONS.cancel, callback_data=f"cancel_pay:{pay_id}"))
        return builder
    
    def custom_pay_method_check(self, texts, pay_id):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text=texts.BUTTONS.send_payment_to_check,
            callback_data=f"check_custom_pay_method:{pay_id}"
        ))
        builder.row(InlineKeyboardButton(
            text=texts.BUTTONS.cancel, 
            callback_data=f"cancel_pay:{pay_id}"
        ))
        return builder

    def ad_buttons_links_buttons(self, texts, links, is_back=False):
        try:
            builder = InlineKeyboardBuilder()
            if not links and is_back:
                builder.row(
                    InlineKeyboardButton(
                        text=texts.BUTTONS.back,
                        callback_data="back_to_user_menu",
                    )
                )
                return builder.as_markup()
            links = links.split("\n")
            if links:
                for link in links:
                    try:
                        name, url = link.split("|")
                        try:
                            builder.row(InlineKeyboardButton(text=name, url=url.strip()))
                        except:
                            continue
                    except ValueError:
                        continue
                if is_back:
                    builder.row(
                        InlineKeyboardButton(
                            text=texts.BUTTONS.back,
                            callback_data="back_to_user_menu",
                        )
                    )
                return builder.as_markup()
            else:
                name, url = links.split("|")
                if name and url:
                    try:
                        builder.row(InlineKeyboardButton(text=name, url=url.strip()))
                        if is_back:
                            builder.row(
                                InlineKeyboardButton(
                                    text=texts.BUTTONS.back,
                                    callback_data="back_to_user_menu",
                                )
                            )
                        return builder.as_markup()
                    except:
                        return None
                else:
                    return None
        except:
            return None
        
    def select_category(self, texts, categories):
        builder = InlineKeyboardBuilder()
        for category in categories:
            builder.row(InlineKeyboardButton(text=category.name, callback_data=f"open_category:{category.cat_id}"))
        builder.adjust(2)
        builder.row(InlineKeyboardButton(text=texts.BUTTONS.back, callback_data="back_to_user_menu"))
        return builder

    async def select_subcategories_and_positions(self, texts, subcategories, positions):
        builder = InlineKeyboardBuilder()
        settings = await config_file.DB.get_settings()

        for sub_category in subcategories:
            builder.row(InlineKeyboardButton(text=sub_category.name, callback_data=f"open_subcategory:{sub_category.sub_cat_id}"))
        for position in positions:
            if position.sub_cat_id is not None:
                continue
            match settings.currency.value:
                case "rub":
                    price = position.price_rub
                case "usd":
                    price = position.price_usd
                case "eur":
                    price = position.price_eur
            if position.is_infinity:
                items = texts.BUTTONS.nolimit
            else:
                items = f"{len(await config_file.DB.get_items(pos_id=position.pos_id))} {texts.BUTTONS.pcs}"
            builder.row(InlineKeyboardButton(text=texts.BUTTONS.position_button_name.format(
                name=position.name,
                price=price,
                curr=config_file.BotConfig.CURRENCIES[settings.currency.value]['sign'],
                items=items,
            ), callback_data=f"open_position:{position.pos_id}"))
        builder.adjust(2)
        builder.row(InlineKeyboardButton(text=texts.BUTTONS.back, callback_data=f"buy"))
        return builder

    async def select_positions(self, texts, positions):
        builder = InlineKeyboardBuilder()
        settings = await config_file.DB.get_settings()
        for position in positions:
            match settings.currency.value:
                case "rub":
                    price = position.price_rub
                case "usd":
                    price = position.price_usd
                case "eur":
                    price = position.price_eur
            if position.is_infinity:
                items = texts.BUTTONS.nolimit
            else:
                items = f"{len(await config_file.DB.get_items(pos_id=position.pos_id))} {texts.BUTTONS.pcs}"
            builder.row(InlineKeyboardButton(text=texts.BUTTONS.position_button_name.format(
                name=position.name,
                price=price,
                curr=config_file.BotConfig.CURRENCIES[settings.currency.value]['sign'],
                items=items,
            ), callback_data=f"open_position:{position.pos_id}"))
        builder.adjust(2)
        builder.row(InlineKeyboardButton(text=texts.BUTTONS.back, callback_data=f"open_category:{positions[0].cat_id}"))
        return builder

    def position_buy(self, texts, position):
        builder = InlineKeyboardBuilder()
        
        buy_text = texts.BUTTONS.buy
            
        builder.row(InlineKeyboardButton(text=buy_text, callback_data=f"buy_position:{position.pos_id}"))
        builder.row(InlineKeyboardButton(text=texts.BUTTONS.back, callback_data=f"open_subcategory:{position.sub_cat_id}" if position.sub_cat_id else f"open_category:{position.cat_id}"))    
        return builder
    
    def confirm_buy_item(self, position_id, count):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="✅", callback_data=f"buy_item_confirm:{position_id}:{count}"),
                    InlineKeyboardButton(text="❌", callback_data=f"open_position:{position_id}"))
        return builder
    
    
    def choose_contest(self, texts, contests):
        builder = InlineKeyboardBuilder()
        for contest in contests:
            end_time = utils.utils.get_time_for_end_contest(contest, texts.TEXTS.day_s)
            builder.row(InlineKeyboardButton(
                text=f"#{contest.contest_id} 🎉 | {contest.prize}{config_file.BotConfig.CURRENCIES[contest.currency.value]['sign']} | {end_time}",
                callback_data=f"contest_view:{contest.contest_id}"
            ))
        builder.row(InlineKeyboardButton(
            text=texts.BUTTONS.back,
            callback_data="profile"
        ))
        return builder
    
    async def contest_inl(self, texts, contest, user):
        # Local import avoids a config -> keyboards -> loader -> config cycle.
        from tgbot.data import loader

        builder = InlineKeyboardBuilder()
        purchases = (await config_file.DB.get_purchases_stats_for_user(user.user_id))['count_purchases']
        count_success, count_conditions, channels_count = 0, 0, 0

        if contest.refills_num > 0:
            count_conditions += 1
            if user.count_refills >= contest.refills_num:
                count_success += 1
        if contest.purchases_num > 0:
            count_conditions += 1
            if purchases >= contest.purchases_num:
                count_success += 1
        if len(utils.utils.get_channels(contest.channels_ids)) > 0:
            count_conditions += 1
            channels_ids = utils.utils.get_channels(contest.channels_ids)
            for channel_id in channels_ids:
                user_status = await loader.bot.get_chat_member(chat_id=channel_id, user_id=user.user_id)
                if user_status.status != 'left':
                    channels_count += 1

            if channels_count == len(channels_ids):
                count_success += 1

        if count_success == count_conditions:
            builder.row(InlineKeyboardButton(text=texts.BUTTONS.contest_enter, 
                                             callback_data=f"contest_enter:{contest.contest_id}"))
        else:
            builder.row(InlineKeyboardButton(
                text=texts.BUTTONS.you_not_completed_all_conditions.format(
                    count=count_success,
                    count_conditions=count_conditions    
                ),
                callback_data="NONE"))
        builder.row(InlineKeyboardButton(
            text=texts.BUTTONS.back,
            callback_data="profile"
        ))
        return builder
    
    def choose_language(self, texts):
        builder = InlineKeyboardBuilder()
        for language in config_file.BotConfig.LANGUAGES:
            builder.row(
                InlineKeyboardButton(
                    text=language['name'],
                    callback_data=f"change_language:{language['language']}"
                )
            )
        builder.row(InlineKeyboardButton(
            text=texts.BUTTONS.back,
            callback_data="profile"
        ))
        return builder
    
    def first_time_choose_language(self):
        """Выбор языка для новых пользователей"""
        builder = InlineKeyboardBuilder()
        for language in config_file.BotConfig.LANGUAGES:
            builder.row(
                InlineKeyboardButton(
                    text=language['name'],
                    callback_data=f"first_language:{language['language']}"
                )
            )
        return builder
        return builder
    
    def legal_documents_user_menu(self, texts):
        """Меню правовых документов для пользователей"""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text=texts.BUTTONS.terms_of_service,
                callback_data="user_legal:terms"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text=texts.BUTTONS.privacy_policy, 
                callback_data="user_legal:privacy"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text=texts.BUTTONS.user_agreement,
                callback_data="user_legal:agreement"
            )
        )
        builder.row(InlineKeyboardButton(
            text=texts.BUTTONS.back,
            callback_data="back_to_user_menu"
        ))
        return builder
    
    async def sub_kb(self, texts, bot, channels):
        builder = InlineKeyboardBuilder()
        
        for channel_id in channels:
            try:
                # Используем информацию из конфига если доступна
                if channel_id in config_file.BotConfig.CHANNELS_INFO:
                    channel_info = config_file.BotConfig.CHANNELS_INFO[channel_id]
                    channel_title = channel_info['title']
                    
                    # Определяем ссылку
                    if channel_info['username']:
                        link = f"https://t.me/{channel_info['username']}"
                    elif channel_info['invite_link']:
                        link = channel_info['invite_link']
                    else:
                        link = f"https://t.me/c/{str(abs(channel_id))[4:]}"
                        
                    builder.row(InlineKeyboardButton(text=channel_title, url=link))
                    continue
                
                # Для неизвестных каналов пытаемся получить информацию через API
                try:
                    channel = await bot.get_chat(chat_id=channel_id)
                    channel_title = channel.title
                    
                    # Создаем ссылку
                    if hasattr(channel, 'username') and channel.username:
                        link = f"https://t.me/{channel.username}"
                    elif hasattr(channel, 'invite_link') and channel.invite_link:
                        link = channel.invite_link
                    else:
                        # Пытаемся создать инвайт-ссылку
                        try:
                            invite_link_obj = await bot.create_chat_invite_link(chat_id=channel_id)
                            link = invite_link_obj.invite_link
                        except:
                            link = f"https://t.me/c/{str(abs(channel_id))[4:]}"
                            
                except Exception as e:
                    print(f"Ошибка при получении информации о канале {channel_id} в клавиатуре: {e}")
                    # Используем fallback информацию
                    channel_title = f"Канал"
                    try:
                        invite_link_obj = await bot.create_chat_invite_link(chat_id=channel_id)
                        link = invite_link_obj.invite_link
                    except:
                        link = f"https://t.me/c/{str(abs(channel_id))[4:]}"
                        
                builder.row(InlineKeyboardButton(text=channel_title, url=link))
                
            except Exception as e:
                print(f"Критическая ошибка при обработке канала {channel_id}: {e}")
                # Добавляем кнопку с минимальной информацией
                fallback_link = f"https://t.me/c/{str(abs(channel_id))[4:]}"
                builder.row(InlineKeyboardButton(text="Канал", url=fallback_link))
                continue
                
        builder.row(InlineKeyboardButton(text=texts.BUTTONS.check_sub, callback_data="check_sub"))
        return builder
    
    def privacy_policy_kb(self, texts):
        """
        Клавиатура для принятия политики конфиденциальности
        """
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text=texts.BUTTONS.privacy_accept_btn,
                callback_data="privacy_accept"
            ),
            InlineKeyboardButton(
                text=texts.BUTTONS.privacy_decline_btn, 
                callback_data="privacy_decline"
            )
        )
        return builder
    
    def privacy_policy_with_navigation_kb(self, texts, current_page: int, total_pages: int):
        """Клавиатура для навигации по политике конфиденциальности"""
        builder = InlineKeyboardBuilder()
        
        # Кнопки навигации
        nav_buttons = []
        if current_page > 0:
            nav_buttons.append(InlineKeyboardButton(
                text="⬅️ Предыдущая", 
                callback_data=f"privacy_page:{current_page-1}"
            ))
        if current_page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton(
                text="➡️ Следующая", 
                callback_data=f"privacy_page:{current_page+1}"
            ))
        
        if nav_buttons:
            if len(nav_buttons) == 2:
                builder.row(nav_buttons[0], nav_buttons[1])
            else:
                builder.row(nav_buttons[0])
        
        # Кнопка принятия политики (только на последней странице)
        if current_page == total_pages - 1:
            builder.row(
                InlineKeyboardButton(
                    text=texts.BUTTONS.privacy_accept_btn,
                    callback_data="privacy_accept"
                )
            )
            builder.row(
                InlineKeyboardButton(
                    text=texts.BUTTONS.privacy_decline_btn,
                    callback_data="privacy_decline"
                )
            )
        
        return builder
    
    async def main_user_menu(self, texts):
        """Главное меню пользователя (inline версия)"""
        builder = InlineKeyboardBuilder()
        settings = await config_file.DB.get_settings()
        
        # Основные кнопки меню
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.buy, callback_data="buy"),
            InlineKeyboardButton(text=texts.BUTTONS.steam_points, callback_data="steam_points")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.profile, callback_data="profile"),
            InlineKeyboardButton(text=texts.BUTTONS.reviews, callback_data="reviews")
        )
        
        # Дополнительные кнопки
        kb_extra = [InlineKeyboardButton(text=texts.BUTTONS.support, callback_data="support")]
        if settings.faq and settings.faq != "-":
            kb_extra.insert(0, InlineKeyboardButton(text=texts.BUTTONS.faq, callback_data="faq"))
        builder.row(*kb_extra)
        
        return builder
    
    def purchases_navigation(self, texts, current_index=0, total_purchases=0, purchase_id=None):
        """Клавиатура для навигации по покупкам"""
        builder = InlineKeyboardBuilder()
        
        # Кнопки навигации
        nav_buttons = []
        
        # Предыдущая покупка
        if current_index > 0:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=f"purchase_prev:{current_index-1}"
                )
            )
        
        # Информация о текущей позиции
        nav_buttons.append(
            InlineKeyboardButton(
                text=f"{current_index + 1}/{total_purchases}",
                callback_data="noop"
            )
        )
        
        # Следующая покупка
        if current_index < total_purchases - 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=f"purchase_next:{current_index+1}"
                )
            )
        
        if nav_buttons:
            builder.row(*nav_buttons)
        
        # Кнопка "Показать файл" для товаров с файлами
        if purchase_id:
            builder.row(
                InlineKeyboardButton(
                    text="📎 Показать файл",
                    callback_data=f"show_purchase_file:{purchase_id}"
                )
            )
        
        # Кнопка поиска по чеку
        builder.row(
            InlineKeyboardButton(
                text="🔍 Поиск по чеку",
                callback_data="search_purchase_receipt"
            )
        )
        
        # Кнопка возврата
        builder.row(
            InlineKeyboardButton(
                text=texts.BUTTONS.back,
                callback_data="profile"
            )
        )
        
        return builder.as_markup()


class ReplyButtons:
    async def main_menu(self, texts, user_id, admins):
        settings = await config_file.DB.get_settings()
        ad_buttons = await config_file.DB.get_ad_buttons()
        if settings.keyboard.value == "Reply":
            kb_extra = [KeyboardButton(text=texts.BUTTONS.support)]
            if settings.faq and settings.faq != "-":
                kb_extra.insert(0, KeyboardButton(text=texts.BUTTONS.faq))
            kb = [
                [KeyboardButton(text=texts.BUTTONS.buy), KeyboardButton(text=texts.BUTTONS.steam_points)],
                [KeyboardButton(text=texts.BUTTONS.profile)],
                kb_extra,
            ]
                

            if user_id in admins:
                kb.append([KeyboardButton(text=texts.BUTTONS.admin_panel),])
            
            for button in ad_buttons:
                kb.append([KeyboardButton(text=button.name)])

            keyboard = ReplyKeyboardMarkup(
                keyboard=kb,
                resize_keyboard=True,
                input_field_placeholder=texts.BUTTONS.choose_action
            )
        else:
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text=texts.BUTTONS.buy, callback_data="buy"),
                InlineKeyboardButton(text=texts.BUTTONS.steam_points, callback_data="steam_points")
            )
            builder.row(
                InlineKeyboardButton(text=texts.BUTTONS.profile, callback_data="profile"),
                InlineKeyboardButton(text=texts.BUTTONS.reviews, callback_data="reviews")
            )
            kb_extra = [InlineKeyboardButton(text=texts.BUTTONS.support, callback_data="support")]
            if settings.faq and settings.faq != "-":
                kb_extra.insert(0, InlineKeyboardButton(text=texts.BUTTONS.faq, callback_data="faq"))
            builder.row(*kb_extra)
            
            if user_id in admins:
                builder.row(InlineKeyboardButton(text=texts.BUTTONS.admin_panel, callback_data="admin_panel"))

            for button in ad_buttons:
                builder.row(InlineKeyboardButton(text=button.name, callback_data=f"ad_button_open:{button.button_id}"))

            keyboard = builder.as_markup()

        return keyboard
    

USERS_INLINE = InlineButtons()
USERS_REPLY = ReplyButtons()
    
