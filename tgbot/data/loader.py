import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.client.default import DefaultBotProperties

from tgbot.data.config import BotConfig, DB, BotButtons
from tgbot.data.config import BotTexts as BTs
from tgbot.data.filters import IsAdmin

# Создаем роутеры для обработки входящих сообщений
userRouter, adminRouter, adButtonRouter = Router(), Router(), Router()
adminRouter.message.filter(IsAdmin())
adminRouter.callback_query.filter(IsAdmin())

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Создаем базовый объект бота
bot = Bot(token=BotConfig.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML", link_preview_is_disabled=True))
dp = Dispatcher()
scheduler = AsyncIOScheduler()


# Делаем обработчики на рекламные кнопки
@adButtonRouter.message(F.text)
async def ad_buttons_message(msg: types.Message, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    button = await DB.get_ad_button(name=msg.text)
    if button:
        if button.photo:
            return await msg.answer_photo(photo=button.photo, caption=button.text,
                                          reply_markup=BotButtons.USERS_INLINE.ad_buttons_links_buttons(BotTexts, button.links))
        else:
            return await msg.answer(text=button.text,
                             reply_markup=BotButtons.USERS_INLINE.ad_buttons_links_buttons(BotTexts, button.links))
                                 

@adButtonRouter.callback_query(F.data.startswith("ad_button_open:"))
async def ad_buttons_callback(call: types.CallbackQuery, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    button = await DB.get_ad_button(button_id=int(call.data.split(":")[1]))
    if button:
        await call.message.delete()
        if button.photo:
            return await call.message.answer_photo(photo=button.photo, caption=button.text,
                                          reply_markup=BotButtons.USERS_INLINE.ad_buttons_links_buttons(BotTexts, button.links, True))
        else:
            return call.message.answer(text=button.text,
                             reply_markup=BotButtons.USERS_INLINE.ad_buttons_links_buttons(BotTexts, button.links, True))