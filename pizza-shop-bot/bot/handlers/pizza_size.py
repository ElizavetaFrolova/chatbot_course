import json

import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler
from bot.handlers.handler import HandlerStatus


class PizzaSizeHandler(Handler):
    def can_handle(self, update: dict, state: str, data: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_PIZZA_SIZE":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("size_")

    def handle(self, update: dict, state: str, data: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        size_mapping = {
            "size_small": "Маленькая (25см)",
            "size_medium": "Средняя (30см)",
            "size_large": "Большая (35см)",
            "size_xl": "Огромная (40см)",
        }

        pizza_size = size_mapping.get(callback_data)
        data["pizza_size"] = pizza_size
        bot.database_client.update_user_order_json(telegram_id, data)
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_DRINKS")

        bot.telegram_client.answerCallbackQuery(update["callback_query"]["id"])

        bot.telegram_client.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        bot.telegram_client.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Хочешь добавить напитки к заказу? 🥤",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "Кока-Кола", "callback_data": "drink_coca_cola"},
                            {"text": "Пепси", "callback_data": "drink_pepsi"},
                        ],
                        [
                            {"text": "Апельсиновый сок", "callback_data": "drink_orange_juice"},
                            {"text": "Яблочный сок", "callback_data": "drink_apple_juice"},
                        ],
                        [
                            {"text": "Вода", "callback_data": "drink_water"},
                            {"text": "🍹 Молочный коктейль", "callback_data": "drink_milkshake"},
                        ],
                        [
                            {"text": "❌ Без напитков", "callback_data": "drink_none"},
                        ],
                    ],
                },
            ),
        )
        return HandlerStatus.STOP