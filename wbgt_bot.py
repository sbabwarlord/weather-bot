import requests
from datetime import datetime
from telegram import Bot
import asyncio
import os
import base64

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

WBGT_API = "https://api-open.data.gov.sg/v2/real-time/api/weather?api=wbgt"
TARGET_STATION = "S126"  # Replace with your station ID

_sig = base64.b64decode("Q29kZSBzaGFyZWQgYnkgVEFCIEJDUA==").decode("utf-8")


def get_colour_code(wbgt: float):
    if wbgt <= 29.9:
        return "", "WHITE"
    elif wbgt <= 30.9:
        return "", "GREEN"
    elif wbgt <= 31.9:
        return "", "YELLOW"
    elif wbgt <= 32.9:
        return "", "RED"
    elif wbgt <= 34.9:
        return "", "BLACK"
    else:
        return "", "CUT OFF"


def fetch_wbgt():
    response = requests.get(WBGT_API, timeout=10)
    response.raise_for_status()
    data = response.json()
    record = data["data"]["records"][0]
    readings = record["item"]["readings"]
    timestamp = record["datetime"]
    station_data = next(
        (r for r in readings if r["station"]["id"] == TARGET_STATION), None
    )
    return station_data, timestamp


def format_message(station_data, timestamp):
    dt = datetime.fromisoformat(timestamp).strftime("%d %b %Y, %I:%M %p")
    wbgt = float(station_data["wbgt"])
    emoji, colour = get_colour_code(wbgt)

    return (
        f"*WBGT Update*\n"
        f"{dt}\n\n"
        f"WBGT: *{wbgt:.1f}°C*\n"
        f"Colour Code: {emoji} *{colour}*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"_{_sig}_"
    )


async def main():
    station_data, timestamp = fetch_wbgt()
    if not station_data:
        print("Station data not found.")
        return

    message = format_message(station_data, timestamp)
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=message,
        parse_mode="Markdown",
    )
    print("Sent.")


if name == "main":
    asyncio.run(main())
