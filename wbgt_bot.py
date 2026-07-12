import requests
from telegram import Bot
import asyncio
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
# Only needed if the channel/group has Topics enabled and you want
# messages posted inside a specific topic rather than General.
TOPIC_ID = os.environ.get("TOPIC_ID")  # optional

UV_API = "https://api-open.data.gov.sg/v2/real-time/api/uv"

# File to remember the previous UV category
STATE_FILE = "last_uv_status.txt"


def fetch_uv():
    response = requests.get(UV_API, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["data"]["records"][0]["index"][0]["value"]


def get_uv_status(uv):
    if uv <= 2:
        return "LOW"
    elif uv <= 5:
        return "MODERATE"
    elif uv <= 7:
        return "HIGH"
    elif uv <= 10:
        return "VERY HIGH"
    else:
        return "EXTREME"


def get_message(status, uv):
    if status == "LOW":
        return (
            "*UV Index Update*\n\n"
            f"Current UV Index: *{uv}*\n"
            "Risk Level: *LOW*\n\n"
            "UV levels have dropped to a low level.\n"
            "No special sun protection is required."
        )
    elif status == "MODERATE":
        return (
            "*UV Index Update*\n\n"
            f"Current UV Index: *{uv}*\n"
            "Risk Level: *MODERATE*\n\n"
            "Some protection against sunburn is needed."
        )
    elif status == "HIGH":
        return (
            "*UV Index Update*\n\n"
            f"Current UV Index: *{uv}*\n"
            "Risk Level: *HIGH*\n\n"
            "Reduce prolonged exposure to the sun."
        )
    elif status == "VERY HIGH":
        return (
            "*UV Index Update*\n\n"
            f"Current UV Index: *{uv}*\n"
            "Risk Level: *VERY HIGH*\n\n"
            "Extra sun protection is strongly recommended."
        )
    else:
        return (
            "*UV Index Update*\n\n"
            f"Current UV Index: *{uv}*\n"
            "Risk Level: *EXTREME*\n\n"
            "Avoid outdoor activities where possible."
        )


def load_previous_status():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    return None


def save_status(status):
    with open(STATE_FILE, "w") as f:
        f.write(status)


async def main():
    uv = fetch_uv()
    current_status = get_uv_status(uv)
    previous_status = load_previous_status()

    # Only send when the UV category changes
    if current_status != previous_status:
        # Skip the very first run if UV is LOW
        if not (previous_status is None and current_status == "LOW"):
            bot = Bot(token=TELEGRAM_TOKEN)
            send_kwargs = {
                "chat_id": CHANNEL_ID,
                "text": get_message(current_status, uv),
                "parse_mode": "Markdown",
            }
            if TOPIC_ID:
                send_kwargs["message_thread_id"] = int(TOPIC_ID)
            await bot.send_message(**send_kwargs)
            print(f"Notification sent: {current_status}")

    # Save the current category for the next run
    save_status(current_status)

if __name__ == "__main__":
    asyncio.run(main())
