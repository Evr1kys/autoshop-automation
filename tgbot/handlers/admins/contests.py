from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tgbot.data.loader import adminRouter, bot
from tgbot.data.config import BotButtons, BotConfig, DB
from tgbot.data.config import BotTexts as BTs
from tgbot.states import adminStates
from tgbot.utils import utils

import time


@adminRouter.callback_query(F.data == "contests_admin")
async def contests_admin(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.contests, 
                                 reply_markup=(await BotButtons.ADMIN_INLINE.contests_inl(BotTexts)).as_markup())


@adminRouter.callback_query(F.data.startswith("edit_contest_settings:"))
async def contests_conditions(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    action = call.data.split(":")[1]

    if action == "conditions":
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.conditions, 
                                     reply_markup=(await BotButtons.ADMIN_INLINE.contests_conditions_inl(BotTexts)).as_markup())
    else:
        settings = await DB.get_contests_settings()
        if action == "channels_ids":
            await call.message.edit_text(BotTexts.ADMIN_TEXTS.enter_channels_ids.format(
                value=settings.__dict__[action]), 
                                         reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "contests_admin").as_markup())
        else:
            await call.message.edit_text(BotTexts.ADMIN_TEXTS.edit_contest_settings.format(
                action=BotTexts.ADMIN_TEXTS.contests_settings_values[action],
                value=settings.__dict__[action]
            ), reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "contests_admin").as_markup())
        await state.set_state(adminStates.AdminMainSettings.enter_new_value_contest)
        await state.update_data(action=action)
        

@adminRouter.message(StateFilter(adminStates.AdminMainSettings.enter_new_value_contest))
async def enter_new_value_contest(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    action = (await state.get_data())['action']
    if not msg.text.isdigit() and action != "channels_ids":
        await msg.reply(BotTexts.ADMIN_TEXTS.value_is_no_number, 
                        reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "contests_admin").as_markup())
    await state.clear() 
    
    if action == "channels_ids":
        value = msg.text
    else:
        value = int(msg.text)
        
    await DB.update_contests_settings(**{action: value})
    await msg.answer(BotTexts.ADMIN_TEXTS.contests, 
                                    reply_markup=(await BotButtons.ADMIN_INLINE.contests_inl(BotTexts)).as_markup())
        

@adminRouter.callback_query(F.data == "start_contest")
async def contest_create(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    settings = await DB.get_contests_settings()
    await DB.create_contest(
        settings.prize,
        (await DB.get_settings()).currency,
        settings.members_num,
        int(time.time()) + settings.end_time,
        settings.winners_num,
        settings.channels_ids,
        settings.refills_num,
        settings.purchases_num,
    )
    await call.answer(BotTexts.ADMIN_TEXTS.contest_is_start_successful)
    

@adminRouter.callback_query(F.data == "cancel_contest_now")
async def cancel_contest_now(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    contests = await DB.get_all_contests()
    
    if len(contests) > 1:
        await call.message.edit_text(text=BotTexts.TEXTS.choose_contest, 
                                     reply_markup=BotButtons.ADMIN_INLINE.choose_contest(BotTexts, contests, True).as_markup())
    elif len(contests) == 1:
        contest = contests[0]
        end_time = utils.get_time_for_end_contest(contest, BotTexts.TEXTS.day_s)
        text = BotTexts.TEXTS.contest_text.format(
            contest_id=contest.contest_id,
            prize=contest.prize,
            cur=BotConfig.CURRENCIES[contest.currency.value]['sign'],
            end_time=end_time,
            winners_num=contest.winners_num,
            winners=utils.numeral_noun_declension(contest.winners_num, BotTexts.TEXTS.winner_s),
            members_num=contest.members_num,
            members=utils.numeral_noun_declension(contest.members_num, BotTexts.TEXTS.member_s)
        )
        
        await call.message.edit_text(text=text, 
                                     reply_markup=BotButtons.ADMIN_INLINE.confirm(
                                         f"cancel_contest_confirm:{contest.contest_id}:yes",
                                         f"cancel_contest_confirm:{contest.contest_id}:no").as_markup())
    else:
        await call.answer(BotTexts.TEXTS.no_contests, True)


@adminRouter.callback_query(F.data.startswith("cancel_contest_confirm:"))
async def cancel_contest_confirm(call: CallbackQuery, state: FSMContext):
    await state.clear()
    _, contest_id, action = call.data.split(":")

    if action == "yes":
        contest = await DB.get_contest(contest_id=int(contest_id))
        if contest:
            await utils.end_contest(contest, DB, bot)
    await call.message.delete()