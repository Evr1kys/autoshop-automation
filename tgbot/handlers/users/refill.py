from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from tgbot.data.loader import bot, userRouter, adminRouter
from tgbot.data.config import BotButtons, BotConfig, BotImages , DB
from tgbot.data.config import BotTexts as BTs
from tgbot.utils import utils, payments, models
from tgbot.states.userStates import UserRefills

from AsyncPayments.lolz import AsyncLolzteamMarketPayment
from AsyncPayments.aaio import AsyncAaio
from AsyncPayments.cryptoBot import AsyncCryptoBot
from AsyncPayments.crystalPay import AsyncCrystalPay
from AsyncPayments.cryptomus import AsyncCryptomus
from AsyncPayments.cryptomus.models import InvoiceStatuses
from AsyncPayments.payok import AsyncPayOK
from traceback import print_exc
from datetime import datetime
from random import randint


async def success_refill(BotTexts, call: CallbackQuery, way, amount, p_id, user_id, pay_amount):
    try:
        if await DB.get_refill(receipt=p_id, is_finished=True):
            return await call.answer(BotTexts.TEXTS.error_refill)

        user = await DB.get_user(user_id=user_id)
        settings = await DB.get_settings()
        refill = await DB.get_refill(p_id)
        curr = refill.currency
        amount_rub, amount_euro, amount_dollar, ref_percent, ref_amount = 0, 0, 0, 0, 0
        
        # Получаем external_id для отображения в логах (например, для Platega)
        external_id_info = ""
        if refill and hasattr(refill, 'external_id') and refill.external_id:
            external_id_info = f"\n🔗 ID транзакции: <code>{refill.external_id}</code>"

        pay_amount = float(pay_amount)

        amount_rub = float(amount)
        amount_euro = await utils.get_exchange(amount_rub, 'RUB', 'EUR', DB)
        amount_dollar = await utils.get_exchange(amount_rub, 'RUB', 'USD', DB)

        if curr == models.Currencies.rub:
            pay_rub = user.balance_rub + pay_amount
            pay_usd = user.balance_usd + await utils.get_exchange(pay_amount, 'RUB', 'USD', DB)
            pay_eur = user.balance_eur + await utils.get_exchange(pay_amount, 'RUB', 'EUR', DB)
        elif curr == models.Currencies.usd:
            pay_usd = user.balance_usd + pay_amount
            pay_rub = user.balance_rub + await utils.get_exchange(pay_amount, 'USD', 'RUB', DB)
            pay_eur = user.balance_eur + await utils.get_exchange(pay_amount, 'USD', 'EUR', DB)
        elif curr == models.Currencies.eur:
            pay_eur = user.balance_eur + pay_amount
            pay_rub = user.balance_rub + await utils.get_exchange(pay_amount, 'EUR', 'RUB', DB)
            pay_usd = user.balance_usd + await utils.get_exchange(pay_amount, 'EUR', 'USD', DB)


        await utils.send_admins("refill_log", bot, DB,
            user_mention=f"<a href='tg://user?id={user_id}'>{user.full_name}</a>",
            user_id=user_id,
            pay_amount=pay_amount,
            curr=BotConfig.CURRENCIES[curr.value]['sign'],
            pay_id=p_id,
            way=BotTexts.TEXTS.payments_names[way] if way != "custom_pay_method" else settings.custom_pay_method,
            external_id_info=external_id_info

        )
        await DB.update_refill(p_id, is_finish=1)
        await DB.update_user(user_id=user_id, total_refill=int(user.total_refill) + float(amount_rub),
                             count_refills=int(user.count_refills) + 1, balance_rub=pay_rub, 
                             balance_usd=pay_usd, balance_eur=pay_eur)
    
        if way != 'custom_pay_method':
            await call.message.delete()
            await call.message.answer(BotTexts.TEXTS.success_refill_text.format(
                way=BotTexts.TEXTS.payments_names[way], 
                amount=pay_amount, 
                receipt=p_id, 
                curr=BotConfig.CURRENCIES[curr.value]['sign']))
        else:
            await bot.send_message(user_id, BotTexts.TEXTS.success_refill_text.format(
                way=settings.custom_pay_method, 
                amount=pay_amount, 
                receipt=p_id, 
                curr=BotConfig.CURRENCIES[curr.value]['sign']))

        if settings.is_ref:
            if user.ref_id is None:
                pass
            else:
                reffer_id = user.ref_id
                reffer = await DB.get_user(user_id=reffer_id)
                if reffer.ref_lvl == 1:
                    ref_percent = settings.ref_percent_1
                elif reffer.ref_lvl == 2:
                    ref_percent = settings.ref_percent_2
                else:
                    # reffer.ref_lvl == 3
                    ref_percent = settings.ref_percent_3

                ref_amount_rub = int(amount_rub) / 100 * int(ref_percent)
                ref_amount_eur = int(amount_euro) / 100 * int(ref_percent)
                ref_amount_usd = int(amount_dollar) / 100 * int(ref_percent)

                if settings.currency == models.Currencies.rub:
                    ref_amount = ref_amount_rub
                elif settings.currency == models.Currencies.eur:
                    ref_amount = ref_amount_eur
                elif settings.currency == models.Currencies.usd:
                    ref_amount = ref_amount_usd

                await DB.update_user(reffer_id, balance_rub=round(reffer.balance_rub + round(ref_amount_rub, 1), 2), 
                                     balance_eur=round(reffer.balance_eur + round(ref_amount_eur, 1), 2),
                                     balance_usd=round(reffer.balance_usd + round(ref_amount_usd, 1), 2),
                                     ref_earn_rub=reffer.ref_earn_rub + round(ref_amount_rub, 1),
                                     ref_earn_usd=reffer.ref_earn_usd + round(ref_amount_usd, 1),
                                     ref_earn_eur=reffer.ref_earn_eur + round(ref_amount_eur, 1),)

                try:
                    await bot.send_message(reffer_id, BotTexts.TEXTS.yes_refill_ref.format(
                        name=call.from_user.mention_html(), 
                        amount=amount,
                        ref_amount=round(ref_amount, 1),
                        cur=BotConfig.CURRENCIES[settings.currency.value]['sign']))
                except (TelegramBadRequest, TelegramForbiddenError):
                    # Пользователь заблокировал бота или удалил аккаунт - игнорируем ошибку
                    pass
    except:
        print_exc()


