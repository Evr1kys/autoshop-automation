from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tgbot.data.loader import bot, userRouter
from tgbot.data.config import BotButtons, BotConfig, BotImages, DB
from tgbot.data.config import BotTexts as BTs
from tgbot.utils import utils


@userRouter.message(F.text == BTs.Ru.BUTTONS.contests)
@userRouter.message(F.text == BTs.En.BUTTONS.contests)
@userRouter.message(F.text == BTs.Ua.BUTTONS.contests)
async def contests_user(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if not (await DB.get_settings()).contests_is_on:
        return await msg.answer(BotTexts.TEXTS.is_contests_text, 
                                reply_markup=BotButtons.USERS_INLINE.close(BotTexts).as_markup())
    await state.clear()
    user = await DB.get_user(user_id=msg.from_user.id)
    contests = await DB.get_all_contests()
    if len(contests) > 1:
        await msg.reply(text=BotTexts.TEXTS.choose_contest, 
                        reply_markup=BotButtons.USERS_INLINE.choose_contest(BotTexts, contests).as_markup())
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
        
        if contest.purchases_num > 0 or contest.refills_num > 0:
            text += BotTexts.TEXTS.conditions
        status_refills, status_purchases = "❌", "❌"
        
        if contest.refills_num > 0:
            if user.count_refills >= contest.refills_num:
                status_refills = "✅"
            text += BotTexts.TEXTS.conditions_refills.format(
                num=contest.refills_num,
                refills=utils.numeral_noun_declension(contest.refills_num,
                                                      BotTexts.TEXTS.refill_s),
                                                      status=status_refills
            )
        if contest.purchases_num > 0:
            purchases = (await DB.get_purchases_stats_for_user(msg.from_user.id))['count_purchases']
            if purchases >= contest.purchases_num:
                status_purchases = "✅"
            text += BotTexts.TEXTS.conditions_purchases.format(
                num=contest.purchases_num,
                purchases=utils.numeral_noun_declension(contest.purchases_num,
                                                      BotTexts.TEXTS.purchase_s),
                                                      status=status_purchases
            )
        channels_ids = utils.get_channels(contest.channels_ids)
        if len(channels_ids) > 0:
            urls_txt = ""
            for channel_id in channels_ids:
                user_status = await bot.get_chat_member(chat_id=channel_id,
                                                        user_id=msg.from_user.id)
                channel = await bot.get_chat(chat_id=channel_id)
                if user_status.status == "left":
                    urls_txt += f"<a href='{channel.invite_link}'>{channel.title}</a> - ❌\n"
                else:
                    urls_txt += f"<a href='{channel.invite_link}'>{channel.title}</a> - ✅\n"
                
            text += "\n\n" + BotTexts.TEXTS.conditions_channels.format(
                num=len(channels_ids),
                channels_text=utils.numeral_noun_declension(len(channels_ids), BotTexts.TEXTS.channel_s),
                channels=urls_txt
            )
        
        if BotImages.CONTEST_PHOTO:
            await msg.answer_photo(photo=BotImages.CONTEST_PHOTO,
                                   caption=text, 
                                   reply_markup=(await BotButtons.USERS_INLINE.contest_inl(BotTexts, contest, user)).as_markup())
        else:
            await msg.answer(text, reply_markup=(await BotButtons.USERS_INLINE.contest_inl(BotTexts, contest, user)).as_markup())
        
    else:
        await msg.reply(BotTexts.TEXTS.no_contests)


@userRouter.callback_query(F.data == "contests")
async def contests_user_callback(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await call.message.delete()
    if not (await DB.get_settings()).contests_is_on:
        return await call.message.answer(BotTexts.TEXTS.is_contests_text, 
                                reply_markup=BotButtons.USERS_INLINE.custom_button(BotTexts, "back_to_user_menu").as_markup())
    await state.clear()
    user = await DB.get_user(user_id=call.from_user.id)
    contests = await DB.get_all_contests()
    if len(contests) > 1:
        await call.message.answer(text=BotTexts.TEXTS.choose_contest, 
                        reply_markup=BotButtons.USERS_INLINE.choose_contest(BotTexts, contests).as_markup())
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
        
        if contest.purchases_num > 0 or contest.refills_num > 0:
            text += BotTexts.TEXTS.conditions
        status_refills, status_purchases = "❌", "❌"
        
        if contest.refills_num > 0:
            if user.count_refills >= contest.refills_num:
                status_refills = "✅"
            text += BotTexts.TEXTS.conditions_refills.format(
                num=contest.refills_num,
                refills=utils.numeral_noun_declension(contest.refills_num,
                                                      BotTexts.TEXTS.refill_s),
                                                      status=status_refills
            )
        if contest.purchases_num > 0:
            purchases = (await DB.get_purchases_stats_for_user(call.from_user.id))['count_purchases']
            if purchases >= contest.purchases_num:
                status_purchases = "✅"
            text += BotTexts.TEXTS.conditions_purchases.format(
                num=contest.purchases_num,
                purchases=utils.numeral_noun_declension(contest.purchases_num,
                                                      BotTexts.TEXTS.purchase_s),
                                                      status=status_purchases
            )
        channels_ids = utils.get_channels(contest.channels_ids)
        if len(channels_ids) > 0:
            urls_txt = ""
            for channel_id in channels_ids:
                user_status = await bot.get_chat_member(chat_id=channel_id,
                                                        user_id=call.from_user.id)
                channel = await bot.get_chat(chat_id=channel_id)
                if user_status.status == "left":
                    urls_txt += f"<a href='{channel.invite_link}'>{channel.title}</a> - ❌\n"
                else:
                    urls_txt += f"<a href='{channel.invite_link}'>{channel.title}</a> - ✅\n"
                
            text += "\n\n" + BotTexts.TEXTS.conditions_channels.format(
                num=len(channels_ids),
                channels_text=utils.numeral_noun_declension(len(channels_ids), BotTexts.TEXTS.channel_s),
                channels=urls_txt
            )
        
        if BotImages.CONTEST_PHOTO:
            await call.message.answer_photo(photo=BotImages.CONTEST_PHOTO,
                                   caption=text, 
                                   reply_markup=(await BotButtons.USERS_INLINE.contest_inl(BotTexts, contest, user)).as_markup())
        else:
            await call.message.answer(text, reply_markup=(await BotButtons.USERS_INLINE.contest_inl(BotTexts, contest, user)).as_markup())
        
    else:
        await call.message.answer(BotTexts.TEXTS.no_contests, reply_markup=BotButtons.USERS_INLINE.custom_button(BotTexts,
                                                                                                                 "back_to_user_menu").as_markup())


@userRouter.callback_query(F.data.startswith("contest_view:"))
@userRouter.callback_query(F.data.startswith("mail_contest_open:"))
async def contest_view(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if not (await DB.get_settings()).contests_is_on:
        return await call.message.answer(BotTexts.TEXTS.is_contests_text, 
                                         reply_markup=BotButtons.USERS_INLINE.close(BotTexts).as_markup())
    await state.clear()
    user = await DB.get_user(user_id=call.from_user.id)
    contest = await DB.get_contest(contest_id=int(call.data.split(":")[1]))
    if not contest:
        return await call.answer()
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
    
    if contest.purchases_num > 0 or contest.refills_num > 0:
        text += BotTexts.TEXTS.conditions
    status_refills, status_purchases = "❌", "❌"
    
    if contest.refills_num > 0:
        if user.count_refills >= contest.refills_num:
            status_refills = "✅"
        text += BotTexts.TEXTS.conditions_refills.format(
            num=contest.refills_num,
            refills=utils.numeral_noun_declension(contest.refills_num,
                                                    BotTexts.TEXTS.refill_s),
                                                    status=status_refills
        )
    if contest.purchases_num > 0:
        purchases = (await DB.get_purchases_stats_for_user(call.from_user.id))['count_purchases']
        if purchases >= contest.purchases_num:
            status_purchases = "✅"
        text += BotTexts.TEXTS.conditions_purchases.format(
            num=contest.purchases_num,
            purchases=utils.numeral_noun_declension(contest.purchases_num,
                                                    BotTexts.TEXTS.purchase_s),
                                                    status=status_purchases
        )
    channels_ids = utils.get_channels(contest.channels_ids)
    if len(channels_ids) > 0:
        urls_txt = ""
        for channel_id in channels_ids:
            user_status = await bot.get_chat_member(chat_id=channel_id,
                                                    user_id=call.from_user.id)
            channel = await bot.get_chat(chat_id=channel_id)
            if user_status.status == "left":
                urls_txt += f"<a href='{channel.invite_link}'>{channel.title}</a> - ❌\n"
            else:
                urls_txt += f"<a href='{channel.invite_link}'>{channel.title}</a> - ✅\n"
            
        text += "\n\n" + BotTexts.TEXTS.conditions_channels.format(
            num=len(channels_ids),
            channels_text=utils.numeral_noun_declension(len(channels_ids), BotTexts.TEXTS.channel_s),
            channels=urls_txt
        )
    await call.answer()
    if BotImages.CONTEST_PHOTO:
        if call.data.startswith("contest_view:"):
            await call.message.delete()
        await call.message.answer_photo(photo=BotImages.CONTEST_PHOTO,
                                caption=text, 
                                reply_markup=(await BotButtons.USERS_INLINE.contest_inl(BotTexts, contest, user)).as_markup())
    else:
        if call.data.startswith("contest_view:"):
            await call.message.edit_text(text, reply_markup=(await BotButtons.USERS_INLINE.contest_inl(BotTexts, contest, user)).as_markup())
        else:
            await call.message.answer(text, reply_markup=(await BotButtons.USERS_INLINE.contest_inl(BotTexts, contest, user)).as_markup())


@userRouter.callback_query(F.data.startswith("contest_enter:"))
async def contest_enter(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if not (await DB.get_settings()).contests_is_on:
        return await call.message.answer(BotTexts.TEXTS.is_contests_text, 
                                         reply_markup=BotButtons.USERS_INLINE.close(BotTexts).as_markup())
    await state.clear()
    contest_id = int(call.data.split(":")[1])
    contest_members = await DB.get_contest_members_id(contest_id)
    contest = await DB.get_contest(contest_id=contest_id)
    
    if contest:
        if len(contest_members) == contest.members_num:
            if call.from_user.id not in contest_members:
                await call.answer(BotTexts.TEXTS.u_didnt_have_time_to_enter_contest, True)
            return utils.end_contest(contest, DB, bot)
        if call.from_user.id not in contest_members:
            await DB.add_contest_member(call.from_user.id, contest_id)
            await utils.send_admins(
                "user_is_entered_contest_alert", bot, DB,
                user=call.from_user.mention_html(),
                user_id=call.from_user.id,
                prize=contest.prize,
                cur=BotConfig.CURRENCIES[contest.currency.value]['sign'],
            )
            await call.answer(BotTexts.TEXTS.success, True)
            contest_members_new = await DB.get_contest_members_id(contest_id)
            if len(contest_members_new) == contest.members_num:
                return utils.end_contest(contest, DB, bot)
        else:
            await call.answer(BotTexts.TEXTS.u_already_enter_contest, True)
    else:
        await call.answer(BotTexts.TEXTS.contest_already_ended, True)


