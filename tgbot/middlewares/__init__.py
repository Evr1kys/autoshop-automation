from aiogram import Router
from tgbot.middlewares.exists_user import ExistsUserMiddleware
from tgbot.middlewares.language import UserLanguageMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.middlewares.switchers import SwitchersMiddleware


def setup_middlewares(router: Router):
    router.message.middleware(ThrottlingMiddleware())
    router.callback_query.middleware(ThrottlingMiddleware())
    ###
    router.message.middleware(ExistsUserMiddleware())
    router.callback_query.middleware(ExistsUserMiddleware())
    ###
    router.message.middleware(UserLanguageMiddleware())
    router.callback_query.middleware(UserLanguageMiddleware())
    ###
    router.message.middleware(SwitchersMiddleware())
    router.callback_query.middleware(SwitchersMiddleware())
    