async def initPayments():
    paymentConfig = await DB.get_payments_config()
    lolz, aaio, cryptoBot, crystalPay, lava, payok, yoomoney, cryptomus, pal24, platega = None, None, None, None, None, None, None, None, None, None
    try:
        try:
            lolz = AsyncLolzteamMarketPayment(paymentConfig['lolz_token'])
        except ValueError:
            pass
        except AttributeError:
            pass
        try:
            aaio = AsyncAaio(paymentConfig['aaio_api_key'], paymentConfig['aaio_shop_id'], paymentConfig['aaio_secret_key_1'])
        except ValueError:
            pass
        try:
            cryptoBot = AsyncCryptoBot(paymentConfig['crypto_token'])
        except ValueError:
            pass
        try:
            crystalPay = AsyncCrystalPay(paymentConfig['crystal_cassa'], paymentConfig['crystal_token'], "None")
        except ValueError:
            pass
        try:
            payok = AsyncPayOK(paymentConfig['payok_api_key'], paymentConfig['payok_secret'], 
                               paymentConfig['payok_api_id'], paymentConfig['payok_shop_id'])
        except:
            pass
        try:
            cryptomus = AsyncCryptomus(paymentConfig['payment_api_key'], paymentConfig['merchant_id'], "None")
        except:
            pass
        try:
            lava = payments.Lava(paymentConfig['lava_project_id'], paymentConfig['lava_secret_key'])
        except:
            pass
        try:
            yoomoney = payments.YooMoney(paymentConfig['yoomoney_token'], paymentConfig['yoomoney_number'])
        except:
            pass
        try:
            pal24 = payments.PAL24(paymentConfig['pal24_token'], paymentConfig['pal24_shop_id'])
        except:
            pass
        try:
            platega = payments.Platega(paymentConfig['platega_merchant_id'], paymentConfig['platega_api_secret'])
        except:
            pass
    except Exception:
        print("Error with init payments: ")
        print_exc()
    return lolz, aaio, cryptoBot, crystalPay, lava, payok, yoomoney, cryptomus, pal24, platega


