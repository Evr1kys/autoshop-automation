from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tgbot.states.adminStates import AdminMainSettings
from tgbot.utils import payments, utils
from tgbot.data.config import BotButtons, BotConfig, DB
from tgbot.data.config import BotTexts as BTs
from tgbot.data.loader import adminRouter

from traceback import print_exc
from datetime import datetime 
from AsyncPayments.lolz import AsyncLolzteamMarketPayment
from AsyncPayments.aaio import AsyncAaio
from AsyncPayments.cryptoBot import AsyncCryptoBot
from AsyncPayments.crystalPay import AsyncCrystalPay
from AsyncPayments.cryptomus import AsyncCryptomus
from AsyncPayments.payok import AsyncPayOK

async def initPayments():
    paymentConfig = await DB.get_payments_config()
    lolz, aaio, cryptoBot, crystalPay, lava, payok, yoomoney, cryptomus = None, None, None, None, None, None, None, None
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
    except Exception:
        print("Error with init payments: ")
        print_exc()
    return lolz, aaio, cryptoBot, crystalPay, lava, payok, yoomoney, cryptomus


@adminRouter.callback_query(F.data == "payments")
async def open_payments_menu(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.select_payment, 
                                 reply_markup=(await BotButtons.ADMIN_INLINE.payments_settings(BotTexts, await DB.get_payments())).as_markup())
    

@adminRouter.callback_query(F.data.startswith("payments:"))
async def payment_info_open(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    method = call.data.split(":")[1]
    if method == "custom_pay_method":
        settings = await DB.get_settings()
        return await call.message.edit_text(BotTexts.ADMIN_TEXTS.payment_info_custom_pay_method.format(
        method=settings.custom_pay_method,
        preview_refill=BotTexts.TEXTS.create_refill_text_custom_pay_method.format(
            paymentMethod=settings.custom_pay_method,
            pay_amount=100,
            curr=BotConfig.CURRENCIES[settings.currency.value]['sign'],
            pay_id="123456789",
            under_date=datetime.fromtimestamp(utils.get_unix()).strftime("%d.%m.%Y %H:%M:%S"),
            custom_pay_method_text=settings.custom_pay_method_text,
        ),
        min=settings.custom_pay_method_min_amount,
        curr=BotConfig.CURRENCIES[settings.currency.value]['sign'],
        status=BotTexts.ADMIN_TEXTS.payments_on_off[settings.is_custom_pay_method_on]),
                                 reply_markup=BotButtons.ADMIN_INLINE.payments_settings_info(BotTexts, method, settings.is_custom_pay_method_on, settings.is_custom_pay_method_receipt_on).as_markup())
    payments = await DB.get_payments()
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.payment_info.format(
        method=BotTexts.TEXTS.payments_names[method],
        status=BotTexts.ADMIN_TEXTS.payments_on_off[payments[method]]),
                                 reply_markup=BotButtons.ADMIN_INLINE.payments_settings_info(BotTexts, method, payments[method]).as_markup())


