from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from tgbot.data.config import DB, BotButtons
from tgbot.utils.utils import send_admins, get_language

from traceback import print_exc
from loguru import logger
from typing import Any, Callable, Dict, Awaitable


class ExistsUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        update: Update = data['event_update']
        user = data["event_from_user"]
        if update.message:
            logger.info(f"{user.full_name} - {update.message.text}")
        else:
            logger.info(f"{user.full_name} - {update.callback_query.data} (Callback)")
        try:
            if user is not None and not user.is_bot:
                settings = await DB.get_settings()

                db_user = await DB.get_user(user_id=user.id)

                # Если пользователя нет — не регистрируем автоматически, позволяем пройти /start
                if db_user is None:
                    # Разрешаем только команду /start и callback'ы выбора языка
                    if update.message:
                        if update.message.text and not update.message.text.startswith('/start'):
                            await update.message.answer(
                                "❌ Пожалуйста, начните с команды /start для проверки подписки, выбора языка и принятия политики конфиденциальности."
                            )
                            return
                    elif update.callback_query:
                        # Разрешаем только callback'ы выбора языка и проверки подписки
                        allowed_callbacks = ['first_language:', 'check_sub']
                        if not any(update.callback_query.data.startswith(prefix) for prefix in allowed_callbacks):
                            await update.callback_query.answer(
                                "❌ Сначала пройдите регистрацию через /start", 
                                show_alert=True
                            )
                            return
                else:
                    # Кешируем объект user
                    self.user = db_user
                    BotTexts = await get_language(user.id, DB)
                    # Проверяем бан
                    if self.user.is_ban:
                        return await event.answer(BotTexts.TEXTS.is_ban_text)

                    # Обновляем только если что-то поменялось
                    updates = {}
                    if self.user.user_name != user.full_name:
                        updates['full_name'] = user.full_name
                    # Проверяем username отдельно
                    new_username = user.username or ""
                    if new_username != self.user.user_name:
                        updates['user_name'] = new_username

                    # Если что-то поменялось — делаем update
                    if updates:
                        await DB.update_user(user.id, **updates)
                    
                    # Проверяем принятие политики конфиденциальности
                    if not self.user.privacy_accepted:
                        # Разрешаем только команду /start и callback'ы политики
                        if update.message:
                            if update.message.text and not update.message.text.startswith('/start'):
                                await update.message.answer(
                                    "❌ Для использования бота необходимо принять политику конфиденциальности. Используйте команду /start",
                                    reply_markup=BotButtons.USERS_INLINE.privacy_policy_kb(BotTexts).as_markup()
                                )
                                return
                        elif update.callback_query:
                            # Разрешаем callback'ы связанные с политикой, навигацией и проверкой подписки
                            allowed_callbacks = [
                                'privacy_accept', 
                                'privacy_decline',
                                'first_language:',  # префикс для выбора языка
                                'check_sub'  # проверка подписки
                            ]
                            # Также разрешаем навигацию по страницам политики
                            if (update.callback_query.data.startswith('privacy_page:') or 
                                any(update.callback_query.data.startswith(prefix) for prefix in allowed_callbacks) or
                                update.callback_query.data in allowed_callbacks):
                                pass  # Разрешаем
                            else:
                                await update.callback_query.answer(
                                    "❌ Сначала примите политику конфиденциальности", 
                                    show_alert=True
                                )
                                return

        except Exception:
            print_exc()
        
        return await handler(event, data)