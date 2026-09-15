from aiogram.fsm.state import State, StatesGroup


class AdminMainSettings(StatesGroup):
    # main settings
    enter_new_value = State()
    # payments
    enter_new_value_payment = State()
    enter_new_value_custom_pay_method = State()
    # contests settings
    enter_new_value_contest = State()


class AdminExtraSettings(StatesGroup):
    # promocodes
    enter_promo_name_for_create = State()
    enter_promo_uses = State()
    enter_promo_discount = State()
    enter_promo_name_for_delete = State()
    # ref levels
    enter_new_number_of_refs_for_ref_lvl = State()


class AdminExtraButtons(StatesGroup):
    # ad buttons
    enter_name_for_create_ad_button = State()
    enter_content_for_ad_button = State()
    enter_photo_for_ad_button = State()
    enter_links_buttons_for_ad_button = State()
    enter_name_for_delete_ad_button = State()
    # mail buttons
    enter_name_for_create_mail_button = State()
    select_mail_button_type = State()
    enter_link_for_create_mail_button = State()
    select_category_for_open_category_button = State()
    select_category_for_open_subcategory_button = State()
    select_subcategory_for_open_subcategory_button = State()
    select_category_for_open_position_button = State()
    select_subcategory_for_open_position_button = State()
    select_position_for_open_position_button = State()
    select_contest_for_open_contest_button = State()
    enter_new_name_for_mail_button = State()
    

class AdminProductsManage(StatesGroup):
    # categories
    enter_category_name = State()
    select_category_for_edit = State()
    enter_new_name_for_category = State()
    # subcategories
    enter_subcategory_name = State()
    select_category_for_add_sub = State()
    select_category_for_edit_sub = State()
    select_sub_for_edit = State()
    enter_new_name_for_sub = State()
    select_category_for_move_sub = State()
    # positions
    enter_position_name = State()
    enter_position_price = State()
    enter_position_item_type = State()
    enter_position_description = State()
    enter_position_photo = State()
    enter_position_type = State()
    enter_new_position_name = State()
    enter_new_position_price = State()
    enter_new_position_description = State()
    enter_new_position_photo = State()
    enter_new_position_type = State()
    select_category_for_add_position = State()
    select_subcategory_for_add_position = State()
    select_category_for_move_position = State()
    select_subcategory_for_move_position = State()
    select_category_for_edit_position = State()
    select_subcategory_for_edit_position = State()
    select_position_for_edit = State()
    # items
    enter_data_items = State()
    select_category_for_add_items = State()
    select_subcategory_for_add_items = State()
    select_position_for_add_items = State()
    enter_item_id_for_delete = State()


class AdminOther(StatesGroup):
    # mail
    enter_message_for_mail = State()


class AdminFind(StatesGroup):
    # profile
    enter_user_profile = State()
    enter_new_balance = State()
    enter_sms_for_user = State()
    # receipt
    enter_receipt = State()


class SteamSettings(StatesGroup):
    enter_price = State()
    enter_commission = State()
    enter_api_key = State()
    enter_limits = State()


class ReviewsManagement(StatesGroup):
    enter_admin_reply = State()


