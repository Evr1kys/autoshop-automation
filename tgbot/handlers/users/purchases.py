from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile

from tgbot.data.loader import userRouter, bot
from tgbot.data.config import BotButtons, BotImages, BotConfig, DB
from tgbot.data.config import BotTexts as BTs
from tgbot.utils import utils
from tgbot.utils.utils import get_exchange, send_admins, get_language, get_unix, safe_send_photo, split_messages, get_date, safe_html_text
from tgbot.data.config import DB
from tgbot.states import userStates

import os
import asyncio


@userRouter.callback_query(F.data.startswith("open_category:"))
async def open_category(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    category_id = int(call.data.split(":")[1])
    positions = await DB.get_positions(cat_id=category_id)
    sub_categories = await DB.get_subcategories(cat_id=category_id)
    if sub_categories or positions:
        try:
            await call.message.delete()
        except Exception:
            # Игнорируем ошибки удаления сообщений
            pass
        category = await DB.get_category(cat_id=category_id)
        await call.message.answer(BotTexts.TEXTS.current_cat.format(name=category.name),
                                  reply_markup=(await BotButtons.USERS_INLINE.select_subcategories_and_positions(
                                      BotTexts, sub_categories, positions
                                  )).as_markup())
    else:
        await call.answer(BotTexts.TEXTS.no_products)
        
        
@userRouter.callback_query(F.data.startswith("open_subcategory:"))
async def open_subcategory(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    subcategory_id = int(call.data.split(":")[1])
    positions = await DB.get_positions(sub_cat_id=subcategory_id)
    if positions:
        try:
            await call.message.delete()
        except Exception:
            # Игнорируем ошибки удаления сообщений
            pass
        category = await DB.get_category(cat_id=positions[0].cat_id)
        subcategory = await DB.get_subcategory(sub_cat_id=subcategory_id)
        await call.message.answer(BotTexts.TEXTS.current_cat.format(name=f"{category.name} - {subcategory.name}"),
                                  reply_markup=(await BotButtons.USERS_INLINE.select_positions(BotTexts, positions)).as_markup())
    else:
        await call.answer(BotTexts.TEXTS.no_products)
        

@userRouter.callback_query(F.data.startswith("open_position:"))
async def open_position(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    position = await DB.get_position(pos_id=int(call.data.split(":")[1]))
    category = await DB.get_category(cat_id=position.cat_id)
    subcategory = await DB.get_subcategory(sub_cat_id=position.sub_cat_id)
    settings = await DB.get_settings()
    match settings.currency.value:
        case "rub":
            price = position.price_rub
        case "usd":
            price = position.price_usd
        case "eur":
            price = position.price_eur
    if position.is_infinity:
        items = BotTexts.BUTTONS.nolimit
    else:
        items = f"{len(await DB.get_items(pos_id=position.pos_id))} {BotTexts.BUTTONS.pcs}"
    # Формируем текст с ценой
    price_display = f"<b>{price:.2f}</b> {BotConfig.CURRENCIES[settings.currency.value]['sign']}"
    
    text = BotTexts.TEXTS.open_position_text.format(
        cat_name=f"{category.name} - {subcategory.name}" if subcategory else category.name,
        pos_name=position.name,
        price=price_display,
        cur="",  # Убираем валюту, так как она уже в price_display
        items=items,
        desc=safe_html_text(position.description) if position.description else ""
    )
    if position.photo and position.photo != "-":
        try:
            await call.message.delete()
        except Exception:
            # Игнорируем ошибки удаления сообщений
            pass
        # Используем безопасную функцию отправки фото
        await safe_send_photo(
            call, 
            position.photo, 
            text, 
            reply_markup=BotButtons.USERS_INLINE.position_buy(BotTexts, position).as_markup()
        )
    else:
        try:
            await call.message.edit_text(text=text, reply_markup=BotButtons.USERS_INLINE.position_buy(BotTexts, position).as_markup())
        except Exception:
            # Если не получилось отредактировать, отправляем новое сообщение
            await call.message.answer(text=text, reply_markup=BotButtons.USERS_INLINE.position_buy(BotTexts, position).as_markup())
        



@userRouter.callback_query(F.data.startswith("buy_position:"))
async def buy_position(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    position = await DB.get_position(pos_id=int(call.data.split(":")[1]))
    user = await DB.get_user(user_id=call.from_user.id)
    items = await DB.get_items(pos_id=position.pos_id)
    settings = await DB.get_settings()
    curr = BotConfig.CURRENCIES[settings.currency.value]['sign']
    
    match settings.currency.value:
        case "rub":
            original_price = position.price_rub
            balance = user.balance_rub
        case "usd":
            original_price = position.price_usd
            balance = user.balance_usd
        case "eur":
            original_price = position.price_eur
            balance = user.balance_eur

    # Используем обычную цену для покупки
    price = original_price

    if balance < price:
        await call.answer(BotTexts.TEXTS.no_balance_for_buying) 
        enabled_payments = await DB.get_enabled_payments()
        if settings.is_refill and enabled_payments:
            if BotImages.TOPUP_BALANCE_PHOTO:
                try:
                    from aiogram.types import FSInputFile
                    import os
                    # Проверяем, это локальный файл или file_id/URL
                    if isinstance(BotImages.TOPUP_BALANCE_PHOTO, str) and os.path.exists(BotImages.TOPUP_BALANCE_PHOTO):
                        photo = FSInputFile(BotImages.TOPUP_BALANCE_PHOTO)
                    else:
                        photo = BotImages.TOPUP_BALANCE_PHOTO
                    return await call.message.answer_photo(photo=photo, caption=BotTexts.TEXTS.choose_refill_method,
                                            reply_markup=(await BotButtons.USERS_INLINE.get_refill_kb(BotTexts, enabled_payments)).as_markup())
                except Exception as e:
                    print(f"Ошибка при отправке фото пополнения: {e}")
                    return await call.message.answer(BotTexts.TEXTS.choose_refill_method,
                                reply_markup=(await BotButtons.USERS_INLINE.get_refill_kb(BotTexts, enabled_payments)).as_markup())
            else:
                return await call.message.answer(BotTexts.TEXTS.choose_refill_method,
                            reply_markup=(await BotButtons.USERS_INLINE.get_refill_kb(BotTexts, enabled_payments)).as_markup())

    if len(items) < 1:
        return await call.answer(BotTexts.TEXTS.no_products, True)

    if price != 0:
        count = int(balance / price)
        
        if count > len(items):
            items = len(items)
        else:
            items = count
    else:
        items = len(items)
        
    try:
        await call.message.delete()
    except Exception:
        # Игнорируем ошибки удаления сообщений
        pass
    
    if items == 1:
        # Формируем текст с ценой
        price_text = f"{price:.2f}{curr}"
        
        await call.message.answer(
            f"<b>❓ Вы действительно хотите купить товар?</b>\n\n"
            f"- Товар: <code>{position.name}</code>\n"
            f"- Количество: <code>1 шт.</code>\n"
            f"- Сумма к покупке: {price_text}",
            reply_markup=BotButtons.USERS_INLINE.confirm_buy_item(position.pos_id, 1).as_markup()
        )
    else:
        await state.set_state(userStates.UserProducts.enter_count_products_for_buy)
        await state.update_data(position=position)

        # Формируем текст с ценой
        price_text = f"{price:.2f}{curr}"
        
        await call.message.answer(
            f"<b>❗ Введите количество товаров для покупки</b>\n"
            f"⚠️ От <code>1</code> до <code>{items}</code>\n\n"
            f"- Товар: <code>{position.name}</code> - {price_text}\n"
            f"- Ваш баланс: <code>{balance:.2f}{curr}</code>",
            reply_markup=BotButtons.USERS_INLINE.custom_button(BotTexts, f"open_position:{position.pos_id}").as_markup()
        )


@userRouter.message(F.text, StateFilter(userStates.UserProducts.enter_count_products_for_buy))
async def enter_count_products_for_buy(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    position = (await state.get_data())['position']
    user = await DB.get_user(user_id=msg.from_user.id)
    items = await DB.get_items(pos_id=position.pos_id)
    settings = await DB.get_settings()
    curr = BotConfig.CURRENCIES[settings.currency.value]['sign']
    
    match settings.currency.value:
        case "rub":
            original_price = position.price_rub
            balance = user.balance_rub
        case "usd":
            original_price = position.price_usd
            balance = user.balance_usd
        case "eur":
            original_price = position.price_eur
            balance = user.balance_eur

    # Используем обычную цену
    price = original_price

    if price != 0:
        count = int(balance / price)
        if count > len(items):
            count = len(items)
    else:
        count = len(items)

    # Формируем текст с ценой
    price_text = f"{price:.2f}{curr}"
    
    send_message = (f"<b>❗ Введите количество товаров для покупки</b>\n"
                   f"⚠️ От <code>1</code> до <code>{count}</code>\n\n"
                   f"- Товар: <code>{position.name}</code> - {price_text}\n"
                   f"- Ваш баланс: <code>{balance:.2f}{curr}</code>")

    if not msg.text.isdigit():
        return await msg.answer(
            f"{BotTexts.TEXTS.incorrect_data}\n" + send_message,
            reply_markup=BotButtons.USERS_INLINE.custom_button(BotTexts, f"open_position:{position.pos_id}").as_markup()
        )

    count = int(msg.text)
    amount_pay = round(price * count, 2)

    if len(items) < 1:
        await state.clear()
        return await msg.answer(BotTexts.TEXTS.data_was_edit)

    if count < 1 or count > len(items):
        return await msg.answer(
            f"{BotTexts.TEXTS.incorrect_count_items}\n" + send_message,
            reply_markup=BotButtons.USERS_INLINE.custom_button(BotTexts, f"open_position:{position.pos_id}").as_markup()
        )

    if int(balance) < amount_pay:
        return await msg.answer(
            f"{BotTexts.TEXTS.no_balance_on_account}\n" + send_message,
            reply_markup=BotButtons.USERS_INLINE.custom_button(BotTexts, f"open_position:{position.pos_id}").as_markup()
        )

    await state.clear()
    
    # Формируем текст с ценой
    total_price_text = f"{amount_pay:.2f}{curr}"
    
    await msg.answer(
        f"<b>❓ Вы действительно хотите купить товар?</b>\n\n"
        f"- Товар: <code>{position.name}</code>\n"
        f"- Количество: <code>{count} шт.</code>\n"
        f"- Сумма к покупке: {total_price_text}",
        reply_markup=BotButtons.USERS_INLINE.confirm_buy_item(position.pos_id, count).as_markup()
    )


# Подтверждение покупки товара
@userRouter.callback_query(F.data.startswith("buy_item_confirm:"))
async def user_buy_confirm(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    position = await DB.get_position(pos_id=int(call.data.split(":")[1]))
    purchase_count = int(call.data.split(":")[2])
    items = await DB.get_items(pos_id=position.pos_id)

    if purchase_count > len(items):
        return await call.message.edit_text(
            BotTexts.TEXTS.data_was_edit,
        )

    await call.message.edit_text(BotTexts.TEXTS.please_await_products)

    user = await DB.get_user(user_id=call.from_user.id)
    settings = await DB.get_settings()
    curr = BotConfig.CURRENCIES[settings.currency.value]['sign']
    
    match settings.currency.value:
        case "rub":
            price = position.price_rub
            balance = user.balance_rub
        case "usd":
            price = position.price_usd
            balance = user.balance_usd
        case "eur":
            price = position.price_eur
            balance = user.balance_eur
    
    purchase_price = round(price * purchase_count, 2)

    if balance < purchase_price:
        return await call.message.answer(BotTexts.TEXTS.no_balance_on_account)

    
    save_items, save_len = await DB.buy_items(items, purchase_count, position.is_infinity, position.item_type in ['photo', 'file'])
    save_count = len(save_items)

    if purchase_count != save_count:
        purchase_price = round(price * save_count, 2)
        purchase_count = save_count

    await DB.update_user(user.user_id,
                         balance_rub=round(user.balance_rub - round(position.price_rub * purchase_count, 2), 2),
                         balance_eur=round(user.balance_eur - round(position.price_eur * purchase_count, 2), 2),
                         balance_usd=round(user.balance_usd - round(position.price_usd * purchase_count, 2), 2))

    receipt = get_unix(True)
    purchase_data = "\n".join(save_items)
    
    # Получаем file_id из первого товара для покупки (если есть)
    first_item_file_id = None
    if items:
        first_item_file_id = items[0].file_id

    await DB.add_purchase(
        user_id=user.user_id,
        receipt=receipt,
        count=purchase_count,
        price_rub=round(position.price_rub * purchase_count, 2),
        price_usd=round(position.price_usd * purchase_count, 2),
        price_eur=round(position.price_eur * purchase_count, 2),
        pos_id=position.pos_id,
        item=purchase_data,
        file_id=first_item_file_id
    )

    try:
        await call.message.delete()
    except Exception:
        # Игнорируем ошибки удаления сообщений
        pass
    
    match position.item_type:
        case "text":
            for item in split_messages(save_items, save_count):
                send_items = "\n\n".join(item)
                if len(send_items) <= 4096:
                    await call.message.answer(send_items, parse_mode="None")
                else:
                    with open(f"{position.name}.txt", "w", encoding="utf-8") as file:
                        file.write(send_items)
                        file.close()

                    await call.message.answer_document(document=FSInputFile(f"{position.name}.txt"), 
                                                       caption=BotTexts.TEXTS.your_items)
                    os.remove(f"{position.name}.txt")
                    break
                await asyncio.sleep(0.3)
        case "photo":
            for item in save_items:
                if item.strip():  # Проверяем что строка не пустая
                    parts = item.split(":::")
                    if len(parts) >= 2:
                        data, file_id = parts[0], parts[1]
                        if file_id.strip():  # Проверяем что file_id не пустой
                            try:
                                await call.message.answer_photo(photo=file_id, caption=data, parse_mode="None")
                            except Exception as e:
                                print(f"Ошибка отправки фото: {e}")
                                await call.message.answer(f"⚠️ Не удалось отправить изображение: {data}", parse_mode="None")
                        else:
                            await call.message.answer(data, parse_mode="None")
                    else:
                        await call.message.answer(item, parse_mode="None")
                    await asyncio.sleep(0.3)
        case "file":
            for item in save_items:
                if item.strip():  # Проверяем что строка не пустая
                    parts = item.split(":::")
                    if len(parts) >= 2:
                        data, file_id = parts[0], parts[1]
                        if file_id.strip():  # Проверяем что file_id не пустой
                            try:
                                await call.message.answer_document(document=file_id, caption=data, parse_mode="None")
                            except Exception as e:
                                print(f"Ошибка отправки файла: {e}")
                                await call.message.answer(f"⚠️ Не удалось отправить файл: {data}", parse_mode="None")
                        else:
                            await call.message.answer(data, parse_mode="None")
                    else:
                        await call.message.answer(item, parse_mode="None")
                    await asyncio.sleep(0.3)
        

    await call.message.answer(
        BotTexts.TEXTS.successful_buying.format(
            receipt=receipt,
            position_name=position.name,
            purchase_count=purchase_count,
            purchase_price=purchase_price,
            curr=curr,
            date=get_date(),
        )
    )
    await send_admins(
        "new_purchase_alert", bot, DB,
            user_name=call.from_user.mention_html(),
            user_id=call.from_user.id,
            amount=purchase_price,
            curr=curr,
            pos_name=position.name,
            receipt=receipt,
            count=purchase_count
        )