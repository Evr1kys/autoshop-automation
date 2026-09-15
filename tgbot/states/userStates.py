from aiogram.fsm.state import State, StatesGroup


class UserRefills(StatesGroup):
    enter_amount = State()
    enter_receipt_for_custom_pay_method = State()


class UserPromocodes(StatesGroup):
    enter_promo = State()
    
    
class UserProducts(StatesGroup):
    enter_count_products_for_buy = State()


class SteamStates(StatesGroup):
    enter_steam_link = State()
    enter_steam_amount = State()
    confirm_purchase = State()


class ReviewStates(StatesGroup):
    enter_review_text = State()
    select_rating = State()


class UserPurchases(StatesGroup):
    enter_receipt = State()