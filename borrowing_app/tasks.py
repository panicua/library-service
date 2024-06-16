from datetime import datetime, timedelta

import requests
from celery import shared_task
from decouple import config, Csv

from borrowing_app.models import Borrowing

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


@shared_task
def borrowing_overdue() -> None:
    borrowings = Borrowing.objects.select_related("user", "book").filter(
        expected_return_date__lte=datetime.now().date() + timedelta(days=1),
        actual_return_date__isnull=True,
    )
    if not borrowings:
        send_telegram_message.delay("*No borrowings overdue today!*")
        return

    message = "*Today's overdue borrowings*:\n\n"
    for borrowing in borrowings:
        message += (
            f"*User*: {borrowing.user.email},\n"
            f"*Book*: {borrowing.book.title},\n"
            f"*Expected return date*: {borrowing.expected_return_date},\n"
            f"*Actual return date*: {borrowing.actual_return_date}\n\n"
        )

    send_telegram_message.delay(message)
