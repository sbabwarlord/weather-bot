import requests
from telegram import Bot
import asyncio
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
# THREAD_ID = int(os.environ["THREAD_ID"])

UV_API = "https://api-open.data.gov.sg/v2/real-time/api/uv"

STATE_FILE = "last_uv_status.txt"

def fetch_uv();
    response = requestes.get(UV_API,timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["data"]["records"][0]["index"][0]["value"]

def get_uv_status(uv):
    if uv <=2:
        return "LOW"
    elif uv <=5:
        return "MODERATE"
    elif uv <= 7:
        return "HIGH"
    elif uv <=10:
        return "VERY HIGH"
    else:
        return "EXTREME"

def get_message(status,uv):

    if status =="LOW":
        return (
            " *UV Index Update in Singapore* 🇸🇬\n\n"
            f"Current UV Index: *{uv}*\n"
            "Risk Level: *LOW*\n\n"
            "UV Level have dropped to a low level.\n
            "No sun protection is required."
        )

    elif status == "MODERATE";
        return (
            "☀️ *UV Index in Singapore* 🇸🇬\n\"
        f"Current UV Index: *{uv}*\n"
        "Risk Level: *MODERATE*\n\n"
        "Some protection against sunburn is needed"
    )

     elif status == "HIGH";
        return (
            "*UV Index in Singapore* 🇸🇬\n\"
        f"Current UV Index: *{uv}*\n"
        "Risk Level: *HIGHTE*\n\n"
        Reduce prolonged exposure to the sun"
    )
    
def get_uv_level(uv_value: int):
    if uv_value <= 2:
        return "Low", "No protection needed"
    elif uv_value <= 5:
        return "Moderate", "Some protection against sunburn is needed"
    elif uv_value <= 7:
        return "High", "Some protection against sunburn is needed"
    elif uv_value <= 10:
        return "Very High", "Extra protection against sunburn is needed"
    else:
        return "Extreme", "Extra protection against sunburn is needed"

def fetch_uv():
    response = requests.get(UV_API, timeout=10)
    response.raise_for_status()
    data = response.json()
    index_list = data["data"]["records"][0]["index"]
    latest = index_list[0]
    return latest["value"]

def format_message(uv_value):
    uv_level, uv_advice = get_uv_level(uv_value)

    return (
        f"☀️ *UV Index in Singapore* 🇸🇬\n\n"
        f"UV Index: *{uv_value}* ({uv_level})\n"
        f"Advisory: _{uv_advice}_\n\n"
        f"━━━━━━━━━━━━━━━\n"
    )

async def main():
    uv_value = fetch_uv()
    message = format_message(uv_value)
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=message,
        parse_mode="Markdown",
       # message_thread_id=THREAD_ID
    )
    print("Sent.")

if __name__ == "__main__":
    asyncio.run(main())
