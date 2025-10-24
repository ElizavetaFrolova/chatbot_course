from bot.handlers.handler import Handler
import bot.database_client
from bot.handlers.handler import HandlerStatus


class UpdateDatabaseLogger(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        return True

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:
        bot.database_client.persist_updates([update])
        return HandlerStatus.CONTINUE

