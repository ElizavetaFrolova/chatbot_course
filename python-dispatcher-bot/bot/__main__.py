import bot.database_client
import bot.telegram_client
import time
from bot.dispatcher import Dispatcher
from bot.handlers.message_echo import MessageEcho
from bot.long_polling import start_long_polling
from bot.handlers.message_db import DatabaseHandler
from bot.handlers.message_photo import MessagePhoto


if __name__=="__main__":
    try:
        dispatcher =Dispatcher()
        dispatcher.add_handler(DatabaseHandler(),MessagePhoto(),MessageEcho())
        start_long_polling(dispatcher)        
    except KeyboardInterrupt:
        print("\nBye!")