@userRouter.callback_query(F.data == "refill")
async def topup_balance(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    enabled_payments = await DB.get_enabled_payments()
    await call.message.delete()
    
    if (await DB.get_settings()).is_refill and enabled_payments:
        if BotImages.TOPUP_BALANCE_PHOTO:
            try:
                # Используем FSInputFile для локальных изображений и bot.send_photo после удаления сообщения
                balance_photo = FSInputFile(BotImages.TOPUP_BALANCE_PHOTO)
                await bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=balance_photo, 
                    caption=BotTexts.TEXTS.choose_refill_method,
                    reply_markup=(await BotButtons.USERS_INLINE.get_refill_kb(BotTexts, enabled_payments)).as_markup()
                )
            except Exception as e:
                # Если изображение не найдено, отправляем без фото
                await bot.send_message(
                    chat_id=call.message.chat.id,
                    text=BotTexts.TEXTS.choose_refill_method,
                    reply_markup=(await BotButtons.USERS_INLINE.get_refill_kb(BotTexts, enabled_payments)).as_markup()
                )
        else:
            await bot.send_message(
                chat_id=call.message.chat.id,
                text=BotTexts.TEXTS.choose_refill_method,
                reply_markup=(await BotButtons.USERS_INLINE.get_refill_kb(BotTexts, enabled_payments)).as_markup()
            )
    else:
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=BotTexts.TEXTS.is_refill_text, 
            reply_markup=BotButtons.USERS_INLINE.close(BotTexts).as_markup()
        )


