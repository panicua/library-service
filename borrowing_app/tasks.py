import requests
from celery import shared_task
from decouple import config, Csv

TELEGRAM_API_KEY = config("TELEGRAM_API_KEY", None)
TELEGRAM_CHAT_IDS = config("TELEGRAM_CHAT_IDS", cast=Csv())


@shared_task
def send_telegram_message(message) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage"
    for CHAT_ID in TELEGRAM_CHAT_IDS:
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
        }
        response = requests.post(url, data=payload)

        if response.status_code != 200:
            raise Exception(f"Error sending message: {response.text}")
