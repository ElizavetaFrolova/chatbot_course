from bot.handler import Handler
import bot.telegram_client


class MessagePhoto(Handler):

    def can_handle(self, update: dict) -> bool:
        return "message" in update and "photo" in update["message"]

    def handle(self, update: dict) -> bool:
        message = update["message"]
        chat_id = message["chat"]["id"]

        best_photo = message["photo"][-1]
        file_id = best_photo["file_id"]

        bot.telegram_client.sendPhoto(
            chat_id=chat_id,
            photo=file_id,
        )

        return False