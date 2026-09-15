from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, User

from tgbot.utils.utils import get_language
from tgbot.data.config import BotConfig

import time
from cachetools import TTLCache
from typing import Any, Awaitable, Callable, Dict, Union

# Антиспам
class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, default_rate: Union[int, float] = 1) -> None:
        self.default_rate = default_rate

        self.users = TTLCache(maxsize=10_000, ttl=600)

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data):
        this_user: User = data.get("event_from_user")

        if this_user.id in BotConfig.ADMINS:
            return await handler(event, data)

        if get_flag(data, "rate") is not None:
            self.default_rate = get_flag(data, "rate")

        if self.default_rate == 0:
            return await handler(event, data)

        if this_user.id not in self.users:
            self.users[this_user.id] = {
                'last_throttled': int(time.time()),
                'count_throttled': 0,
                'now_rate': self.default_rate,
            }

            return await handler(event, data)
        else:
            if int(time.time()) - self.users[this_user.id]['last_throttled'] >= self.users[this_user.id]['now_rate']:
                self.users.pop(this_user.id)

                return await handler(event, data)
            else:
                self.users[this_user.id]['last_throttled'] = int(time.time())
                BotTexts = await get_language(this_user.id, DB)

                if self.users[this_user.id]['count_throttled'] == 0:
                    self.users[this_user.id]['count_throttled'] = 1
                    self.users[this_user.id]['now_rate'] = self.default_rate + 2

                    return await handler(event, data)
                elif self.users[this_user.id]['count_throttled'] == 1:
                    self.users[this_user.id]['count_throttled'] = 2
                    self.users[this_user.id]['now_rate'] = self.default_rate + 3

                    await event.answer(BotTexts.TEXTS.please_dont_spam)
                elif self.users[this_user.id]['count_throttled'] == 2:
                    self.users[this_user.id]['count_throttled'] = 3
                    self.users[this_user.id]['now_rate'] = self.default_rate + 5

                    await event.answer(BotTexts.TEXTS.bot_will_not_respond)
