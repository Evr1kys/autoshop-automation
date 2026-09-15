from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from tgbot.data.config import DB, BotConfig, BotButtons
from tgbot.utils.utils import get_language

from typing import Any, Callable, Dict, Awaitable

class SwitchersMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        update: Update = data['event_update']
        settings = await DB.get_settings()
        BotTexts = await get_language(user.id, DB)
        
        if settings.is_work and user.id not in BotConfig.ADMINS:
            return await event.answer(BotTexts.TEXTS.is_work_text)
        
        # Проверка подписки временно отключена
        
        return await handler(event, data)