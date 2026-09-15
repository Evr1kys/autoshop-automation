from aiogram.filters import Filter
from aiogram.types import Message
from tgbot.data.config import BotConfig

class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in BotConfig.ADMINS
    