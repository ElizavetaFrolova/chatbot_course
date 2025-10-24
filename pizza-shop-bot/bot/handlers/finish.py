import json

import bot.telegram_client
from bot.database_client import clear_user_state_and_order, update_user_state
from bot.handlers.handler import Handler
from bot.handlers.handler import HandlerStatus


class OrderApprovalHandler(Handler):
    def can_handle(self, update: dict, state: str, data: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_ORDER_APPROVE":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data in ["order_approve", "order_restart"]

    def handle(self, update: dict, state: str, data: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        bot.telegram_client.answerCallbackQuery(update["callback_query"]["id"])
        bot.telegram_client.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        if callback_data == "order_approve":
            update_user_state(telegram_id, "ORDER_FINISHED")

            pizza_name = data.get("pizza_name", "Unknown")
            pizza_size = data.get("pizza_size", "Unknown")
            drink = data.get("drink", "Unknown")

            order_confirmation = f"""✅ **Заказ подтвержден!**
                🍕 **Ваш заказ:**
                • Пицца: {pizza_name}
                • Размер: {pizza_size}
                • Напиток: {drink}

                Спасибо за заказ! Ваша пицца будет готова в ближайшее время.

                Отправьте /start для нового заказа."""

            # Send order confirmation message
            bot.telegram_client.sendMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text=order_confirmation,
                parse_mode="Markdown",
            )

        elif callback_data == "order_restart":
            clear_user_state_and_order(telegram_id)

            # Update user state to wait for pizza selection
            update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

            # Send pizza selection message with inline keyboard
            bot.telegram_client.sendMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text="Please choose pizza type",
                reply_markup=json.dumps(
                    {
                            "inline_keyboard": [
                            [
                                {"text": "Маргарита", "callback_data": "pizza_margherita"},
                                {"text": "Пепперони", "callback_data": "pizza_pepperoni"},
                            ],
                            [
                                {
                                    "text": "Четыре сезона",
                                    "callback_data": "pizza_quattro_stagioni",
                                },
                                {
                                    "text": "Капричоза",
                                    "callback_data": "pizza_capricciosa",
                                },
                            ],
                            [
                                {"text": "Дьябола", "callback_data": "pizza_diavola"},
                                {"text": "Прошутто", "callback_data": "pizza_prosciutto"},
                            ],
                        ],
                    },
                ),
            )

        return HandlerStatus.STOP