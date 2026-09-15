from tgbot.utils import utils
from tgbot.utils import models

from sqlalchemy import select, update, delete, insert, func, funcfilter, desc

import math
import datetime

PAYMENTS_CONFIG_FIELDS = {
    "lolz": ["lolz_token", "lolz_merchant_id"],
    "crystalPay": ['crystal_cassa', 'crystal_token'],
    "cryptoBot": ['crypto_token'],
    'lava': ['lava_secret_key', "lava_project_id"],
    'payok': ['payok_api_id', 'payok_api_key', 'payok_secret', 'payok_shop_id'],
    'aaio': ['aaio_api_key', "aaio_shop_id", 'aaio_secret_key_1'],
    'yoomoney': ["yoomoney_token", "yoomoney_number"],
    'cryptomus': ["payment_api_key", "merchant_id"],
    'platega': ["platega_merchant_id", "platega_api_secret"]
}

class DataBase:
    async def get_user(self, **kwargs):
        async with models.async_session() as session:
            return (await session.execute(select(models.User).filter_by(**kwargs).params(**kwargs))).scalar_one_or_none()

    async def register_user(self, user_id, user_name, full_name):
        async with models.async_session() as session:
            await session.execute(insert(models.User).values(
                user_id=user_id,
                user_name=user_name,
                full_name=full_name,
                reg_date=utils.get_date(),
                reg_date_unix=utils.get_unix(),
            ))
            await session.commit()

    # Редактирование пользователя
    async def update_user(self, user_id, **kwargs):
        async with models.async_session() as session:
            await session.execute(update(models.User).where(models.User.user_id == user_id).values(**kwargs))
            await session.commit()

    # Удаление пользователя из БД
    async def delete_user(self, user_id):
        async with models.async_session() as session:
            await session.execute(delete(models.User).where(models.User.user_id == user_id))
            await session.commit()

    # Получение всех пользователей из БД
    async def all_users(self):
        async with models.async_session() as session:
            return (await session.execute(select(models.User))).scalars().all()

    # Очистка невалидных пользователей из БД
    async def clean_invalid_users(self):
        """Удаляет пользователей с некорректными user_id"""
        async with models.async_session() as session:
            # Удаляем пользователей с некорректными user_id
            await session.execute(delete(models.User).where(
                (models.User.user_id.is_(None)) | 
                (models.User.user_id <= 0) |
                (models.User.user_id > 999999999999999)  # Максимально возможный Telegram user_id
            ))
            await session.commit()
            return True

    # Получение только валидных пользователей для рассылки
    async def get_valid_users_for_mailing(self):
        """Возвращает только пользователей с валидными user_id"""
        async with models.async_session() as session:
            result = await session.execute(select(models.User).where(
                (models.User.user_id.is_not(None)) & 
                (models.User.user_id > 0) &
                (models.User.user_id <= 999999999999999)  # Максимально возможный Telegram user_id
            ))
            return result.scalars().all()

    ##############################################################################################
    ################################            Другое            ################################
    ##############################################################################################

    # Добавление пополнения
    async def add_refill(self, amount, way, user_id, receipt, pay_url, second_amount, currency, external_id=None):
        async with models.async_session() as session:
            await session.execute(
                insert(models.Refill).values(
                    user_id=user_id,
                    amount=amount,
                    way=way,
                    receipt=receipt,
                    date=utils.get_date(),
                    date_unix=utils.get_unix(),
                    pay_url=pay_url,
                    second_amount=second_amount,
                    currency=currency,
                    under_date=utils.get_unix() + 3600,
                    external_id=external_id
                )
            )
            await session.commit()

    # Получение пополнения
    async def get_refill(self, receipt, is_finished=False):
        async with models.async_session() as session:
            return (await session.execute(select(models.Refill).where(models.Refill.receipt == receipt).where(models.Refill.is_finish == is_finished))).scalar_one_or_none()

    # Получение всех пополнений
    async def all_refills(self):
        async with models.async_session() as session:
            return (await session.execute(select(models.Refill))).scalars().all()

    async def update_refill(self, receipt, **kwargs):
        async with models.async_session() as session:
            await session.execute(update(models.Refill).where(models.Refill.receipt == receipt).values(**kwargs))
            await session.commit()

    async def delete_refill(self, receipt):
        async with models.async_session() as session:
            await session.execute(delete(models.Refill).where(models.Refill.receipt == receipt))
            await session.commit()

    async def get_unfinished_user_refill(self, user_id):
        async with models.async_session() as session:
            return (await session.execute(select(models.Refill).where(models.Refill.user_id == user_id).where(models.Refill.is_finish == False))).scalar_one_or_none()

    async def update_rates(self, **kwargs):
        async with models.async_session() as session:
            await session.execute(update(models.Rates).values(**kwargs))
            await session.commit()


    async def get_rates(self):
        async with models.async_session() as session:
            rates = await session.get_one(models.Rates, "rates")

        return rates.usd_rub, rates.usd_eur, rates.eur_rub, rates.eur_usd, rates.rub_usd, rates.rub_eur

    async def get_settings(self):
        async with models.async_session() as session:
            return await session.get_one(models.Settings, "main")
    
    # Изменение настроек
    async def update_settings(self, **kwargs):
        async with models.async_session() as session:
            await session.execute(update(models.Settings).values(**kwargs))
            await session.commit()

    async def get_enabled_payments(self):
        async with models.async_session() as session:
            payments = await session.get_one(models.Payment, "payments")
        
        enabled_payments = []
        for payment in payments.__dict__.items():
            if payment[1] and payment[0] not in ["_sa_instance_state", "settings"]:
                enabled_payments.append(payment[0])
        return enabled_payments

    async def get_payments(self):
        async with models.async_session() as session:
            payments = await session.get_one(models.Payment, "payments")
        
        all_payments = {}
        for payment in payments.__dict__.items():
            if payment[0] not in ["_sa_instance_state", "settings"]:
                all_payments[payment[0]] = payment[1]
        return all_payments
    
    # Вкл/Выкл платежной системы
    async def update_payment(self, **kwargs):
        async with models.async_session() as session:
            await session.execute(update(models.Payment).values(**kwargs))
            await session.commit()
            
    async def update_payment_config(self, field, value):
        async with models.async_session() as session:
            await session.execute(update(models.PaymentConfig).where(models.PaymentConfig.field == field).values(value=value))
            await session.commit()

    async def get_payments_config(self) -> dict:
        async with models.async_session() as session:
            config = (await session.execute(select(models.PaymentConfig))).all()
        
        paymentsConfig = {}
        for field in config:
            field = field[0]
            for configField in PAYMENTS_CONFIG_FIELDS.values():
                for fieldName in configField:
                    if field.field == fieldName:
                        paymentsConfig[fieldName] = field.value

        return paymentsConfig
    
    async def get_config_for_payment(self, payment):
        async with models.async_session() as session:
            return (await session.execute(select(models.PaymentConfig).where(models.PaymentConfig.payment_id == payment))).scalars().all()

    # Получение промокода
    async def get_promocode(self, **kwargs):
        async with models.async_session() as session:
            return (await session.execute(select(models.Promocode).filter_by(**kwargs).params(**kwargs))).scalar_one_or_none()

    # Получение активироного промокода
    async def get_active_promocode(self, **kwargs):
        async with models.async_session() as session:
            return (await session.execute(select(models.ActivePromocode).filter_by(**kwargs).params(**kwargs))).scalar_one_or_none()

    # Активировать промокод
    async def activate_promocode(self, user_id, promocode_name):
        async with models.async_session() as session:
            await session.execute(insert(models.ActivePromocode).values(user_id=user_id, promocode_name=promocode_name))
            await session.commit()

    # Редактирование промокода
    async def update_promocode(self, promocode, **kwargs):
        async with models.async_session() as session:
            await session.execute(update(models.Promocode).where(models.Promocode.name == promocode).values(**kwargs))
            await session.commit()


    # Создание промокода
    async def create_promocode(self, promocode, uses, discount_rub, discount_usd, discount_eur):
        async with models.async_session() as session:
            await session.execute(insert(models.Promocode).values(
                name=promocode,
                uses=uses,
                discount_rub=discount_rub,
                discount_usd=discount_usd,
                discount_eur=discount_eur,
            ))
            await session.commit()


    # Удаление промокода
    async def delete_promocode(self, promocode):
        async with models.async_session() as session:
            await session.execute(delete(models.Promocode).where(models.Promocode.name == promocode))
            await session.execute(delete(models.ActivePromocode).where(models.ActivePromocode.promocode_name == promocode))
            await session.commit()

    async def add_ad_button(self, name, content, photo, links):
        async with models.async_session() as session:
            await session.execute(insert(models.AdButton).values(
                name=name,
                text=content,
                photo=photo,
                links=links,
            ))
            await session.commit()

    async def delete_ad_button(self, name):
        async with models.async_session() as session:
            await session.execute(delete(models.AdButton).where(models.AdButton.name == name))
            await session.commit()

    async def get_ad_buttons(self):
        async with models.async_session() as session:
            return (await session.execute(select(models.AdButton))).scalars().all()
        
    async def get_ad_button(self, **kwargs):
        async with models.async_session() as session:
            return (await session.execute(select(models.AdButton).filter_by(**kwargs).params(**kwargs))).scalar_one_or_none()

    async def add_category(self, name):
        async with models.async_session() as session:
            await session.execute(insert(models.Category).values(name=name))
            await session.commit()

    async def get_all_categories(self):
        async with models.async_session() as session:
            return (await session.execute(select(models.Category))).scalars().all()

    async def get_category(self, **kwargs):
        async with models.async_session() as session:
            return (await session.execute(select(models.Category).filter_by(**kwargs).params(**kwargs))).scalar_one_or_none()
        
    async def update_category(self, category_id, **kwargs):
        async with models.async_session() as session:
            await session.execute(update(models.Category).where(models.Category.cat_id == category_id).values(**kwargs))
            await session.commit()

    async def delete_category(self, category_id):
        async with models.async_session() as session:
            await session.execute(delete(models.Category).where(models.Category.cat_id == category_id))
            await session.commit()

    async def delete_all_categories(self):
        async with models.async_session() as session:
            await session.execute(delete(models.Category))
            await session.commit()

    async def add_subcategory(self, name, category_id):
        async with models.async_session() as session:
            await session.execute(insert(models.SubCategory).values(name=name, cat_id=category_id))
            await session.commit()

    async def get_all_subcategories(self):
        async with models.async_session() as session:
            return (await session.execute(select(models.SubCategory))).scalars().all()

    async def get_subcategory(self, **kwargs):
        async with models.async_session() as session:
            return (await session.execute(select(models.SubCategory).filter_by(**kwargs).params(**kwargs))).scalar_one_or_none()
        
    async def get_subcategories(self, **kwargs):
        async with models.async_session() as session:
            return (await session.execute(select(models.SubCategory).filter_by(**kwargs).params(**kwargs))).scalars().all()
        
    async def update_subcategory(self, subcategory_id, **kwargs):
        async with models.async_session() as session:
            await session.execute(update(models.SubCategory).where(models.SubCategory.sub_cat_id == subcategory_id).values(**kwargs))
            await session.commit()

    async def delete_subcategory(self, subcategory_id):
        async with models.async_session() as session:
            await session.execute(delete(models.SubCategory).where(models.SubCategory.sub_cat_id == subcategory_id))
            await session.commit()

    async def delete_all_subcategories(self):
        async with models.async_session() as session:
            await session.execute(delete(models.SubCategory))
            await session.commit()

    async def get_all_positions(self):
        async with models.async_session() as session:
            return (await session.execute(select(models.Position))).scalars().all()

    async def get_positions(self, **kwargs):
        async with models.async_session() as session:
            return (await session.execute(select(models.Position).filter_by(**kwargs).params(**kwargs))).scalars().all()
        
    async def get_position(self, **kwargs):
        async with models.async_session() as session:
            return (await session.execute(select(models.Position).filter_by(**kwargs).params(**kwargs))).scalar_one_or_none()
        
    async def update_position(self, position_id, **kwargs):
        async with models.async_session() as session:
            await session.execute(update(models.Position).where(models.Position.pos_id == position_id).values(**kwargs))
            await session.commit()

    async def delete_position(self, position_id):
        async with models.async_session() as session:
            await session.execute(delete(models.Position).where(models.Position.pos_id == position_id))
            await session.execute(delete(models.Item).where(models.Item.pos_id == position_id))
            await session.commit()

    async def delete_all_positions(self):
        async with models.async_session() as session:
            await session.execute(delete(models.Position))
            await session.execute(delete(models.Item))
            await session.commit()

    async def add_position(self, name, price_rub, price_usd, price_eur, description, photo, cat_id, sub_cat_id, position_type, item_type):
        async with models.async_session() as session:
            await session.execute(insert(models.Position).values(
                name=name,
                price_rub=float(price_rub),
                price_usd=float(price_usd),
                price_eur=float(price_eur),
                description=description,
                photo=photo,
                cat_id=int(cat_id),
                sub_cat_id=int(sub_cat_id) if sub_cat_id else None,
                is_infinity=position_type,
                item_type=item_type,
            ))
            await session.commit()

    async def get_items(self, **kwargs):
        async with models.async_session() as session:
            return (await session.execute(select(models.Item).filter_by(**kwargs).params(**kwargs))).scalars().all()
        
    async def delete_position_items(self, position_id):
        async with models.async_session() as session:
            await session.execute(delete(models.Item).where(models.Item.pos_id == position_id))
            await session.commit()

    async def add_items(self, category_id, position_id, items, file_id, is_file=False, is_text_infinity=False):
        async with models.async_session() as session:
            if is_file:
                await session.execute(insert(models.Item).values(
                    pos_id=position_id,
                    cat_id=category_id,
                    date=utils.get_date(),
                    data=items,
                    file_id=file_id
                ))
            else:
                if is_text_infinity:
                    await session.execute(insert(models.Item).values(
                        data=items,
                        pos_id=position_id,
                        cat_id=category_id,
                        date=utils.get_date()
                    ))
                else:
                    for item_data in items:
                        if not item_data.isspace() and item_data != "":
                            await session.execute(insert(models.Item).values(
                                data=item_data.strip(),
                                pos_id=position_id,
                                cat_id=category_id,
                                date=utils.get_date()
                            ))
            await session.commit()

    async def delete_all_items(self):
        async with models.async_session() as session:
            await session.execute(delete(models.Item))
            await session.commit()

    async def delete_item(self, item_id):
        async with models.async_session() as session:
            await session.execute(delete(models.Item).where(models.Item.item_id == item_id))
            await session.commit()

    async def add_mail_button(self, name, button_type):
        async with models.async_session() as session:
            await session.execute(insert(models.MailButton).values(name=name, button_type=button_type))
            await session.commit()

    async def get_mail_buttons(self):
        async with models.async_session() as session:
            return (await session.execute(select(models.MailButton))).scalars().all()
        
    async def get_mail_button(self, button_id):
        async with models.async_session() as session:
            return (await session.execute(select(models.MailButton).where(models.MailButton.button_id == button_id))).scalar_one_or_none()
        
    async def delete_mail_button(self, button_id):
        async with models.async_session() as session:
            await session.execute(delete(models.MailButton).where(models.MailButton.button_id == button_id))
            await session.commit()

    async def update_mail_button(self, button_id, **kwargs):
        async with models.async_session() as session:
            await session.execute(update(models.MailButton).where(models.MailButton.button_id == button_id).values(**kwargs))
            await session.commit()

    async def get_payment_method_stats(self, method):
        refills_for_day, refills_for_week, refills_for_month, refills_for_all_time = 0, 0, 0, 0
        refills_count_for_day, refills_count_for_week, refills_count_for_month, refills_count_for_all_time = 0, 0, 0, 0
        async with models.async_session() as session:
            today = datetime.datetime.today()
            month_timestamp = int(datetime.datetime(today.year, today.month, 1, 00, 00, 00).timestamp())
            settings = await self.get_settings()
            refills = (await session.execute(select(models.Refill).where(models.Refill.way == method))).scalars().all()
            
            for refill in refills:
                if refill.date_unix - settings.profit_day >= 0:
                    if settings.currency == refill.currency:
                        refills_for_day += refill.second_amount
                    else:
                        refills_for_day += await utils.get_exchange(refill.second_amount , refill.currency.value.upper(), settings.currency.value.upper(), self)
                    refills_count_for_day += 1
                
                if refill.date_unix - settings.profit_week >= 0:
                    if settings.currency == refill.currency:
                        refills_for_week += refill.second_amount
                    else:
                        refills_for_week += await utils.get_exchange(refill.second_amount , refill.currency.value.upper(), settings.currency.value.upper(), self)
                    refills_count_for_week += 1
                    
                if refill.date_unix - month_timestamp >= 0:
                    if settings.currency == refill.currency:
                        refills_for_month += refill.second_amount
                    else:
                        refills_for_month += await utils.get_exchange(refill.second_amount , refill.currency.value.upper(), settings.currency.value.upper(), self)
                    refills_count_for_month += 1
                    
                if settings.currency == refill.currency:
                    refills_for_all_time += refill.second_amount
                else:
                    refills_for_all_time += await utils.get_exchange(refill.second_amount , refill.currency.value.upper(), settings.currency.value.upper(), self)
                refills_count_for_all_time += 1
            
            
            return refills_for_day, refills_for_week, refills_for_month, refills_for_all_time, refills_count_for_day, refills_count_for_week, refills_count_for_month, refills_count_for_all_time
    
    async def get_purchases_stats_for_user(self, user_id):
        async with models.async_session() as session:
            return {
                "count_purchases": (await session.execute(select(funcfilter(func.sum(models.Purchase.count), models.Purchase.user_id == user_id)))).scalar() or 0,
                "total_purchases_rub": (await session.execute(select(funcfilter(func.sum(models.Purchase.price_rub), models.Purchase.user_id == user_id)))).scalar() or 0,
                "total_purchases_eur": (await session.execute(select(funcfilter(func.sum(models.Purchase.price_eur), models.Purchase.user_id == user_id)))).scalar() or 0,
                "total_purchases_usd": (await session.execute(select(funcfilter(func.sum(models.Purchase.price_usd), models.Purchase.user_id == user_id)))).scalar() or 0,
            }
            
    async def buy_items(self, items: list[models.Item], count: int, is_infitity: bool, is_file_or_photo: bool):
        async with models.async_session() as session:
            save_items, save_len = [], 0

            for x, select_item in enumerate(items):
                if x != count:
                    if is_file_or_photo:
                        # Безопасное извлечение file_id
                        file_id_parts = select_item.file_id.split(':')
                        file_id_suffix = file_id_parts[1] if len(file_id_parts) > 1 else select_item.file_id
                        
                        if count > 1:
                            select_data = f"{x + 1}. {select_item.data if select_item.data else ''}:::{file_id_suffix}"
                        else:
                            select_data = f"{select_item.data if select_item.data else ''}:::{file_id_suffix}"
                    else:
                        if count > 1:
                            select_data = f"{x + 1}. {select_item.data}"
                        else:
                            select_data = select_item.data

                    save_items.append(select_data)
                    if not is_infitity:
                        await session.execute(delete(models.Item).where(models.Item.item_id == select_item.item_id))

                    if len(select_data) >= save_len:
                        save_len = len(select_data)
                else:
                    break
            await session.commit()
            save_len = math.ceil(3500 / (save_len + 1))

        return save_items, save_len
    
    async def add_purchase(self, user_id, receipt, count, price_rub, price_usd, price_eur, pos_id, item, file_id=None):
        async with models.async_session() as session:
            await session.execute(insert(models.Purchase).values(
                user_id=user_id,
                receipt=str(receipt),
                count=count,
                price_rub=price_rub,
                price_usd=price_usd,
                price_eur=price_eur,
                pos_id=pos_id,
                item=item,
                date=utils.get_date(),
                unix=utils.get_unix(),
                file_id=file_id,
            ))
            await session.commit()

    async def get_purchase(self, **kwargs):
        async with models.async_session() as session:
            return (await session.execute(select(models.Purchase).filter_by(**kwargs).params(**kwargs))).scalar_one_or_none()
        
    # Последние N покупок
    async def get_last_purchases(self, user_id, count):
        async with models.async_session() as session:
            return (await session.execute(select(models.Purchase).where(models.Purchase.user_id == user_id).order_by(desc(models.Purchase.unix)).limit(count))).scalars().all()

    async def get_data_for_stats(self):
        async with models.async_session() as session:
            return ((await session.execute(select(models.Purchase))).scalars().all(),
                    (await session.execute(select(models.Refill))).scalars().all(),
                    (await session.execute(select(models.User))).scalars().all(),
                    await session.get_one(models.Settings, "main"))
    
    async def get_sum_balances(self):
        async with models.async_session() as session:
            return {
                "rub": (await session.execute(select(func.sum(models.User.balance_rub)))).scalar() or 0, 
                "usd": (await session.execute(select(func.sum(models.User.balance_eur)))).scalar() or 0, 
                "eur": (await session.execute(select(func.sum(models.User.balance_usd)))).scalar() or 0,
            }
            
    async def create_contest(self, prize, currency, members_num, end_time, winners_num, channels_ids, refills_num, purchases_num):
        async with models.async_session() as session:
            await session.execute(insert(models.Contest).values(
                prize=prize,
                currency=currency,
                members_num=members_num,
                end_time=end_time,
                winners_num=winners_num,
                channels_ids=channels_ids,
                refills_num=refills_num,
                purchases_num=purchases_num
            ))
            await session.commit()

    async def get_all_contests(self):
        async with models.async_session() as session:
            return (await session.execute(select(models.Contest))).scalars().all()

    async def get_contest(self, **kwargs):
        async with models.async_session() as session:
            return (await session.execute(select(models.Contest).filter_by(**kwargs).params(**kwargs))).scalar_one_or_none()

    async def get_contests_settings(self):
        async with models.async_session() as session:
            return await session.get_one(models.ContestsSettings, "main")
    
    # Изменение настроек
    async def update_contests_settings(self, **kwargs):
        async with models.async_session() as session:
            await session.execute(update(models.ContestsSettings).values(**kwargs))
            await session.commit()

    async def get_contest_members(self, contest_id: int):
        async with models.async_session() as session:
            return (await session.execute(select(models.ContestMember).where(models.ContestMember.contest_id == contest_id))).scalars().all()

    # ==================== СИСТЕМА СКИДОК ====================
    

    async def add_contest_member(self, user_id: int, contest_id: int):
        async with models.async_session() as session:
            await session.execute(insert(models.ContestMember).values(
                user_id=user_id,
                contest_id=contest_id
            ))
            await session.commit()
        
    async def get_contest_members_id(self, contest_id: int):
        members = await self.get_contest_members(contest_id)
        users_ids = []
        for user in members:
            users_ids.append(user.user_id)
        return users_ids

    async def delete_contest(self, contest_id):
        async with models.async_session() as session:
            await session.execute(delete(models.Contest).where(models.Contest.contest_id == contest_id))
            await session.execute(delete(models.ContestMember).where(models.ContestMember.contest_id == contest_id))
            await session.commit()

    # ========== МЕТОДЫ ДЛЯ РАБОТЫ С УВЕДОМЛЕНИЯМИ ==========
    
    async def create_product_notification(self, pos_id, title, message, file_path=None, file_id=None):
        """Создает уведомление о товаре"""
        import time
        from datetime import datetime
        
        async with models.async_session() as session:
            notification = models.ProductNotification(
                pos_id=pos_id,
                title=title,
                message=message,
                file_path=file_path,
                file_id=file_id,
                created_date=datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                created_unix=int(time.time())
            )
            session.add(notification)
            await session.commit()
            await session.refresh(notification)
            return notification.notification_id

    async def get_product_buyers(self, pos_id):
        """Получает список пользователей, которые купили данный товар"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.Purchase.user_id).distinct().where(models.Purchase.pos_id == pos_id)
            )
            return [row[0] for row in result.fetchall()]

    async def add_users_to_notification_queue(self, notification_id, user_ids):
        """Добавляет пользователей в очередь для отправки уведомления"""
        async with models.async_session() as session:
            for user_id in user_ids:
                queue_item = models.NotificationQueue(
                    notification_id=notification_id,
                    user_id=user_id
                )
                session.add(queue_item)
            await session.commit()

    async def get_pending_notifications(self, limit=50):
        """Получает неотправленные уведомления из очереди"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.NotificationQueue, models.ProductNotification)
                .join(models.ProductNotification, models.NotificationQueue.notification_id == models.ProductNotification.notification_id)
                .where(models.NotificationQueue.is_sent == False)
                .limit(limit)
            )
            return result.fetchall()

    async def mark_notification_sent(self, queue_id, error_message=None):
        """Отмечает уведомление как отправленное"""
        import time
        from datetime import datetime
        
        async with models.async_session() as session:
            result = await session.execute(
                select(models.NotificationQueue).where(models.NotificationQueue.queue_id == queue_id)
            )
            queue_item = result.scalar_one_or_none()
            
            if queue_item:
                queue_item.is_sent = True
                queue_item.sent_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                queue_item.sent_unix = int(time.time())
                if error_message:
                    queue_item.error_message = error_message
                await session.commit()

    async def update_notification_file_id(self, notification_id, file_id):
        """Обновляет file_id уведомления для быстрой отправки"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.ProductNotification).where(models.ProductNotification.notification_id == notification_id)
            )
            notification = result.scalar_one_or_none()
            
            if notification:
                notification.file_id = file_id
                await session.commit()

    async def get_notification_stats(self, notification_id):
        """Получает статистику по уведомлению"""
        async with models.async_session() as session:
            # Общее количество получателей
            total_result = await session.execute(
                select(func.count(models.NotificationQueue.queue_id))
                .where(models.NotificationQueue.notification_id == notification_id)
            )
            total_count = total_result.scalar() or 0
            
            # Количество отправленных
            sent_result = await session.execute(
                select(func.count(models.NotificationQueue.queue_id))
                .where(
                    models.NotificationQueue.notification_id == notification_id,
                    models.NotificationQueue.is_sent == True,
                    models.NotificationQueue.error_message.is_(None)
                )
            )
            sent_count = sent_result.scalar() or 0
            
            # Количество ошибок
            error_result = await session.execute(
                select(func.count(models.NotificationQueue.queue_id))
                .where(
                    models.NotificationQueue.notification_id == notification_id,
                    models.NotificationQueue.error_message.is_not(None)
                )
            )
            error_count = error_result.scalar() or 0
            
            return {
                'total': total_count,
                'sent': sent_count,
                'errors': error_count,
                'pending': total_count - sent_count
            }

    async def get_all_notifications(self):
        """Получает все уведомления с базовой статистикой"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.ProductNotification, models.Position.name.label('position_name'))
                .outerjoin(models.Position, models.ProductNotification.pos_id == models.Position.pos_id)
                .order_by(models.ProductNotification.created_unix.desc())
            )
            
            notifications = []
            for notification, position_name in result.fetchall():
                stats = await self.get_notification_stats(notification.notification_id)
                notifications.append({
                    'notification': notification,
                    'position_name': position_name or 'Неизвестно',
                    'stats': stats
                })
            
            return notifications

    async def update_product_file(self, pos_id, new_file_path, new_file_id=None):
        """Обновляет файл товара и создает его новые экземпляры"""
        async with models.async_session() as session:
            # Удаляем старые экземпляры товара
            await session.execute(delete(models.Item).where(models.Item.pos_id == pos_id))
            
            # Получаем информацию о позиции
            position_result = await session.execute(
                select(models.Position).where(models.Position.pos_id == pos_id)
            )
            position = position_result.scalar_one_or_none()
            
            if position and new_file_path:
                # Читаем новый файл и создаем экземпляры
                try:
                    with open(new_file_path, 'r', encoding='utf-8') as file:
                        lines = file.readlines()
                    
                    from datetime import datetime
                    current_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                    
                    for line in lines:
                        line = line.strip()
                        if line:  # Если строка не пустая
                            item = models.Item(
                                data=line,
                                pos_id=pos_id,
                                cat_id=position.cat_id,
                                date=current_date,
                                file_id=new_file_id
                            )
                            session.add(item)
                    
                    await session.commit()
                    return len(lines)
                    
                except Exception as e:
                    await session.rollback()
                    raise e
            
            return 0

    async def update_purchases_with_new_file(self, pos_id, new_file_id, notification_title="Обновление товара"):
        """Обновляет данные о товаре в покупках пользователей при обновлении файла"""
        async with models.async_session() as session:
            # Получаем название позиции
            position_result = await session.execute(
                select(models.Position).where(models.Position.pos_id == pos_id)
            )
            position = position_result.scalar_one_or_none()
            
            if position and new_file_id:
                # Формируем новые данные для покупок
                new_item_data = f"Файл товара '{position.name}':::{new_file_id}"
                
                # Обновляем все покупки этого товара
                await session.execute(
                    update(models.Purchase)
                    .where(models.Purchase.pos_id == pos_id)
                    .values(item=new_item_data)
                )
                
                await session.commit()
                
                # Получаем количество обновленных покупок
                result = await session.execute(
                    select(func.count(models.Purchase.receipt)).where(models.Purchase.pos_id == pos_id)
                )
                updated_count = result.scalar()
                
                return updated_count
            
            return 0

    # ===== Методы для работы с отзывами =====
    
    async def get_review_settings(self):
        """Получить настройки системы отзывов"""
        async with models.async_session() as session:
            return (await session.execute(select(models.ReviewSettings))).scalar_one_or_none()
    
    async def add_review(self, user_id, purchase_receipt, pos_id, rating, review_text=None, created_at=None, created_unix=None, is_anonymous=False):
        """Добавить отзыв"""
        async with models.async_session() as session:
            await session.execute(insert(models.ProductReview).values(
                user_id=user_id,
                purchase_receipt=purchase_receipt,
                pos_id=pos_id,
                rating=rating,
                review_text=review_text,
                created_at=created_at,
                created_unix=created_unix,
                is_anonymous=is_anonymous
            ))
            await session.commit()
            
            # Получаем ID добавленного отзыва
            result = await session.execute(
                select(models.ProductReview.review_id)
                .where(models.ProductReview.purchase_receipt == purchase_receipt)
            )
            return result.scalar()
    
    async def get_review_by_receipt(self, receipt):
        """Получить отзыв по номеру чека"""
        async with models.async_session() as session:
            return (await session.execute(
                select(models.ProductReview).where(models.ProductReview.purchase_receipt == receipt)
            )).scalar_one_or_none()
    
    async def get_reviews_for_position(self, pos_id, limit=10):
        """Получить отзывы для товара"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.ProductReview)
                .where(models.ProductReview.pos_id == pos_id)
                .order_by(desc(models.ProductReview.created_unix))
                .limit(limit)
            )
            return result.scalars().all()
    
    async def get_reviews_count_for_position(self, pos_id):
        """Получить количество отзывов для товара"""
        async with models.async_session() as session:
            result = await session.execute(
                select(func.count(models.ProductReview.review_id))
                .where(models.ProductReview.pos_id == pos_id)
            )
            return result.scalar()
    
    async def get_user_reviews(self, user_id, limit=10):
        """Получить отзывы пользователя"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.ProductReview)
                .where(models.ProductReview.user_id == user_id)
                .order_by(desc(models.ProductReview.created_unix))
                .limit(limit)
            )
            return result.scalars().all()
    
    async def get_user_reviews_count(self, user_id):
        """Получить количество отзывов пользователя"""
        async with models.async_session() as session:
            result = await session.execute(
                select(func.count(models.ProductReview.review_id))
                .where(models.ProductReview.user_id == user_id)
            )
            return result.scalar()
    
    async def add_review_bonus(self, review_id, user_id, bonus_amount, currency, reason, created_at, created_unix):
        """Добавить бонус за отзыв"""
        async with models.async_session() as session:
            await session.execute(insert(models.ReviewBonus).values(
                review_id=review_id,
                user_id=user_id,
                bonus_amount=bonus_amount,
                currency=currency,
                reason=reason,
                created_at=created_at,
                created_unix=created_unix
            ))
            await session.commit()
    
    async def get_purchase_by_receipt(self, receipt):
        """Получить покупку по номеру чека"""
        async with models.async_session() as session:
            return (await session.execute(
                select(models.Purchase).where(models.Purchase.receipt == receipt)
            )).scalar_one_or_none()
    
    # ===== Методы для работы со Steam Points =====
    
    async def get_steam_config(self):
        """Получить конфигурацию Steam API"""
        async with models.async_session() as session:
            return (await session.execute(select(models.SteamApiConfig))).scalar_one_or_none()
    
    async def add_steam_order(self, user_id, steam_url, amount, order_id, price_rub, api_response, status="pending", created_at=None, created_unix=None):
        """Добавить заказ Steam Points"""
        async with models.async_session() as session:
            await session.execute(insert(models.SteamOrder).values(
                user_id=user_id,
                steam_url=steam_url,
                amount=amount,
                order_id=order_id,
                price_rub=price_rub,
                api_response=api_response,
                status=status,
                created_at=created_at,
                created_unix=created_unix
            ))
            await session.commit()
    
    async def update_steam_order(self, order_id, **kwargs):
        """Обновить заказ Steam Points"""
        async with models.async_session() as session:
            await session.execute(
                update(models.SteamOrder)
                .where(models.SteamOrder.order_id == order_id)
                .values(**kwargs)
            )
            await session.commit()
    
    async def get_steam_order(self, order_id):
        """Получить заказ Steam Points"""
        async with models.async_session() as session:
            return (await session.execute(
                select(models.SteamOrder).where(models.SteamOrder.order_id == order_id)
            )).scalar_one_or_none()
    
    # ===== Дополнительные методы для админки =====
    
    async def get_total_reviews_count(self):
        """Получить общее количество отзывов"""
        async with models.async_session() as session:
            result = await session.execute(
                select(func.count(models.ProductReview.review_id))
            )
            return result.scalar()
    
    async def get_pending_reviews_count(self):
        """Получить количество отзывов на модерации"""
        async with models.async_session() as session:
            result = await session.execute(
                select(func.count(models.ProductReview.review_id))
                .where(models.ProductReview.is_approved == False)
            )
            return result.scalar()
    
    async def get_pending_reviews(self, limit=10):
        """Получить отзывы на модерации"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.ProductReview)
                .where(models.ProductReview.is_approved == False)
                .order_by(desc(models.ProductReview.created_unix))
                .limit(limit)
            )
            return result.scalars().all()
    
    async def update_review(self, review_id, **kwargs):
        """Обновить отзыв"""
        async with models.async_session() as session:
            await session.execute(
                update(models.ProductReview)
                .where(models.ProductReview.review_id == review_id)
                .values(**kwargs)
            )
            await session.commit()
    
    async def delete_review(self, review_id):
        """Удалить отзыв"""
        async with models.async_session() as session:
            await session.execute(
                delete(models.ProductReview)
                .where(models.ProductReview.review_id == review_id)
            )
            await session.commit()
    
    async def get_steam_orders_count(self):
        """Получить общее количество заказов Steam"""
        async with models.async_session() as session:
            result = await session.execute(
                select(func.count(models.SteamOrder.order_id))
            )
            return result.scalar()
    
    async def get_pending_steam_orders_count(self):
        """Получить количество заказов Steam в обработке"""
        async with models.async_session() as session:
            result = await session.execute(
                select(func.count(models.SteamOrder.order_id))
                .where(models.SteamOrder.status.in_(['pending', 'processing']))
            )
            return result.scalar()
    
    async def get_recent_steam_orders(self, limit=10):
        """Получить последние заказы Steam"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.SteamOrder)
                .order_by(desc(models.SteamOrder.created_unix))
                .limit(limit)
            )
            return result.scalars().all()
    
    async def update_steam_config(self, **kwargs):
        """Обновить конфигурацию Steam API"""
        async with models.async_session() as session:
            await session.execute(
                update(models.SteamApiConfig)
                .where(models.SteamApiConfig.id == 1)
                .values(**kwargs)
            )
            await session.commit()
    
    async def get_steam_api_balance(self):
        """Получить баланс Steam API через запрос к внешнему API"""
        steam_config = await self.get_steam_config()
        if not steam_config:
            return None
        
        # Проверяем, что у нас есть API ключ и URL
        if not steam_config.api_key or not steam_config.api_url:
            from tgbot.utils.error_monitoring import log_steam_api_event
            log_steam_api_event("API ключ или URL не настроены", "error")
            return steam_config.current_balance  # Возвращаем из базы как fallback
        
        try:
            import requests
            import time
            
            # Получаем баланс через API (используем POST запрос с JSON телом)
            response = requests.post(
                f"{steam_config.api_url}/api/balance",
                json={'api_key': steam_config.api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Проверяем успешность запроса
                if data.get('success'):
                    balance_rub = data.get('balance', 0)  # Баланс уже в рублях
                    
                    # Обновляем баланс в базе данных (сохраняем в рублях)
                    await self.update_steam_config(
                        current_balance=balance_rub,
                        last_balance_check=str(int(time.time()))
                    )
                    
                    # Рассчитываем количество очков для отображения
                    api_price = steam_config.api_price_per_point or 0.011
                    balance_points = balance_rub / api_price if api_price > 0 else 0
                    
                    # Логируем только в файл, не в консоль
                    from tgbot.utils.error_monitoring import log_steam_api_event
                    log_steam_api_event(f"Баланс обновлен с API: {balance_rub:.2f} ₽ ({balance_points:,.0f} очков)")
                    return balance_rub  # Возвращаем рубли
                else:
                    from tgbot.utils.error_monitoring import log_steam_api_event
                    log_steam_api_event(f"API ошибка: {data.get('error', 'Unknown error')}", "error")
                    return steam_config.current_balance  # Fallback к базе данных
            else:
                from tgbot.utils.error_monitoring import log_steam_api_event
                log_steam_api_event(f"HTTP ошибка: {response.status_code}", "error")
                return steam_config.current_balance  # Fallback к базе данных
                
        except Exception as e:
            from tgbot.utils.error_monitoring import log_steam_api_event
            log_steam_api_event(f"Ошибка получения баланса Steam API: {e}", "error")
            return steam_config.current_balance  # Fallback к базе данных
    
    async def get_steam_api_price(self):
        """Получить текущую цену за очко из API"""
        steam_config = await self.get_steam_config()
        if not steam_config:
            return None
        
        try:
            import requests
            import time
            
            # Получаем цену через API
            response = requests.get(
                f"{steam_config.api_url}/api/price",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Проверяем успешность запроса
                if data.get('success'):
                    api_price = data.get('price', 0.005)
                    
                    # Обновляем API цену в базе данных (НЕ администраторскую цену!)
                    await self.update_steam_config(
                        api_price_per_point=api_price,
                        last_price_check=str(int(time.time()))
                    )
                    
                    return api_price
                else:
                    from tgbot.utils.error_monitoring import log_steam_api_event
                    log_steam_api_event(f"API ошибка при получении цены: {data.get('error', 'Unknown error')}", "error")
                    return None
            else:
                from tgbot.utils.error_monitoring import log_steam_api_event
                log_steam_api_event(f"HTTP ошибка при получении цены: {response.status_code}", "error")
                return None
                
        except Exception as e:
            from tgbot.utils.error_monitoring import log_steam_api_event
            log_steam_api_event(f"Ошибка получения цены Steam API: {e}", "error")
            return None
    
    # ===== Методы для системы отзывов =====
    
    async def get_review_settings(self):
        """Получить настройки системы отзывов"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.ReviewSettings).where(models.ReviewSettings.id == 1)
            )
            return result.scalar_one_or_none()
    
    async def create_review_settings(self):
        """Создать настройки системы отзывов"""
        async with models.async_session() as session:
            await session.execute(insert(models.ReviewSettings).values(id=1))
            await session.commit()
    
    async def update_review_settings(self, **kwargs):
        """Обновить настройки системы отзывов"""
        async with models.async_session() as session:
            await session.execute(
                update(models.ReviewSettings)
                .where(models.ReviewSettings.id == 1)
                .values(**kwargs)
            )
            await session.commit()
    
    async def add_review(self, user_id, purchase_receipt, pos_id, rating, review_text=None, 
                        is_anonymous=False, created_at=None, created_unix=None):
        """Добавить отзыв"""
        async with models.async_session() as session:
            result = await session.execute(
                insert(models.ProductReview).values(
                    user_id=user_id,
                    purchase_receipt=purchase_receipt,
                    pos_id=pos_id,
                    rating=rating,
                    review_text=review_text,
                    is_anonymous=is_anonymous,
                    created_at=created_at or utils.get_date(),
                    created_unix=created_unix or utils.get_unix()
                )
            )
            await session.commit()
            return result.inserted_primary_key[0]
    
    async def get_reviews_for_position(self, pos_id, limit=10, offset=0):
        """Получить отзывы для товара"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.ProductReview)
                .where(
                    (models.ProductReview.pos_id == pos_id) &
                    (models.ProductReview.is_approved == True)
                )
                .order_by(desc(models.ProductReview.created_unix))
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
    
    async def get_reviews_count_for_position(self, pos_id):
        """Получить количество отзывов для товара"""
        async with models.async_session() as session:
            result = await session.execute(
                select(func.count(models.ProductReview.review_id))
                .where(
                    (models.ProductReview.pos_id == pos_id) &
                    (models.ProductReview.is_approved == True)
                )
            )
            return result.scalar()
    
    async def get_user_reviews(self, user_id, limit=10):
        """Получить отзывы пользователя"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.ProductReview)
                .where(models.ProductReview.user_id == user_id)
                .order_by(desc(models.ProductReview.created_unix))
                .limit(limit)
            )
            return result.scalars().all()
    
    async def get_review_by_receipt(self, receipt):
        """Получить отзыв по номеру покупки"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.ProductReview)
                .where(models.ProductReview.purchase_receipt == receipt)
            )
            return result.scalar_one_or_none()
    
    async def get_purchase_by_receipt(self, receipt):
        """Получить покупку по номеру чека"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.Purchase)
                .where(models.Purchase.receipt == receipt)
            )
            return result.scalar_one_or_none()
    
    # ===== Методы для Steam API =====
    
    async def get_steam_config(self):
        """Получить конфигурацию Steam API"""
        async with models.async_session() as session:
            result = await session.execute(
                select(models.SteamApiConfig).where(models.SteamApiConfig.id == 1)
            )
            return result.scalar_one_or_none()
    
    async def create_steam_config(self):
        """Создать конфигурацию Steam API"""
        async with models.async_session() as session:
            await session.execute(insert(models.SteamApiConfig).values(id=1))
            await session.commit()
    
    async def add_steam_order(self, user_id, steam_link, steam_amount, points_delivered=0,
                             price_rub=0, price_usd=0, price_eur=0, api_cost=0, profit=0,
                             status='pending', steam64=None, before_points=None, after_points=None,
                             api_response=None, receipt=None):
        """Добавить заказ Steam Points"""
        async with models.async_session() as session:
            await session.execute(
                insert(models.SteamOrder).values(
                    user_id=user_id,
                    steam_link=steam_link,
                    steam_amount=steam_amount,
                    points_delivered=points_delivered,
                    price_rub=price_rub,
                    price_usd=price_usd,
                    price_eur=price_eur,
                    api_cost=api_cost,
                    profit=profit,
                    status=status,
                    steam64=steam64,
                    before_points=before_points,
                    after_points=after_points,
                    api_response=api_response,
                    receipt=receipt or utils.get_unix(True),
                    created_at=utils.get_date(),
                    created_unix=utils.get_unix()
                )
            )
            await session.commit()
