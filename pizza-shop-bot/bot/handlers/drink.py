import json

import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler
from bot.handlers.handler import HandlerStatus


class DrinksSelectionHandler(Handler):
    def can_handle(self, update: dict, state: str, data: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_DRINKS":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("drink_")

    def handle(self, update: dict, state: str, data: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        drink_mapping = {
            "drink_coca_cola": "Кока-Кола",
            "drink_pepsi": "Пепси",
            "drink_orange_juice": "Апельсиновый сок",
            "drink_apple_juice": "Яблочный сок",
            "drink_water": "Вода",
            "drink_milkshake": "Молочный коктейль",
            "drink_none": "Без напитков",
        }
        selected_drink = drink_mapping.get(callback_data)

        data["drink"] = selected_drink

        bot.database_client.update_user_order_json(telegram_id, data)
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_ORDER_APPROVE")
        bot.telegram_client.answerCallbackQuery(update["callback_query"]["id"])

        bot.telegram_client.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        pizza_name = data.get("pizza_name", "Unknown")
        pizza_size = data.get("pizza_size", "Unknown")
        drink = data.get("drink", "Unknown")

        order_summary = f"""🥰 **Давай проверим твой заказ:**

        🍕 **Пицца:** {pizza_name}
        📏 **Размер:** {pizza_size}
        🥤 **Напиток:** {drink}

        Всё так, как ты хотел(а)?"""

        bot.telegram_client.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text=order_summary,
            parse_mode="Markdown",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "✅ Всё супер!", "callback_data": "order_approve"},
                            {
                                "text": "🔄 Хочу изменить","callback_data": "order_restart",
                            },
                        ],
                    ],
                },
            ),
        )
        return HandlerStatus.STOP