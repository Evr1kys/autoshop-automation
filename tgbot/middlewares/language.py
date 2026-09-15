from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from tgbot.utils.utils import get_language
from tgbot.data.config import DB

from typing import Any, Callable, Dict, Awaitable

class UserLanguageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        data["BotTexts"] = await get_language(user.id, DB)
        return await handler(event, data)