@adminRouter.callback_query(F.data.startswith("payment_action:"))
async def payment_actions(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    try:
        _, method, action, field = call.data.split(":")
    except ValueError:
        _, method, action = call.data.split(":")
    payments = await DB.get_payments()
    settings = await DB.get_settings()
    match action:
        case "name":
            await call.message.edit_text(
                BotTexts.ADMIN_TEXTS.enter_new_name_for_custom_pay_method.format(name=settings.custom_pay_method),
                reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "payments:custom_pay_method").as_markup()
            )
            await state.set_state(AdminMainSettings.enter_new_value_custom_pay_method)
            await state.update_data(action="name")
        case "text":
            await call.message.edit_text(
                BotTexts.ADMIN_TEXTS.enter_new_text_for_custom_pay_method.format(text=settings.custom_pay_method_text),
                reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "payments:custom_pay_method").as_markup()
            )
            await state.set_state(AdminMainSettings.enter_new_value_custom_pay_method)
            await state.update_data(action="text")
        case "min":
            await call.message.edit_text(
                BotTexts.ADMIN_TEXTS.enter_new_min_for_custom_pay_method.format(min=settings.custom_pay_method_min_amount, 
                                                                                curr=BotConfig.CURRENCIES[settings.currency.value]['sign']),
                reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "payments:custom_pay_method").as_markup()
            )
            await state.set_state(AdminMainSettings.enter_new_value_custom_pay_method)
            await state.update_data(action="min")
        case "receipt":
            new_status = False if settings.is_custom_pay_method_receipt_on else True
            await DB.update_settings(is_custom_pay_method_receipt_on=new_status)
            return await call.message.edit_text(BotTexts.ADMIN_TEXTS.payment_info_custom_pay_method.format(
                method=settings.custom_pay_method,
                preview_refill=BotTexts.TEXTS.create_refill_text_custom_pay_method.format(
                    paymentMethod=settings.custom_pay_method,
                    pay_amount=100,
                    curr=BotConfig.CURRENCIES[settings.currency.value]['sign'],
                    pay_id="123456789",
                    under_date=datetime.fromtimestamp(utils.get_unix()).strftime("%d.%m.%Y %H:%M:%S"),
                    custom_pay_method_text=settings.custom_pay_method_text,
                ),
                min=settings.custom_pay_method_min_amount,
                curr=BotConfig.CURRENCIES[settings.currency.value]['sign'],
                status=BotTexts.ADMIN_TEXTS.payments_on_off[settings.is_custom_pay_method_on]),
                                                reply_markup=BotButtons.ADMIN_INLINE.payments_settings_info(BotTexts, method, settings.is_custom_pay_method_on, new_status).as_markup())
        case "enable_or_disable":
            if method == "custom_pay_method":
                new_status = False if settings.is_custom_pay_method_on else True
                await DB.update_settings(is_custom_pay_method_on=new_status)
                return await call.message.edit_text(BotTexts.ADMIN_TEXTS.payment_info_custom_pay_method.format(
                    method=settings.custom_pay_method,
                    preview_refill=BotTexts.TEXTS.create_refill_text_custom_pay_method.format(
                        paymentMethod=settings.custom_pay_method,
                        pay_amount=100,
                        curr=BotConfig.CURRENCIES[settings.currency.value]['sign'],
                        pay_id="123456789",
                        under_date=datetime.fromtimestamp(utils.get_unix()).strftime("%d.%m.%Y %H:%M:%S"),
                        custom_pay_method_text=settings.custom_pay_method_text,
                    ),
                    min=settings.custom_pay_method_min_amount,
                    curr=BotConfig.CURRENCIES[settings.currency.value]['sign'],
                    status=BotTexts.ADMIN_TEXTS.payments_on_off[new_status]),
                            reply_markup=BotButtons.ADMIN_INLINE.payments_settings_info(BotTexts, method, new_status, settings.is_custom_pay_method_receipt_on).as_markup())
            new_payments = payments
            new_payments[method] = False if payments[method] else True
            await DB.update_payment(**new_payments)
            await call.message.edit_text(BotTexts.ADMIN_TEXTS.payment_info.format(
                method=BotTexts.TEXTS.payments_names[method], 
                status=BotTexts.ADMIN_TEXTS.payments_on_off[new_payments[method]]),
                                         reply_markup=BotButtons.ADMIN_INLINE.payments_settings_info(BotTexts, method, new_payments[method]).as_markup())
        case "balance":
            lolz, aaio, cryptoBot, crystalPay, lava, payok, yoomoney, cryptomus = await initPayments()
            balance = ""
            try:
                match method:
                    case "lolz":
                        info = await lolz.get_me()
                        balance = f"<b><code>{info.balance}₽</code> (<code>{info.hold}₽</code>)</b>"
                    case "payok":
                        balance = await payok.get_balance()
                    case "aaio":
                        info = await aaio.get_balance()
                        balance = f"<b><code>{info.balance}₽</code> (<code>{info.hold}₽</code>)</b>"
                    case "yoomoney":
                        balance = yoomoney.get_balance()
                    case "lava":
                        info = await lava.get_balance()
                        balance = f"<b>{info['data']['balance']+info['data']['freeze_balance']}₽</code> (<code>{info['data']['freeze_balance']}₽</code></b>)"
                    case "cryptoBot":
                        info = await cryptoBot.get_balance()
                        for bal in info:
                            balance += f"<b>{bal.currency_code}: <code>{round(float(bal.available), 2)} {bal.currency_code}</code></b>\n"
                    case "crystalPay":
                        info = await crystalPay.get_balance_list()
                        for currency, bal in info.items():
                            balance += f"<b>{currency}: <code>{bal['amount']} {bal['currency']}</code></b>\n"
                    case "cryptomus":
                        info = await cryptomus.get_balance()
                        balance += "Merchant:\n"
                        for bal in info.merchant:
                            balance += f"<b>{bal.currency_code}: <code>{bal.balance} {bal.currency_code}</code></b> ({bal.balance_usd}$)"
                        balance += "User:\n"
                        for bal in info.user:
                            balance += f"<b>{bal.currency_code}: <code>{bal.balance} {bal.currency_code}</code></b> ({bal.balance_usd}$)"
            except:
                return await call.answer(BotTexts.ADMIN_TEXTS.get_balance_error)
                        
            await call.message.edit_text(BotTexts.ADMIN_TEXTS.balance_info.format(
                method=BotTexts.TEXTS.payments_names[method],
                balance=balance,
            ), reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, f"payments:{method}").as_markup())
        case "info":
            payment_config = await DB.get_config_for_payment(method)
            text = ""
            for cfg in payment_config:
                text += f"<b>{cfg.text}: <code>{cfg.value}</code></b> \n"

            refills_for_day, refills_for_week, refills_for_month, refills_for_all_time, refills_count_for_day, refills_count_for_week, refills_count_for_month, refills_count_for_all_time = await DB.get_payment_method_stats(method)
            
            await call.message.edit_text(BotTexts.ADMIN_TEXTS.payment_information_text.format(
                method=BotTexts.TEXTS.payments_names[method], 
                configs=text,
                refills_count_for_day=refills_count_for_day,
                refills_count_for_week=refills_count_for_week,
                refills_count_for_month=refills_count_for_month,
                refills_count_for_all_time=refills_count_for_all_time,
                refills_for_day=refills_for_day,
                refills_for_week=refills_for_week,
                refills_for_month=refills_for_month,
                refills_for_all_time=refills_for_all_time,
                curr=BotConfig.CURRENCIES[(await DB.get_settings()).currency.value]['sign']
                ),
                reply_markup=BotButtons.ADMIN_INLINE.payments_info(BotTexts, payment_config, method).as_markup())
        case "edit_cfg":
            await state.set_state(AdminMainSettings.enter_new_value_payment)
            await state.update_data(field=field, method=method)
            await call.message.edit_text(BotTexts.ADMIN_TEXTS.enter_new_value_for.format(field=field),
                                         reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, f"payment_action:{method}:info").as_markup())


