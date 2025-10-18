from bot.handler import Handler
import bot.database_client


class DatabaseHandler(Handler):
    def can_handle(self, update: dict) -> bool:
        message = update.get("message", {})
        return "text" in message or "photo" in message

    def handle(self, update: dict) -> bool:
        msg = update["message"]

        if "photo" in msg:
            largest_photo = msg["photo"][-1]
            msg["photo"] = [largest_photo]

        bot.database_client.persist_updates([update])
        return True