@userRouter.callback_query(F.data.startswith("refill:"))
async def refill(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    unfinishedRefill = await DB.get_unfinished_user_refill(call.from_user.id)
    await call.message.delete()
    if unfinishedRefill:
        if utils.get_unix() <= unfinishedRefill.under_date:
            curr = unfinishedRefill.currency
            if curr == models.Currencies.usd:
                amount = await utils.get_exchange(unfinishedRefill.amount, 'RUB', 'USD', DB)
            elif curr == models.Currencies.eur:
                amount = await utils.get_exchange(unfinishedRefill.amount, 'RUB', 'EUR', DB)
            else:
                # rub
                amount = unfinishedRefill.amount

            if unfinishedRefill.way == "custom_pay_method":
                settings = await DB.get_settings()
                return await call.message.answer(
                    BotTexts.TEXTS.cancel_create_refill_text_custom_pay_method.format(
                        paymentMethod=settings.custom_pay_method,
                        pay_amount=unfinishedRefill.second_amount,
                        curr=BotConfig.CURRENCIES[curr.value]['sign'],
                        pay_id=unfinishedRefill.receipt,
                        under_date=datetime.fromtimestamp(unfinishedRefill.under_date).strftime("%d.%m.%Y %H:%M:%S"),
                        custom_pay_method_text=settings.custom_pay_method_text,
                    ),
                    reply_markup=BotButtons.USERS_INLINE.custom_pay_method_check(BotTexts, unfinishedRefill.receipt).as_markup()
                )
            else:
                return await call.message.answer(BotTexts.TEXTS.cancel_create_refill_text.format(
                    paymentMethod=BotTexts.TEXTS.payments_names[unfinishedRefill.way],
                    pay_amount=unfinishedRefill.second_amount,
                    curr=BotConfig.CURRENCIES[curr.value]['sign'],
                    pay_id=unfinishedRefill.receipt,
                    under_date=datetime.fromtimestamp(unfinishedRefill.under_date).strftime("%d.%m.%Y %H:%M:%S")
                ), reply_markup=BotButtons.USERS_INLINE.refill_inl(BotTexts, unfinishedRefill.way, amount, unfinishedRefill.pay_url,
                                                                unfinishedRefill.receipt, unfinishedRefill.second_amount).as_markup())
        else:
            await DB.delete_refill(unfinishedRefill.receipt)
    paymentMethod = call.data.split(":")[1]
    await state.set_state(UserRefills.enter_amount)
    await state.update_data(way=paymentMethod)
    await call.message.answer(BotTexts.TEXTS.enter_amount_of_refill,
                                 reply_markup=BotButtons.USERS_INLINE.custom_button(BotTexts, "refill").as_markup())


@userRouter.message(StateFilter(UserRefills.enter_amount), F.text)
async def enter_amount(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if msg.text.isdigit() or msg.text.replace(".", "").replace(",", "").isdigit():
        curr = (await DB.get_settings()).currency
        _min = BotTexts.TEXTS.min_amount
        _max = BotTexts.TEXTS.max_amount
        paymentMethod = (await state.get_data())['way']
        if paymentMethod == "custom_pay_method":
            settings = await DB.get_settings()
            _min = settings.custom_pay_method_min_amount
        if curr == models.Currencies.rub:
            min_amount = _min
            max_amount = _max
        elif curr == models.Currencies.usd:
            min_amount = await utils.get_exchange(_min, 'RUB', 'USD', DB)
            max_amount = await utils.get_exchange(_max, 'RUB', 'USD', DB)
        else:
            # eur
            min_amount = await utils.get_exchange(_min, 'RUB', 'EUR', DB)
            max_amount = await utils.get_exchange(_max, 'RUB', 'EUR', DB)

        amount = float(msg.text.replace(",", "."))
        if min_amount <= amount <= max_amount:
            await state.clear()
            bot_name, user_name = (await bot.get_me()).username, msg.from_user.full_name
            commentForApi = BotTexts.TEXTS.payment_comment_api.format(
                                user_name=user_name,
                                bot_name=bot_name,
                                curr=BotConfig.CURRENCIES[curr.value]['sign'],
                                pay_amount=amount
                            )
            success_url = f"https://t.me/{bot_name}"
            lolz, aaio, cryptoBot, crystalPay, lava, payok, yoomoney, cryptomus, pal24, platega = await initPayments()
            pay_url, pay_amount, pay_id = "", 0, ""
            external_id = None  # Для Platega transaction ID
            
            if paymentMethod not in ['crystalPay', 'aaio', 'payok', 'cryptoBot', 'cryptomus', 'lolz', 'pal24', 'platega']:
                match curr:
                    case models.Currencies.usd:
                        amount = await utils.get_exchange(amount, 'USD', 'RUB', DB)
                    case models.Currencies.eur:
                        amount = await utils.get_exchange(amount, 'EUR', 'RUB', DB)

            match paymentMethod:
                case "lolz":
                    paymentConfig = await DB.get_payments_config()
                    invoice = await lolz.create_invoice(amount, utils.get_unix(True), commentForApi, success_url, paymentConfig['lolz_merchant_id'], curr.value)
                    pay_url, pay_id, pay_amount = invoice.url, invoice.invoice_id, invoice.amount
                case "crystalPay":
                    pay = await crystalPay.create_payment(amount, amount_currency=curr.value.upper(), redirect_url=success_url)
                    pay_url, pay_id, pay_amount = pay.url, pay.id, pay.rub_amount
                case "lava":
                    invoice = await lava.create_invoice(amount=amount, 
                                                        comment=commentForApi,
                                                        success_url=success_url)
                    pay_url = invoice['data']['url']
                    pay_id = invoice['data']['id']
                case "yoomoney":
                    form = yoomoney.create_yoomoney_link(amount=amount, comment=utils.get_unix(True))
                    pay_url = form['link']
                    pay_id = form['comment']
                case "aaio":
                    pay_id = utils.get_unix(True)
                    pay_url = await aaio.create_payment_url(amount, pay_id, curr.value.upper(), 
                                                            desc=commentForApi)
                case "payok":
                    pay_id = utils.get_unix(True)
                    pay_url = await payok.create_pay(amount=amount, payment=pay_id, currency=curr.value.upper(), desc=commentForApi, success_url=success_url)
                case "cryptoBot":
                    payment = await cryptoBot.create_invoice(amount, "fiat", fiat=curr.value.upper(), description=commentForApi, paid_btn_url=success_url)
                    if payment.bot_invoice_url:
                        pay_url = payment.bot_invoice_url
                    else:
                        pay_url = payment.pay_url
                    pay_id = payment.invoice_id
                    if curr == models.Currencies.usd:
                        pay_amount = await utils.get_exchange(amount, 'USD', 'RUB', DB)
                    elif curr == models.Currencies.eur:
                        pay_amount = await utils.get_exchange(amount, 'EUR', 'RUB', DB)
                case "cryptomus":
                    # Cryptomus
                    pay_id = utils.get_unix(True)
                    payment = await cryptomus.create_payment(amount=str(amount), currency=curr.value.upper(),
                                                            order_id=str(pay_id), url_success=success_url)
                    pay_url = payment.url
                case "pal24":
                    # PAL24 СБП
                    pay_id = utils.get_unix(True)
                    bill = await pal24.create_bill(
                        amount=amount,
                        order_id=str(pay_id),
                        description=commentForApi,
                        currency=curr.value.upper(),
                        payment_method="SBP"
                    )
                    if bill.get('success') == 'true':
                        pay_url = bill['link_page_url']
                        pay_id = bill['bill_id']
                    else:
                        # Обработка ошибки
                        await msg.answer(BotTexts.TEXTS.payment_error)
                        return
                case "platega":
                    # Platega платежи (СБП) с 6% комиссией
                    import uuid
                    transaction_id = str(uuid.uuid4())
                    
                    # Создаем короткий ID для callback_data
                    short_pay_id = utils.get_unix(True)
                    
                    # Добавляем настраиваемую комиссию для СБП
                    settings = await DB.get_settings()
                    commission_rate = settings.refill_commission_percent / 100  # Получаем комиссию из настроек
                    amount_with_commission = amount * (1 + commission_rate)
                    
                    print(f"Creating Platega payment: original_amount={amount}, amount_with_commission={amount_with_commission}, currency={curr.value.upper()}, transaction_id={transaction_id}")
                    
                    if not platega:
                        await msg.answer("Ошибка: платежная система не настроена")
                        return
                    
                    try:
                        # Используем исправленный метод create_payment с SSL поддержкой
                        payment_result = await platega.create_payment(
                            amount=amount_with_commission,  # Отправляем сумму с комиссией
                            transaction_id=transaction_id,
                            description=commentForApi,
                            currency=curr.value.upper(),
                            payment_method=2,  # СБП / QR
                            return_url=success_url,
                            failed_url=success_url
                        )
                        
                        if payment_result.get('success'):
                            pay_url = payment_result['data'].get('payment_url')
                            real_transaction_id = payment_result['data'].get('transaction_id', transaction_id)
                            pay_id = short_pay_id  # Используем короткий ID для callback
                            pay_amount = amount_with_commission  # Устанавливаем сумму с комиссией
                            print(f"Payment created successfully: url={pay_url}, real_id={real_transaction_id}, callback_id={pay_id}, amount_with_commission={pay_amount}")
                        else:
                            error_msg = payment_result.get('error', 'Неизвестная ошибка')
                            print(f"Payment creation failed: {error_msg}")
                            
                            # Очищаем HTML теги из сообщения об ошибке
                            import re
                            clean_error_msg = re.sub(r'<[^>]+>', '', str(error_msg))
                            clean_error_msg = clean_error_msg.strip()
                            
                            # Если после очистки сообщение пустое, используем стандартное
                            if not clean_error_msg:
                                clean_error_msg = "Сервис временно недоступен. Попробуйте позже."
                            
                            await msg.answer(f"❌ Ошибка создания платежа: {clean_error_msg}")
                            return
                    except Exception as e:
                        print(f"Platega API Exception: {e}")
                        
                        # Очищаем HTML теги из сообщения об ошибке
                        import re
                        clean_error_msg = re.sub(r'<[^>]+>', '', str(e))
                        clean_error_msg = clean_error_msg.strip()
                        
                        # Если после очистки сообщение пустое, используем стандартное
                        if not clean_error_msg:
                            clean_error_msg = "Произошла ошибка при создании платежа"
                        
                        await msg.answer(f"❌ Ошибка создания платежа: {clean_error_msg}")
                        return
                        
                    # Сохраняем external_id для Platega  
                    if paymentMethod == "platega" and 'real_transaction_id' in locals():
                        external_id = real_transaction_id
            if pay_amount == 0:
                pay_amount = amount

            if paymentMethod == "custom_pay_method":
                pay_id = randint(11111111, 99999999)
                await msg.answer(
                    BotTexts.TEXTS.create_refill_text_custom_pay_method.format(
                        paymentMethod=settings.custom_pay_method,
                        pay_amount=amount,
                        curr=BotConfig.CURRENCIES[settings.currency.value]['sign'],
                        pay_id=pay_id,
                        under_date=datetime.fromtimestamp(utils.get_unix() + 3600).strftime("%d.%m.%Y %H:%M:%S"),
                        custom_pay_method_text=settings.custom_pay_method_text,
                    ),
                    reply_markup=BotButtons.USERS_INLINE.custom_pay_method_check(BotTexts, pay_id).as_markup()
                )
            else:
                # Специальное сообщение для Platega с комиссией
                if paymentMethod == "platega":
                    settings = await DB.get_settings()
                    commission_percent = settings.refill_commission_percent
                    commission_amount = pay_amount - amount
                    message_text = f"""💳 <b>Пополнение через СБП</b>

💰 <b>Сумма пополнения:</b> {amount:.2f} {BotConfig.CURRENCIES[curr.value]['sign']}
📈 <b>Комиссия СБП ({commission_percent}%):</b> {commission_amount:.2f} {BotConfig.CURRENCIES[curr.value]['sign']}
💎 <b>К оплате:</b> {pay_amount:.2f} {BotConfig.CURRENCIES[curr.value]['sign']}

🆔 <b>ID платежа:</b> <code>{pay_id}</code>
⏰ <b>Действителен до:</b> {datetime.fromtimestamp(utils.get_unix() + 3600).strftime("%d.%m.%Y %H:%M:%S")}

💡 <i>При оплате через СБП взимается комиссия {commission_percent}%</i>"""
                else:
                    message_text = BotTexts.TEXTS.create_refill_text.format(
                        paymentMethod=BotTexts.TEXTS.payments_names[paymentMethod],
                        pay_amount=amount,
                        curr=BotConfig.CURRENCIES[curr.value]['sign'],
                        pay_id=pay_id,
                        under_date=datetime.fromtimestamp(utils.get_unix() + 3600).strftime("%d.%m.%Y %H:%M:%S")
                    )
                
                await msg.answer(message_text, 
                    reply_markup=BotButtons.USERS_INLINE.refill_inl(BotTexts, paymentMethod, pay_amount, pay_url,
                                                                pay_id, amount).as_markup())
            await DB.add_refill(float(pay_amount), paymentMethod, msg.from_user.id, str(pay_id), pay_url, float(amount), curr, external_id)
        else:
            await msg.answer(BotTexts.TEXTS.min_max_amount.format(min_amount=min_amount,
                                                            curr=BotConfig.CURRENCIES[curr.value]['sign'],
                                                            max_amount=max_amount))
    else:
        await msg.answer(BotTexts.TEXTS.no_int_amount)


@userRouter.callback_query(F.data.startswith("check_pay:"))
async def check_pay(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    _, way, amount, pay_id, second_amount = call.data.split(":")
    lolz, aaio, cryptoBot, crystalPay, lava, payok, yoomoney, cryptomus, pal24, platega = await initPayments()
    refill = await DB.get_refill(pay_id, True)
    try:
        if way == "crystalPay":
            status = (await crystalPay.get_payment_info(pay_id)).state == "payed"
        elif way == "cryptoBot":
            status = (await cryptoBot.get_invoices(invoice_ids=pay_id, count=1))[0].status == "paid"
        elif way == "lava":
            status = await lava.status_invoice(pay_id)
        elif way == "lolz":
            status = (await lolz.get_invoice(invoice_id=pay_id)).status == "paid"
        elif way == "yoomoney":
            status = yoomoney.check_yoomoney_payment(pay_id)
        elif way == "payok":
            status = (await payok.get_transactions(int(pay_id))).transaction_status == 1
        elif way == "aaio":
            status = (await aaio.get_order_info(pay_id)).status in ["success", "hold"]
        elif way == "pal24":
            # Проверка статуса счета PAL24
            bill_status = await pal24.get_bill_status(pay_id)
            status = bill_status.get('status') == 'SUCCESS'
        elif way == "platega":
            # Проверка статуса платежа Platega
            refill_info = await DB.get_refill(pay_id)
            if refill_info and refill_info.external_id:
                payment_status = await platega.get_payment_status(str(refill_info.external_id))
                status = payment_status.get('status') == 'CONFIRMED'
            else:
                status = False
        else:
            # Cryptomus
            status = (await cryptomus.payment_info(order_id=pay_id)).status in [InvoiceStatuses.PAID, InvoiceStatuses.PAID_OVER]

        if status and not refill:
            await success_refill(BotTexts, call, way, amount, pay_id, call.from_user.id, second_amount)
        else:
            await call.answer(BotTexts.TEXTS.refill_check_no)
    except Exception as e:
        print(e)
        await call.answer(BotTexts.TEXTS.refill_check_no)
    
    
@userRouter.callback_query(F.data.startswith("check_custom_pay_method:"))
async def check_custom_pay_method(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    pay_id = call.data.split(":")[1]
    refill = await DB.get_refill(pay_id)
    await call.message.delete()
    if refill:
        settings = await DB.get_settings()
        if settings.is_custom_pay_method_receipt_on:
            await state.set_state(UserRefills.enter_receipt_for_custom_pay_method)
            await state.update_data(pay_id=pay_id)
            return await call.message.answer(BotTexts.TEXTS.send_receipt_photo)
        else:
            chat = BotConfig.LOGS_CHANNEL if BotConfig.LOGS_CHANNEL else BotConfig.ADMINS[0] 
            await bot.send_message(chat, text=BotTexts.ADMIN_TEXTS.new_refill_custom_pay_method_alert.format(
                                        username=f"<a href='tg://user?id={call.from_user.id}'>{call.from_user.full_name}</a>",
                                        user_id=call.from_user.id,
                                        amount=refill.second_amount,
                                        curr=BotConfig.CURRENCIES[refill.currency.value]['sign']
                                   ), 
                                   reply_markup=BotButtons.ADMIN_INLINE.confirm(
                                       f"check_custom_pay_method_receipt:{pay_id}:yes",
                                       f"check_custom_pay_method_receipt:{pay_id}:no",
                                   ).as_markup())
            

@userRouter.message(StateFilter(UserRefills.enter_receipt_for_custom_pay_method), F.photo)
async def enter_receipt_for_custom_pay_method(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    refill = await DB.get_refill((await state.get_data())['pay_id'])
    if refill:
        await state.update_data(photo=msg.photo[-1].file_id)
        await msg.reply(BotTexts.TEXTS.confirm_send_receipt_photo, 
                        reply_markup=BotButtons.ADMIN_INLINE.confirm(
                            f"send_receipt_to_check:yes",
                            f"send_receipt_to_check:no",
                        ).as_markup())
    
    
@userRouter.callback_query(StateFilter(UserRefills.enter_receipt_for_custom_pay_method), 
                           F.data.startswith("send_receipt_to_check:"))
async def send_receipt_to_check(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    data = await state.get_data()
    await state.clear()
    pay_id, photo = data['pay_id'], data['photo']
    _, action = call.data.split(":")
    if action == "yes":
        refill = await DB.get_refill(pay_id)
        chat = BotConfig.LOGS_CHANNEL if BotConfig.LOGS_CHANNEL else BotConfig.ADMINS[0] 
        if refill:
            await bot.send_photo(chat, photo=photo, 
                                caption=BotTexts.ADMIN_TEXTS.new_refill_custom_pay_method_alert.format(
                                    username=f"<a href='tg://user?id={call.from_user.id}'>{call.from_user.full_name}</a>",
                                    user_id=call.from_user.id,
                                    amount=refill.second_amount,
                                    curr=BotConfig.CURRENCIES[refill.currency.value]['sign']
                                    ), 
                                reply_markup=BotButtons.ADMIN_INLINE.confirm(
                                    f"check_custom_pay_method_receipt:{pay_id}:yes",
                                    f"check_custom_pay_method_receipt:{pay_id}:no",
                                ).as_markup())
        await call.message.edit_text(BotTexts.TEXTS.success)
    else:
        await call.message.delete()
        await state.set_state(UserRefills.enter_receipt_for_custom_pay_method)
        await state.update_data(pay_id=pay_id)
        await call.message.answer(BotTexts.TEXTS.send_receipt_photo)
    

@userRouter.callback_query(F.data.startswith("cancel_pay:"))
async def cancel_pay(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    pay_id = call.data.split(":")[1]
    
    # Удаляем заявку на пополнение если она есть
    if await DB.get_refill(pay_id):
        await DB.delete_refill(pay_id)
    
    # Переходим в главное меню с уведомлением об отмене
    try:
        await call.message.delete()
    except Exception:
        pass  # Если не удалось удалить, не страшно
        
    await call.message.answer(
        "❌ <b>Оплата отменена</b>\n\nВы вернулись в главное меню.",
        parse_mode='HTML'
    )
    
    # Показываем главное меню с базовыми кнопками
    await call.message.answer(
        BotTexts.TEXTS.main_menu,
        reply_markup=(await BotButtons.USERS_INLINE.main_user_menu(BotTexts)).as_markup(),
        parse_mode='HTML'
    )
    

###################################

@adminRouter.callback_query(F.data.startswith("check_custom_pay_method_receipt:"))
async def check_custom_pay_method_receipt(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    _, pay_id, action = call.data.split(":")
    refill = await DB.get_refill(pay_id)
    if refill:
        if action == "yes":
            await success_refill(BotTexts, call, "custom_pay_method", refill.amount, pay_id, refill.user_id, refill.second_amount)
            await call.message.edit_reply_markup(reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "NONE", "✅").as_markup())
        else:
            await bot.send_message(
                refill.user_id,
                BotTexts.TEXTS.refill_was_rejected.format(
                    amount=refill.second_amount,
                    curr=BotConfig.CURRENCIES[refill.currency.value]['sign']
                )
            )
            await call.message.edit_reply_markup(reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "NONE", "❌").as_markup())
            await DB.delete_refill(pay_id)