@adminRouter.message(StateFilter(AdminMainSettings.enter_new_value_custom_pay_method))
async def enter_new_value_custom_pay_method(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    action = (await state.get_data())['action']
    if action == "min" and (not msg.text.isdigit() or not msg.text.replace(".", "").isdigit()):
        return await msg.reply(BotTexts.ADMIN_TEXTS.value_is_no_number)
    await state.clear()
    match action:
        case "name":
            await DB.update_settings(custom_pay_method=msg.text)
        case "min":
            await DB.update_settings(custom_pay_method_min_amount=float(msg.text))
        case "text":
            await DB.update_settings(custom_pay_method_text=msg.html_text)
    settings = await DB.get_settings()
    await msg.answer(BotTexts.ADMIN_TEXTS.payment_info_custom_pay_method.format(
        method=settings.custom_pay_method,
        preview_refill=BotTexts.TEXTS.create_refill_text_custom_pay_method.format(
            paymentMethod=settings.custom_pay_method,
            pay_amount=100,
            curr=BotConfig.CURRENCIES[settings.currency.value]['sign'],
            pay_id="123456789",
            under_date=datetime.fromtimestamp(utils.get_unix()).strftime("%d.%m.%Y %H:%M:%S"),
            custom_pay_method_text=settings.custom_pay_method_text,
        ),
        min=settings.custom_pay_method_min_amount,
        curr=BotConfig.CURRENCIES[settings.currency.value]['sign'],
        status=BotTexts.ADMIN_TEXTS.payments_on_off[settings.is_custom_pay_method_on]),
                     reply_markup=BotButtons.ADMIN_INLINE.payments_settings_info(BotTexts, "custom_pay_method", settings.is_custom_pay_method_on, settings.is_custom_pay_method_receipt_on).as_markup())


@adminRouter.message(StateFilter(AdminMainSettings.enter_new_value_payment))
async def enter_new_value_payment(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    data = await state.get_data()
    field, method = data['field'], data['method']
    await state.clear()
    await DB.update_payment_config(field, msg.text)
    await msg.reply(BotTexts.ADMIN_TEXTS.success)
    payment_config = await DB.get_config_for_payment(method)
    text = ""
    for cfg in payment_config:
        text += f"<b>{cfg.text}: <code>{cfg.value}</code></b> \n"

    refills_for_day, refills_for_week, refills_for_month, refills_for_all_time, refills_count_for_day, refills_count_for_week, refills_count_for_month, refills_count_for_all_time = await DB.get_payment_method_stats(method)
            
    await msg.answer(BotTexts.ADMIN_TEXTS.payment_information_text.format(
        method=BotTexts.TEXTS.payments_names[method], 
        configs=text,
        refills_count_for_day=refills_count_for_day,
        refills_count_for_week=refills_count_for_week,
        refills_count_for_month=refills_count_for_month,
        refills_count_for_all_time=refills_count_for_all_time,
        refills_for_day=refills_for_day,
        refills_for_week=refills_for_week,
        refills_for_month=refills_for_month,
        refills_for_all_time=refills_for_all_time,
        curr=BotConfig.CURRENCIES[(await DB.get_settings()).currency.value]['sign']
        ),
                    reply_markup=BotButtons.ADMIN_INLINE.payments_info(BotTexts, payment_config, method).as_markup())