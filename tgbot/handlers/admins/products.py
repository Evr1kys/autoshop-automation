from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types.input_file import FSInputFile

from tgbot.data.loader import adminRouter
from tgbot.data.config import BotButtons, BotConfig, DB
from tgbot.data.config import BotTexts as BTs
from tgbot.utils import utils
from tgbot.states import adminStates
from tgbot.utils import models

from traceback import print_exc
import os


@adminRouter.callback_query(F.data == "products_manage")
async def products_manage(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.products_manage_text, 
                                 reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())
    

### Categories
@adminRouter.callback_query(F.data == "add_category")
async def add_category(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.add_category_text,
                                 reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
    await state.set_state(adminStates.AdminProductsManage.enter_category_name)


@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_category_name))
async def enter_category_name(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if len(msg.text) <= 64:
        await state.clear()
        await DB.add_category(msg.text)
        await utils.send_admins("category_is_created_alert", bot, DB,
            username=msg.from_user.mention_html(),
            name=msg.text,
        )
        await msg.answer(BotTexts.ADMIN_TEXTS.products_manage_text, 
                                 reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())
    else:
        await msg.reply(BotTexts.ADMIN_TEXTS.name_error)


@adminRouter.callback_query(F.data == "edit_category")
async def edit_category(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    categories = await DB.get_all_categories()
    if categories:
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.select_category, 
                                     reply_markup=BotButtons.ADMIN_INLINE.category_select_menu(BotTexts, categories).as_markup())
        await state.set_state(adminStates.AdminProductsManage.select_category_for_edit)
        
    else:
        await call.answer(BotTexts.ADMIN_TEXTS.no_categories_available)


@adminRouter.callback_query(F.data.startswith("select_category:"), StateFilter(adminStates.AdminProductsManage.select_category_for_edit))
async def select_category_for_edit(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    category = await DB.get_category(cat_id=int(call.data.split(":")[1]))
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.category_text.format(
        name=category.name,
        cat_id=category.cat_id,
    ), reply_markup=BotButtons.ADMIN_INLINE.category_edit(BotTexts, category.cat_id).as_markup())


@adminRouter.callback_query(F.data.startswith("edit_category:"))
async def edit_category_callback(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    data = call.data.split(":")
    category = await DB.get_category(cat_id=int(data[1]))
    if data[2] == "name":
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.enter_new_name_for_category.format(name=category.name),
                                 reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
        await state.set_state(adminStates.AdminProductsManage.enter_new_name_for_category)
        await state.update_data(category_id=category.cat_id, old_name=category.name)
    elif data[2] == "del":
        await call.message.delete()
        await DB.delete_category(category.cat_id)
        await utils.send_admins("category_is_deleted_alert", bot, DB,
            username=call.from_user.mention_html(),
            name=category.name,
        )
        await call.message.answer(BotTexts.ADMIN_TEXTS.products_manage_text, 
                                 reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())
    else:
        # delete
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.confirm_category_delete.format(name=category.name),
                                     reply_markup=BotButtons.ADMIN_INLINE.confirm(f"edit_category:{category.cat_id}:del", "products_manage").as_markup())



@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_new_name_for_category))
async def enter_new_name_for_category(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if len(msg.text) <= 64:
        data = await state.get_data()
        await state.clear()
        await DB.update_category(category_id=int(data['category_id']), name=msg.text)
        await utils.send_admins("category_is_edited_alert", bot, DB,
            username=msg.from_user.mention_html(),
            old_name=data['old_name'],
            new_name=msg.text,
        )
        await msg.answer(BotTexts.ADMIN_TEXTS.products_manage_text, 
                                 reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())
    else:
        await msg.reply(BotTexts.ADMIN_TEXTS.name_error)

    
@adminRouter.callback_query(F.data == "del_all_categories")
async def del_all_categories(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.del_all_categories_text,
                                 reply_markup=BotButtons.ADMIN_INLINE.confirm(
                                     f"delete_all_categories", "products_manage"
                                 ).as_markup())
    

@adminRouter.callback_query(F.data == "delete_all_categories")
async def delete_all_categories(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.delete()
    await DB.delete_all_categories()
    await utils.send_admins("all_categories_are_deleted_alert", bot, DB,
            username=call.from_user.mention_html(),
        )
    await call.message.answer(BotTexts.ADMIN_TEXTS.products_manage_text, 
                     reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())


### Subcategories
@adminRouter.callback_query(F.data == "add_subcategory")
async def add_cat_opee(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    categories = await DB.get_all_categories()
    if categories:
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.select_category, 
                                  reply_markup=BotButtons.ADMIN_INLINE.category_select_menu(BotTexts, categories).as_markup())
        await state.set_state(adminStates.AdminProductsManage.select_category_for_add_sub)
    else:
        await call.answer(BotTexts.ADMIN_TEXTS.no_categories_available)


@adminRouter.callback_query(F.data.startswith("select_category"), StateFilter(adminStates.AdminProductsManage.select_category_for_add_sub))
async def select_category_for_add_sub(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    category = await DB.get_category(cat_id=int(call.data.split(":")[1]))
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.enter_name_for_subcategory,
                                 reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
    await state.set_state(adminStates.AdminProductsManage.enter_subcategory_name)
    await state.update_data(category=category)


@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_subcategory_name))
async def enter_subcategory_name(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if len(msg.text) <= 64:
        category: models.Category = (await state.get_data())['category']
        await state.clear()
        await DB.add_subcategory(msg.text, category.cat_id)
        await utils.send_admins("subcategory_is_created_alert", bot, DB,
            username=msg.from_user.mention_html(),
            name=msg.text,
            cat_name=category.name,
        )
        await msg.answer(BotTexts.ADMIN_TEXTS.products_manage_text, 
                                 reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())
    else:
        await msg.reply(BotTexts.ADMIN_TEXTS.name_error)


@adminRouter.callback_query(F.data == "edit_subcategory")
async def edit_subcategory(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    categories = await DB.get_all_categories()
    if categories:
        if await DB.get_all_subcategories():
            await call.message.edit_text(BotTexts.ADMIN_TEXTS.select_category, 
                                  reply_markup=BotButtons.ADMIN_INLINE.category_select_menu(BotTexts, categories).as_markup())
            await state.set_state(adminStates.AdminProductsManage.select_category_for_edit_sub)
        else:
            await call.answer(BotTexts.ADMIN_TEXTS.no_subcategories_available)
    else:
        await call.answer(BotTexts.ADMIN_TEXTS.no_categories_available)


@adminRouter.callback_query(F.data.startswith("select_category:"), StateFilter(adminStates.AdminProductsManage.select_category_for_edit_sub))
async def select_category_for_edit_sub(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    subcategories = await DB.get_subcategories(cat_id=int(call.data.split(":")[1]))
    if subcategories:
        await state.clear()
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.select_subcategory,
                                     reply_markup=BotButtons.ADMIN_INLINE.subcategory_select_menu(BotTexts, subcategories).as_markup())
        await state.set_state(adminStates.AdminProductsManage.select_sub_for_edit)
        await state.update_data(category_id=int(call.data.split(":")[1]))
    else:
        await call.answer(BotTexts.ADMIN_TEXTS.no_subcategories_available_in_this_category)
    

@adminRouter.callback_query(F.data.startswith("select_subcategory:"), StateFilter(adminStates.AdminProductsManage.select_sub_for_edit))
async def select_sub_for_edit(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    category = await DB.get_category(cat_id=int((await state.get_data())['category_id']))
    await state.clear()
    subcategory = await DB.get_subcategory(sub_cat_id=int(call.data.split(":")[1]))
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.subcategory_text.format(
        name=subcategory.name,
        sub_cat_id=subcategory.sub_cat_id,
        cat_name=category.name,
        cat_id=category.cat_id,
    ), reply_markup=BotButtons.ADMIN_INLINE.category_edit(BotTexts, subcategory.sub_cat_id, True).as_markup())


@adminRouter.callback_query(F.data.startswith("edit_subcategory:"))
async def edit_subcategory(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    data = call.data.split(":")
    subcategory = await DB.get_subcategory(sub_cat_id=int(data[1]))
    if data[2] == "name":
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.enter_new_name_for_subcategory.format(name=subcategory.name),
                                 reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
        await state.set_state(adminStates.AdminProductsManage.enter_new_name_for_sub)
        await state.update_data(subcategory_id=subcategory.sub_cat_id, old_name=subcategory.name)
    elif data[2] == "del":
        await call.message.delete()
        await DB.delete_subcategory(subcategory.sub_cat_id)
        await utils.send_admins("subcategory_is_deleted_alert", bot, DB,
            username=call.from_user.mention_html(),
            name=subcategory.name,
        )
        await call.message.answer(BotTexts.ADMIN_TEXTS.products_manage_text, 
                                 reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())
    elif data[2] == "move":
        categories = await DB.get_all_categories()
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.select_category,
                                     reply_markup=BotButtons.ADMIN_INLINE.category_select_menu(BotTexts, categories).as_markup())
        await state.set_state(adminStates.AdminProductsManage.select_category_for_move_sub)
        await state.update_data(subcategory=subcategory)
    else:
        # delete
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.confirm_subcategory_delete.format(name=subcategory.name),
                                     reply_markup=BotButtons.ADMIN_INLINE.confirm(f"edit_subcategory:{subcategory.sub_cat_id}:del", "products_manage").as_markup())


@adminRouter.callback_query(F.data.startswith("select_category:"), StateFilter(adminStates.AdminProductsManage.select_category_for_move_sub))
async def select_category_for_move_sub(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    subcategory: models.SubCategory = (await state.get_data())['subcategory']
    await state.clear()
    category = await DB.get_category(cat_id=subcategory.cat_id)
    await DB.update_subcategory(subcategory_id=subcategory.sub_cat_id, cat_id=int(call.data.split(":")[1]))
    new_category = await DB.get_category(cat_id=int(call.data.split(":")[1]))
    await call.message.delete()
    await utils.send_admins("subcategory_has_been_moved_deleted_alert", bot, DB,
        username=call.from_user.mention_html(),
        sub_name=subcategory.name,
        old_cat_name=category.name,
        new_cat_name=new_category.name
    )
    await call.message.answer(BotTexts.ADMIN_TEXTS.subcategory_text.format(
        name=subcategory.name,
        sub_cat_id=subcategory.sub_cat_id,
        cat_name=new_category.name,
        cat_id=new_category.cat_id,
    ), reply_markup=BotButtons.ADMIN_INLINE.category_edit(BotTexts, subcategory.sub_cat_id, True).as_markup())



@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_new_name_for_sub))
async def enter_new_name_for_sub(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if len(msg.text) <= 64:
        data = await state.get_data()
        await state.clear()
        await DB.update_subcategory(subcategory_id=int(data['subcategory_id']), name=msg.text)
        await utils.send_admins("subcategory_is_edited_alert", bot, DB,
            username=msg.from_user.mention_html(),
            old_name=data['old_name'],
            new_name=msg.text,
        )
        await msg.answer(BotTexts.ADMIN_TEXTS.products_manage_text, 
                                 reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())
    else:
        await msg.reply(BotTexts.ADMIN_TEXTS.name_error)

    
@adminRouter.callback_query(F.data == "del_all_subcategories")
async def del_all_subcategories(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.del_all_subcategories_text,
                                 reply_markup=BotButtons.ADMIN_INLINE.confirm(
                                     f"delete_all_subcategories", "products_manage"
                                 ).as_markup())
    

@adminRouter.callback_query(F.data == "delete_all_subcategories")
async def delete_all_subcategories(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.delete()
    await DB.delete_all_subcategories()
    await utils.send_admins("all_subcategories_are_deleted_alert", bot, DB,
        username=call.from_user.mention_html(),
    )
    await call.message.answer(BotTexts.ADMIN_TEXTS.products_manage_text, 
                     reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())
    

### Positions
@adminRouter.callback_query(F.data == "add_position")
async def add_position(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    categories = await DB.get_all_categories()
    if categories:
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.select_category,
                                     reply_markup=BotButtons.ADMIN_INLINE.category_select_menu(BotTexts, categories).as_markup())
        await state.set_state(adminStates.AdminProductsManage.select_category_for_add_position)
    else:
        await call.answer(BotTexts.ADMIN_TEXTS.no_categories_available)


@adminRouter.callback_query(F.data.startswith("select_category:"), StateFilter(adminStates.AdminProductsManage.select_category_for_add_position, adminStates.AdminProductsManage.select_subcategory_for_add_position))
async def select_category_for_add_position(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    data = call.data.split(":")
    subcategories = await DB.get_subcategories(cat_id=int(data[1]))
    if subcategories and len(data) == 2:
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.select_subcategory, 
                                    reply_markup=BotButtons.ADMIN_INLINE.subcategory_select_menu(BotTexts, subcategories, True).as_markup())
        await state.set_state(adminStates.AdminProductsManage.select_subcategory_for_add_position)
    else:
        await state.set_state(adminStates.AdminProductsManage.enter_position_name)
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.enter_position_name,
                                     reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
    await state.update_data(category_id=data[1])
        
        
@adminRouter.callback_query(F.data.startswith("select_subcategory:"), StateFilter(adminStates.AdminProductsManage.select_subcategory_for_add_position))
async def select_subcategory_for_add_position(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.set_state(adminStates.AdminProductsManage.enter_position_name)
    await state.update_data(subcategory_id=call.data.split(":")[1])
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.enter_position_name,
                                 reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
    

@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_position_name))
async def enter_position_name(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if len(msg.text) <= 64:
        await state.set_state(adminStates.AdminProductsManage.enter_position_price)
        await state.update_data(name=msg.text)
        await msg.reply(BotTexts.ADMIN_TEXTS.enter_position_price,
                                 reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
    else:
        await msg.reply(BotTexts.ADMIN_TEXTS.name_error)


@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_position_price))
async def enter_position_price(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if msg.text.isdigit() or msg.text.replace(".", "").replace(",", "").isdigit():
        await state.set_state(adminStates.AdminProductsManage.enter_position_item_type)
        await state.update_data(price=msg.text)
        await msg.reply(BotTexts.ADMIN_TEXTS.enter_position_item_type,
                                 reply_markup=BotButtons.ADMIN_INLINE.position_item_types(BotTexts).as_markup())
    else:
        await msg.reply(BotTexts.ADMIN_TEXTS.value_is_no_number)


@adminRouter.callback_query(F.data.startswith("select_position_type:"), StateFilter(adminStates.AdminProductsManage.enter_position_item_type))
async def enter_position_item_type(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.enter_position_description, 
                                 reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
    await state.set_state(adminStates.AdminProductsManage.enter_position_description)
    await state.update_data(item_type=call.data.split(":")[1])


@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_position_description))
async def enter_position_description(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if len(msg.text) <= 2000:
        await msg.reply(BotTexts.ADMIN_TEXTS.enter_position_photo, 
                    reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
        await state.set_state(adminStates.AdminProductsManage.enter_position_photo)
        await state.update_data(description=None if msg.text == "-" else msg.html_text)
    else:
        await msg.reply(BotTexts.ADMIN_TEXTS.description_error)


@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_position_photo), F.photo)
@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_position_photo), F.text == "-")
async def enter_position_photo(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await msg.reply(BotTexts.ADMIN_TEXTS.enter_position_type, 
                    reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
    await state.set_state(adminStates.AdminProductsManage.enter_position_type)
    await state.update_data(photo=None if msg.text == "-" else msg.photo[-1].file_id)


@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_position_type), F.text.in_({"+", "-"}))
async def enter_position_type(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    data = await state.get_data()
    await state.clear()
    position_type = True if msg.text == "+" else False
    currency = (await DB.get_settings()).currency.value
    if currency == "rub":
        price_rub = float(data['price'])
        price_eur = await utils.get_exchange(price_rub, 'RUB', 'EUR', DB)
        price_usd = await utils.get_exchange(price_rub, 'RUB', 'USD', DB)
    elif currency == 'usd':
        price_usd = float(data['price'])
        price_rub = await utils.get_exchange(price_usd, 'USD', 'RUB', DB)
        price_eur = await utils.get_exchange(price_usd, 'USD', 'EUR', DB)
    else:
        # eur
        price_eur = float(data['price'])
        price_usd = await utils.get_exchange(price_eur, 'EUR', 'USD', DB)
        price_rub = await utils.get_exchange(price_eur, 'EUR', 'RUB', DB)

    await DB.add_position(
        data['name'],
        price_rub,
        price_usd,
        price_eur,
        data['description'],
        data['photo'],
        data.get("category_id"),
        data.get("subcategory_id"),
        position_type,
        data['item_type'],
    )
    category = await DB.get_category(cat_id=int(data.get("category_id")))
    subcategory = await DB.get_subcategory(sub_cat_id=int(data.get("subcategory_id"))) if data.get("subcategory_id") else None
    await utils.send_admins("position_is_created_alert", bot, DB,
        username=msg.from_user.mention_html(),
        cat_name=category.name,
        cat_id=category.cat_id,
        subcategory=f"<code>{subcategory.name}</code> [<code>{subcategory.sub_cat_id}</code>]" if subcategory else None,
        name=data['name'],
        price=data['price'],
        curr=BotConfig.CURRENCIES[currency]['sign'],
        position_type=BotTexts.ADMIN_TEXTS.position_type[position_type],
        item_type=BotTexts.ADMIN_TEXTS.position_type[data['item_type']],
        description=data['description'], \
        photo=data['photo'])


@adminRouter.callback_query(F.data == "edit_position")
async def edit_position(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    if await DB.get_all_positions():
        categories = await DB.get_all_categories()
        if categories:
            try:
                await call.message.edit_text(BotTexts.ADMIN_TEXTS.select_category, 
                                  reply_markup=BotButtons.ADMIN_INLINE.category_select_menu(BotTexts, categories).as_markup())
            except:
                try:
                    await call.message.delete()
                except:
                    pass
                await call.message.answer(BotTexts.ADMIN_TEXTS.select_category, 
                                  reply_markup=BotButtons.ADMIN_INLINE.category_select_menu(BotTexts, categories).as_markup())
            await state.set_state(adminStates.AdminProductsManage.select_category_for_edit_position)
        else:
            await call.answer(BotTexts.ADMIN_TEXTS.no_categories_available)
    else:
        await call.answer(BotTexts.ADMIN_TEXTS.no_positions_available)


@adminRouter.callback_query(F.data.startswith("select_category:"), StateFilter(adminStates.AdminProductsManage.select_category_for_edit_position))
async def select_category_for_edit_position(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    positions = await DB.get_positions(cat_id=int(call.data.split(":")[1]), sub_cat_id=None)
    sub_categories = await DB.get_subcategories(cat_id=int(call.data.split(":")[1]))
    if sub_categories:
        await call.message.edit_text(
            BotTexts.ADMIN_TEXTS.select_subcategory,
            reply_markup=BotButtons.ADMIN_INLINE.subcategory_select_menu(BotTexts, subcategories=sub_categories, 
                                                                         positions=positions, is_for_edit_position=True).as_markup()
        )
        await state.set_state(adminStates.AdminProductsManage.select_subcategory_for_edit_position)
    else:
        if positions:
            await call.message.edit_text(
                BotTexts.ADMIN_TEXTS.select_position,
                reply_markup=BotButtons.ADMIN_INLINE.position_select_menu(BotTexts, positions).as_markup(),
            )
            await state.set_state(adminStates.AdminProductsManage.select_position_for_edit)
        else:
            await call.answer(BotTexts.ADMIN_TEXTS.no_positions_available_in_this_category)


@adminRouter.callback_query(F.data.startswith("select_subcategory:"), StateFilter(adminStates.AdminProductsManage.select_subcategory_for_edit_position))
async def select_subcategory_for_edit_position(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    positions = await DB.get_positions(sub_cat_id=int(call.data.split(":")[1]))
    if positions:
        await call.message.edit_text(
            BotTexts.ADMIN_TEXTS.select_position,
            reply_markup=BotButtons.ADMIN_INLINE.position_select_menu(BotTexts, positions).as_markup(),
        )
        await state.set_state(adminStates.AdminProductsManage.select_position_for_edit)
    else:
        await call.answer(BotTexts.ADMIN_TEXTS.no_positions_available_in_this_subcategory)


async def get_position_info_paginated(BotTexts, position, message, page=0, is_edit=True):
    """Получить информацию о позиции с пагинацией"""
    category = await DB.get_category(cat_id=position.cat_id)
    subcategory = await DB.get_subcategory(sub_cat_id=position.sub_cat_id)
    items_count = len(await DB.get_items(pos_id=position.pos_id))
    currency = (await DB.get_settings()).currency.value
    
    if currency == "rub":
        price = position.price_rub
    elif currency == 'usd':
        price = position.price_usd
    else:
        price = position.price_eur
    
    # Основная информация (всегда на первой странице)
    basic_info = f"""<b>🌐 Позиция: <code>{position.name}</code>
💎 Категория: <code>{category.name}</code> [<code>{category.cat_id}</code>]
🎲 Подкатегория: {f"<code>{subcategory.name}</code> [<code>{subcategory.sub_cat_id}</code>]" if subcategory else "Нет"}
💰 Цена: <code>{price}{BotConfig.CURRENCIES[currency]['sign']}</code>
🪙 Тип позиции: <code>{BotTexts.ADMIN_TEXTS.position_type[position.is_infinity]}</code>
🔰 Тип товара: <code>{BotTexts.ADMIN_TEXTS.position_type[position.item_type]}</code>
🛒 Кол-во товаров: <code>{items_count} шт.</code></b>"""
    
    # Описание (может быть на отдельной странице)
    description_text = f"<b>🧾 Описание:</b>\n\n{position.description}" if position.description else "<b>🧾 Описание:</b>\n\nОписание отсутствует"
    
    # Определяем, нужна ли пагинация
    total_text = basic_info + "\n\n" + description_text
    text_with_buttons = total_text + "\n\n<b>❗ Выберите, что хотите изменить:</b>"
    
    # Для фото лимит caption - 1024 символа, для обычного сообщения - 4096
    max_length = 1024 if (position.photo and position.photo != "-") else 3000
    
    if len(text_with_buttons) <= max_length:  # Если текст помещается в одно сообщение
        if position.photo and position.photo != "-":
            try:
                await message.delete()
            except TelegramBadRequest:
                pass
            await message.answer_photo(caption=text_with_buttons, photo=position.photo,
                reply_markup=BotButtons.ADMIN_INLINE.position_edit(BotTexts, position.pos_id).as_markup())
        else:
            if is_edit:
                await message.edit_text(text=text_with_buttons,
                    reply_markup=BotButtons.ADMIN_INLINE.position_edit(BotTexts, position.pos_id).as_markup())
            else:
                await message.answer(text=text_with_buttons,
                    reply_markup=BotButtons.ADMIN_INLINE.position_edit(BotTexts, position.pos_id).as_markup())
    else:
        # Нужна пагинация
        pages = [
            basic_info + "\n\n<b>❗ Выберите, что хотите изменить:</b>"
        ]
        
        # Разбиваем описание на части если оно очень длинное
        if len(description_text) > 2000:
            # Разбиваем длинное описание на страницы по 2000 символов
            desc_chunks = []
            for i in range(0, len(description_text), 2000):
                desc_chunks.append(description_text[i:i+2000])
            pages.extend(desc_chunks)
        else:
            pages.append(description_text)
        
        current_page = pages[page] if page < len(pages) else pages[0]
        
        # Создаем клавиатуру с навигацией
        keyboard = BotButtons.ADMIN_INLINE.position_edit_paginated(BotTexts, position.pos_id, page, len(pages))
        
        if position.photo and position.photo != "-" and page == 0:  # Фото только на первой странице
            # Для caption фото максимум 1024 символа
            if len(current_page) > 1024:
                # Обрезаем текст для caption и добавляем информацию о продолжении
                current_page = current_page[:1000] + "...\n\n📄 Используйте кнопки навигации для просмотра полной информации"
            try:
                await message.delete()
            except TelegramBadRequest:
                pass
            await message.answer_photo(caption=current_page, photo=position.photo,
                reply_markup=keyboard.as_markup())
        else:
            if is_edit and page == 0:
                await message.edit_text(text=current_page, reply_markup=keyboard.as_markup())
            else:
                await message.answer(text=current_page, reply_markup=keyboard.as_markup())


async def get_position_info(BotTexts, position, message, is_edit=True):
    """Получить информацию о позиции (использует пагинацию)"""
    await get_position_info_paginated(BotTexts, position, message, page=0, is_edit=is_edit)


@adminRouter.callback_query(F.data.startswith("position_page:"))
async def position_page_navigation(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    """Обработчик навигации по страницам позиции"""
    await state.clear()
    data = call.data.split(":")
    position_id = int(data[1])
    page = int(data[2])
    
    position = await DB.get_position(pos_id=position_id)
    if position:
        await get_position_info_paginated(BotTexts, position, call.message, page=page, is_edit=True)


@adminRouter.callback_query(F.data == "noop")
async def noop_handler(call: CallbackQuery):
    """Обработчик для кнопок, которые ничего не делают"""
    await call.answer()


@adminRouter.callback_query(F.data.startswith("select_position:"), StateFilter(adminStates.AdminProductsManage.select_position_for_edit, adminStates.AdminProductsManage.select_subcategory_for_edit_position))
async def select_position_for_edit(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    position = await DB.get_position(pos_id=int(call.data.split(":")[1]))
    await get_position_info(BotTexts, position, call.message)


@adminRouter.callback_query(F.data.startswith("position_edit:"))
async def position_edit(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    data = call.data.split(":")
    position = await DB.get_position(pos_id=int(data[1]))
    await call.message.delete()
    if data[2] == "price":
        await call.message.answer(BotTexts.ADMIN_TEXTS.enter_new_position_price)
        await state.set_state(adminStates.AdminProductsManage.enter_new_position_price)
    elif data[2] == "name":
        await call.message.answer(BotTexts.ADMIN_TEXTS.enter_new_position_name)
        await state.set_state(adminStates.AdminProductsManage.enter_new_position_name)
    elif data[2] == "description":
        await call.message.answer(BotTexts.ADMIN_TEXTS.enter_new_position_description)
        await state.set_state(adminStates.AdminProductsManage.enter_new_position_description)
    elif data[2] == "photo":
        await call.message.answer(BotTexts.ADMIN_TEXTS.enter_new_position_photo)
        await state.set_state(adminStates.AdminProductsManage.enter_new_position_photo)
    elif data[2] == "position_type":
        await call.message.answer(BotTexts.ADMIN_TEXTS.enter_position_type)
        await state.set_state(adminStates.AdminProductsManage.enter_new_position_type)
    elif data[2] == "delete":
        await call.message.answer(BotTexts.ADMIN_TEXTS.confirm_position_delete.format(name=position.name),
                                     reply_markup=BotButtons.ADMIN_INLINE.confirm(f"position_edit:{position.pos_id}:del", "products_manage").as_markup())
    elif data[2] == "del":
        await DB.delete_position(position.pos_id)
        await utils.send_admins("position_is_deleted_alert", bot, DB,
            username=call.from_user.mention_html(),
            name=position.name,
        )
        await call.message.answer(BotTexts.ADMIN_TEXTS.products_manage_text, 
                                  reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())
    elif data[2] == "move":
        categories = await DB.get_all_categories()
        await call.message.answer(BotTexts.ADMIN_TEXTS.select_category,
                                  reply_markup=BotButtons.ADMIN_INLINE.category_select_menu(BotTexts, categories).as_markup())
        await state.set_state(adminStates.AdminProductsManage.select_category_for_move_position)
    elif data[2] == "clear_items":
        await call.message.answer(BotTexts.ADMIN_TEXTS.confirm_position_items_delete.format(name=position.name),
                                  reply_markup=BotButtons.ADMIN_INLINE.confirm(f"position_edit:{position.pos_id}:confirm_delete_items", "products_manage").as_markup())
    elif data[2] == "upload_items":
        await call.message.answer(BotTexts.ADMIN_TEXTS.enter_data_items["text_infinity" if position.item_type == "text" and position.is_infinity else position.item_type],
                                     reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
        await state.set_state(adminStates.AdminProductsManage.enter_data_items)
        await state.update_data(position=position, count_add_items=0)
    elif data[2] == "get_items":
        try:
            items = await DB.get_items(pos_id=position.pos_id)
            text = ""
            for item in items:
                text += f"{BotTexts.ADMIN_TEXTS.item} #{item.item_id}:"
                if item.data:
                    text += f"\n{item.data}"
                if item.file_id:
                    text += f"\n{item.file_id}"
                text += "\n\n"
            with open(f"position_items_{position.pos_id}.txt", "w", encoding="utf-8") as file:
                file.write(f"{BotTexts.ADMIN_TEXTS.position}: {position.name} | #{position.pos_id}: \n\n{text}")
                file.close()

            await call.message.answer_document(document=FSInputFile(f"position_items_{position.pos_id}.txt"), 
                                            caption=BotTexts.ADMIN_TEXTS.list_of_items.format(name=position.name))
            os.remove(f"position_items_{position.pos_id}.txt")
        except:
            print_exc()
            await call.message.answer(BotTexts.ADMIN_TEXTS.get_list_of_items_error,
                                      reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
    else:
        # confirm_delete_items
        await DB.delete_position_items(position.pos_id)
        await utils.send_admins("position_items_is_deleted_alert", bot, DB,
            username=call.from_user.mention_html(),
            name=position.name,
        )
        await get_position_info(BotTexts, await DB.get_position(pos_id=position.pos_id), call.message, False)
    await state.update_data(position=position)


@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_new_position_price))
async def enter_new_position_price(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if msg.text.isdigit() or msg.text.replace(",", "").replace(".", "").isdigit():
        position = (await state.get_data())['position']
        await state.clear()
        currency = (await DB.get_settings()).currency.value
        if currency == "rub":
            price_rub = float(msg.text)
            price_eur = await utils.get_exchange(price_rub, 'RUB', 'EUR', DB)
            price_usd = await utils.get_exchange(price_rub, 'RUB', 'USD', DB)
        elif currency == 'usd':
            price_usd = float(msg.text)
            price_rub = await utils.get_exchange(price_usd, 'USD', 'RUB', DB)
            price_eur = await utils.get_exchange(price_usd, 'USD', 'EUR', DB)
        else:
            # eur
            price_eur = float(msg.text)
            price_usd = await utils.get_exchange(price_eur, 'EUR', 'USD', DB)
            price_rub = await utils.get_exchange(price_eur, 'EUR', 'RUB', DB)
        await DB.update_position(position_id=position.pos_id, price_rub=price_rub, price_usd=price_usd, price_eur=price_eur)
        await get_position_info(BotTexts, await DB.get_position(pos_id=position.pos_id), msg, False)
    else:
        await msg.reply(BotTexts.ADMIN_TEXTS.value_is_no_number)
    

@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_new_position_name))
async def enter_new_position_name(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if len(msg.text) <= 64:
        position = (await state.get_data())['position']
        await state.clear()
        await DB.update_position(position_id=position.pos_id, name=msg.text)
        await get_position_info(BotTexts, await DB.get_position(pos_id=position.pos_id), msg, False)
    else:
        await msg.reply(BotTexts.ADMIN_TEXTS.name_error)


@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_new_position_description))
async def enter_new_position_description(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if len(msg.text) <= 2000:
        position = (await state.get_data())['position']
        await state.clear()
        await DB.update_position(position_id=position.pos_id, description=None if msg.text == "-" else msg.html_text)
        await get_position_info(BotTexts, await DB.get_position(pos_id=position.pos_id), msg, False)
    else:
        await msg.reply(BotTexts.ADMIN_TEXTS.description_error)


@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_new_position_photo), F.photo)
@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_new_position_photo), F.text == "-")
async def enter_new_position_photo(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    position = (await state.get_data())['position']
    await state.clear()
    await DB.update_position(position_id=position.pos_id, photo=None if msg.text == "-" else msg.photo[-1].file_id)
    await get_position_info(BotTexts, await DB.get_position(pos_id=position.pos_id), msg, False)


@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_new_position_type), F.text.in_({"+", "-"}))
async def enter_new_position_type(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    position = (await state.get_data())['position']
    await state.clear()
    await DB.update_position(position_id=position.pos_id, is_infinity=True if msg.text == "+" else False)
    await get_position_info(BotTexts, await DB.get_position(pos_id=position.pos_id), msg, False)


@adminRouter.callback_query(F.data.startswith("select_category:"), StateFilter(adminStates.AdminProductsManage.select_category_for_move_position, adminStates.AdminProductsManage.select_subcategory_for_move_position))
async def select_category_for_move_position(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    position = (await state.get_data())['position']
    data = call.data.split(":")
    subcategories = await DB.get_subcategories(cat_id=int(data[1]))
    if subcategories and len(data) == 2:
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.select_subcategory, 
                                    reply_markup=BotButtons.ADMIN_INLINE.subcategory_select_menu(BotTexts, subcategories, True).as_markup())
        await state.set_state(adminStates.AdminProductsManage.select_subcategory_for_move_position)
    else: 
        await DB.update_position(position_id=position.pos_id, cat_id=int(data[1]))
        await get_position_info(BotTexts, await DB.get_position(pos_id=position.pos_id), call.message)
        
        
@adminRouter.callback_query(F.data.startswith("select_subcategory:"), StateFilter(adminStates.AdminProductsManage.select_subcategory_for_move_position))
async def select_subcategory_for_move_position(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    position = (await state.get_data())['position']
    subcategory = await DB.get_subcategory(sub_cat_id=int(call.data.split(":")[1]))
    await DB.update_position(position_id=position.pos_id, cat_id=subcategory.cat_id, sub_cat_id=subcategory.sub_cat_id)
    await get_position_info(BotTexts, await DB.get_position(pos_id=position.pos_id), call.message)


@adminRouter.callback_query(F.data == "del_all_positions")
async def del_all_positions(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.del_all_positions_text,
                                 reply_markup=BotButtons.ADMIN_INLINE.confirm(
                                     f"delete_all_positions", "products_manage"
                                 ).as_markup())
    

@adminRouter.callback_query(F.data == "delete_all_positions")
async def delete_all_positions(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.delete()
    await DB.delete_all_positions()
    await utils.send_admins("all_positions_are_deleted_alert", bot, DB,
            username=call.from_user.mention_html(),
        )
    await call.message.answer(BotTexts.ADMIN_TEXTS.products_manage_text, 
                     reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())


### Items
@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_data_items), F.photo, F.document)
@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_data_items))
async def enter_data_items(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    cache_message = await msg.reply(BotTexts.ADMIN_TEXTS.products_add_wait)
    try:
        count_add, new_count = 0, 0
        data = await state.get_data()
        position: models.Position = data['position']
        if position.item_type == "text":
            if position.is_infinity:
                items = msg.text
                new_count = data["count_add_items"] + 1
            else:
                if msg.document:
                    file = await msg.bot.get_file(msg.document.file_id)
                    await msg.bot.download_file(file.file_path,
                                                destination=msg.document.file_name)
                    with open(msg.document.file_name, 'r', encoding="utf-8") as f:
                        items = f.read().split("\n\n")
                        f.close()
                    os.remove(msg.document.file_name)
                else:                    
                    items = msg.text.split("\n\n")
                
                for check_item in items:
                    if not check_item.isspace() and check_item != "": count_add += 1
                new_count = data["count_add_items"] + count_add
            await DB.add_items(position.cat_id, position.pos_id, items, None, False, position.is_infinity)
        elif position.item_type == "photo" and msg.content_type == "photo":
            await DB.add_items(position.cat_id, position.pos_id, None if not msg.html_text else msg.html_text, f"photo:{msg.photo[-1].file_id}", True)
            new_count = data["count_add_items"] + 1
        elif position.item_type == "file" and msg.content_type == "document":
            await DB.add_items(position.cat_id, position.pos_id, None if not msg.html_text else msg.html_text, f"file:{msg.document.file_id}", True)
            new_count = data["count_add_items"] + 1
        else:
            return await msg.reply(BotTexts.ADMIN_TEXTS.no_need_item_type_sent)
        await state.update_data(count_add_items=new_count)
        await cache_message.edit_text(BotTexts.ADMIN_TEXTS.products_successful_added.format(count=count_add or 1),
                                    reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "stop_upload_items", 
                                                                                        BotTexts.ADMIN_TEXTS.stop_upload_items).as_markup() if not position.is_infinity else None)
    except:
        print_exc()
        await cache_message.edit_text(BotTexts.ADMIN_TEXTS.upload_items_error)



