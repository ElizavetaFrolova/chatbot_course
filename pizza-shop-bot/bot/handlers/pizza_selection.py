import json

import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler
from bot.handlers.handler import HandlerStatus


class PizzaSelectionHandler(Handler):
    def can_handle(self, update: dict, state: str, data: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_PIZZA_NAME":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("pizza_")

    def handle(self, update: dict, state: str, data: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        pizza_names_ru = {
        "pizza_margherita": "Маргарита",
        "pizza_pepperoni": "Пепперони", 
        "pizza_quattro_stagioni": "Четыре сезона",
        "pizza_capricciosa": "Капричоза",
        "pizza_diavola": "Дьябола",
        "pizza_prosciutto": "Прошутто"
    }

        pizza_name = pizza_names_ru.get(callback_data, "Неизвестная пицца")

        bot.database_client.update_user_order_json(telegram_id, {"pizza_name": pizza_name})
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_PIZZA_SIZE")
        bot.telegram_client.answerCallbackQuery(update["callback_query"]["id"])
        bot.telegram_client.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )
        bot.telegram_client.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Выбери размер для своей пиццы 😊",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "Маленькая (25см)", "callback_data": "size_small"},
                            {"text": "Средняя (30см)", "callback_data": "size_medium"},
                        ],
                        [
                            {"text": "Большая (35см)", "callback_data": "size_large"},
                            {"text": "Огромная (40см)", "callback_data": "size_xl"},
                        ],
                    ],
                },
            ),
        )
        return HandlerStatus.STOP