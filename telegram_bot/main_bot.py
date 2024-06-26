import logging
import sys

import aiohttp
from decouple import config
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

HOST_API_URL = config("HOST_API_URL", None)
TELEGRAM_API_KEY = config("TELEGRAM_API_KEY", None)
LOG_CHAT_ID_ON_START = config("LOG_CHAT_ID_ON_START", default=False, cast=bool)

# logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        self.API_KEY = TELEGRAM_API_KEY
        self.DEFAULT_BOT_URL = "https://api.telegram.org/bot" + self.API_KEY
        self.CHOOSING_OPTION = 0
        self.reply_keyboard = [
            ["Get my chat_id"],
        ]

        self.validate_api_key_not_empty()

    def validate_api_key_not_empty(self) -> None:
        if not self.API_KEY:
            logger.error(
                "API key not found. "
                "Please set the valid TELEGRAM_API_KEY environment variable."
                "Closing the application..."
            )
            sys.exit(1)

    async def start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        await update.message.reply_text(
            "Hi! I'm the *Library notification bot*.\n"
            "Please choose an option from a menu.",
            parse_mode="markdown",
            disable_web_page_preview=True,
            reply_markup=ReplyKeyboardMarkup(self.reply_keyboard),
        )
        return self.CHOOSING_OPTION

    async def handle_user_choice(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        user_choice = update.message.text

        if user_choice == "Get my chat_id":
            await update.message.reply_text(
                f"Your chat ID: {update.message.chat_id}"
            )
            return self.CHOOSING_OPTION

        if user_choice in ["exit", "cancel"]:
            await update.message.reply_text(
                "Bye!", reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                "You selected an option. This is a placeholder response."
            )
            return self.CHOOSING_OPTION

    async def exit(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        await update.message.reply_text("Conversation closed.")
        return ConversationHandler.END

    async def error_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        logger.error("Exception occurred:", exc_info=context.error)

    def main(self) -> None:
        logger.info("Running telegram bot...")
        application = Application.builder().token(self.API_KEY).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                self.CHOOSING_OPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.handle_user_choice,
                    )
                ],
            },
            fallbacks=[
                CommandHandler("exit", self.exit),
                CommandHandler("quit", self.exit),
            ],
        )
        application.add_handler(conv_handler)
        application.run_polling()


Telegram = TelegramBot()

if __name__ == "__main__":
    Telegram.main()