@adminRouter.callback_query(StateFilter(adminStates.AdminProductsManage.enter_data_items), F.data == "stop_upload_items")
async def stop_upload_items(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.stop_upload_items_text.format(count=(await state.get_data())['count_add_items']))
    await state.clear()


@adminRouter.callback_query(F.data == "add_items")
async def add_items(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    categories = await DB.get_all_categories()
    if categories:
        await call.message.edit_text(BotTexts.ADMIN_TEXTS.select_category,
                                 reply_markup=BotButtons.ADMIN_INLINE.category_select_menu(BotTexts, categories).as_markup())
        await state.set_state(adminStates.AdminProductsManage.select_category_for_add_items)
    else:
        await call.answer(BotTexts.ADMIN_TEXTS.no_categories_available)


@adminRouter.callback_query(F.data.startswith("select_category:"), StateFilter(adminStates.AdminProductsManage.select_category_for_add_items))
async def select_category_for_add_items(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    positions = await DB.get_positions(cat_id=int(call.data.split(":")[1]), sub_cat_id=None)
    sub_categories = await DB.get_subcategories(cat_id=int(call.data.split(":")[1]))
    if sub_categories:
        await call.message.edit_text(
            BotTexts.ADMIN_TEXTS.select_subcategory,
            reply_markup=BotButtons.ADMIN_INLINE.subcategory_select_menu(BotTexts, subcategories=sub_categories, 
                                                                         positions=positions, is_for_edit_position=True).as_markup()
        )
        await state.set_state(adminStates.AdminProductsManage.select_subcategory_for_add_items)
    else:
        if positions:
            await call.message.edit_text(
                BotTexts.ADMIN_TEXTS.select_position,
                reply_markup=BotButtons.ADMIN_INLINE.position_select_menu(BotTexts, positions).as_markup(),
            )
            await state.set_state(adminStates.AdminProductsManage.select_position_for_add_items)
        else:
            await call.answer(BotTexts.ADMIN_TEXTS.no_positions_available_in_this_category)


@adminRouter.callback_query(F.data.startswith("select_subcategory:"), StateFilter(adminStates.AdminProductsManage.select_subcategory_for_add_items))
async def select_subcategory_for_add_items(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    positions = await DB.get_positions(sub_cat_id=int(call.data.split(":")[1]))
    if positions:
        await call.message.edit_text(
            BotTexts.ADMIN_TEXTS.select_position,
            reply_markup=BotButtons.ADMIN_INLINE.position_select_menu(BotTexts, positions).as_markup(),
        )
        await state.set_state(adminStates.AdminProductsManage.select_position_for_add_items)
    else:
        await call.answer(BotTexts.ADMIN_TEXTS.no_positions_available_in_this_subcategory)


@adminRouter.callback_query(F.data.startswith("select_position:"), StateFilter(adminStates.AdminProductsManage.select_position_for_add_items, 
                                                                               adminStates.AdminProductsManage.select_subcategory_for_add_items))
async def select_position_for_add_items(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    position = await DB.get_position(pos_id=int(call.data.split(":")[1]))
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.enter_data_items["text_infinity" if position.item_type == "text" and position.is_infinity else position.item_type],
                                     reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
    await state.set_state(adminStates.AdminProductsManage.enter_data_items)
    await state.update_data(position=position, count_add_items=0)


@adminRouter.callback_query(F.data == "del_item")
async def del_item(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.enter_item_id_for_delete,
                                 reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
    await state.set_state(adminStates.AdminProductsManage.enter_item_id_for_delete)


@adminRouter.message(StateFilter(adminStates.AdminProductsManage.enter_item_id_for_delete))
async def enter_item_id_for_delete(msg: Message, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    if msg.text.isdigit():
        await state.clear()
        await DB.delete_item(int(msg.text))
        await msg.reply(BotTexts.ADMIN_TEXTS.success)
        await msg.answer(BotTexts.ADMIN_TEXTS.products_manage_text, 
                                 reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())
    else:
        await msg.reply(BotTexts.ADMIN_TEXTS.value_is_no_number,
                        reply_markup=BotButtons.ADMIN_INLINE.custom_button(BotTexts, "products_manage").as_markup())
        

@adminRouter.callback_query(F.data == "del_all_items")
async def del_all_items(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.edit_text(BotTexts.ADMIN_TEXTS.del_all_items_text,
                                 reply_markup=BotButtons.ADMIN_INLINE.confirm(
                                     f"delete_all_items", "products_manage"
                                 ).as_markup())
    

@adminRouter.callback_query(F.data == "delete_all_items")
async def delete_all_items(call: CallbackQuery, state: FSMContext, BotTexts: BTs.Ru | BTs.En | BTs.Ua):
    await state.clear()
    await call.message.delete()
    await DB.delete_all_items()
    await utils.send_admins("all_items_are_deleted_alert", bot, DB,
            username=call.from_user.mention_html(),
        )
    await call.message.answer(BotTexts.ADMIN_TEXTS.products_manage_text, 
                     reply_markup=BotButtons.ADMIN_INLINE.products_manage(BotTexts).as_markup())