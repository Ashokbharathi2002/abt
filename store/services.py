import requests
from django.conf import settings

def send_telegram_message(message):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if bot_token == 'PLACEHOLDER_BOT_TOKEN' or chat_id == 'PLACEHOLDER_CHAT_ID':
        print(f"TELEGRAM MOCK: Would have sent message: {message}")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False
