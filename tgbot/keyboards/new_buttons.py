from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Дополнительные клавиатуры для новых функций

class SteamPointsButtons:
    """Клавиатуры для Steam Points"""
    
    def steam_points_menu(self, texts):
        """Меню выбора количества Steam Points"""
        builder = InlineKeyboardBuilder()
        
        # Популярные варианты
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.steam_100, callback_data="steam_buy:100"),
            InlineKeyboardButton(text=texts.BUTTONS.steam_500, callback_data="steam_buy:500")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.steam_1000, callback_data="steam_buy:1000"),
            InlineKeyboardButton(text=texts.BUTTONS.steam_2500, callback_data="steam_buy:2500")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.steam_5000, callback_data="steam_buy:5000")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.steam_custom, callback_data="steam_custom")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.back, callback_data="back_to_user_menu")
        )
        return builder
    
    def steam_order_confirm(self, texts, points, price, currency):
        """Кнопки подтверждения заказа Steam Points"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"steam_confirm:{points}"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="steam_points")
        )
        return builder
    
    def steam_insufficient_funds(self, texts):
        """Кнопки при недостатке средств для Steam Points"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.topup_balance, callback_data="refill")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.back, callback_data="steam_points")
        )
        return builder


class ReviewButtons:
    """Клавиатуры для системы отзывов"""
    
    def review_rating(self, texts):
        """Клавиатура выбора рейтинга для отзыва"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.rate_1_star, callback_data="review_rate:1"),
            InlineKeyboardButton(text=texts.BUTTONS.rate_2_stars, callback_data="review_rate:2")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.rate_3_stars, callback_data="review_rate:3"),
            InlineKeyboardButton(text=texts.BUTTONS.rate_4_stars, callback_data="review_rate:4")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.rate_5_stars, callback_data="review_rate:5")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.cancel, callback_data="back_to_user_menu")
        )
        return builder
    
    def review_prompt_buttons(self, texts, receipt):
        """Кнопки предложения написать отзыв после покупки"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.leave_review_now, callback_data=f"write_review:{receipt}")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.review_later, callback_data="close")
        )
        return builder
    
    def reviews_menu(self, texts):
        """Главное меню отзывов"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.view_reviews, callback_data="view_reviews")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.my_reviews, callback_data="my_reviews")
        )
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.back, callback_data="back_to_user_menu")
        )
        return builder
    
    def product_reviews_list(self, texts, categories):
        """Список категорий для просмотра отзывов"""
        builder = InlineKeyboardBuilder()
        
        for category in categories:
            builder.row(
                InlineKeyboardButton(
                    text=f"📦 {category.name}",
                    callback_data=f"view_category_reviews:{category.cat_id}"
                )
            )
        
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.back, callback_data="reviews")
        )
        return builder
    
    def position_reviews_list(self, texts, positions):
        """Список товаров для просмотра отзывов"""
        builder = InlineKeyboardBuilder()
        
        for position in positions:
            builder.row(
                InlineKeyboardButton(
                    text=f"📦 {position.name}",
                    callback_data=f"view_position_reviews:{position.pos_id}"
                )
            )
        
        builder.row(
            InlineKeyboardButton(text=texts.BUTTONS.back, callback_data="view_reviews")
        )
        return builder


# Создаем экземпляры классов
STEAM_BUTTONS = SteamPointsButtons()
REVIEW_BUTTONS = ReviewButtons()
