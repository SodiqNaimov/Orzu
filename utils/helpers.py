import logging

from django.conf import settings
from django.contrib.sites import requests

logger = logging.getLogger(__name__)


def send_message(chat_id, text):
    url = "https://api.telegram.org/bot{token}/{method}".format(
        token=settings.BOT_TOKEN,
        method="sendMessage"
    )
    data = dict(
        chat_id=chat_id,
        text=text,
        parse_mode='HTML',
        disable_web_page_preview=True
    )
    response = requests.post(url, json=data)

    logger.debug(response.json())
