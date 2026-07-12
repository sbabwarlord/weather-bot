import requests
from datetime import datetime
from telegram import Bot
import asyncio
import os
import base64

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
THREAD_ID = int(os.environ["THREAD_ID"])

WBGT_API = "https://api-open.data.gov.sg/v2/real-time/api/weather?api=wbgt"
UV_API = "https://api-open.data.gov.sg/v2/real-time/api/uv"
TARGET_STATION = "S141"  # Replace with your station ID

_sig = base64.b64decode("Q29kZSBzaGFyZWQgYnkgVEFCIEJDUA==").decode("utf-8")

def get_colour_code(wbgt: float):
    if wbgt <= 29.9:
        return "⬜", "WHITE"
    elif wbgt <= 30.9:
        return "🟩", "GREEN"
    elif wbgt <= 31.9:
        return "🟨", "YELLOW"
    elif wbgt <= 32.9:
        return "🟥", "RED"
    elif wbgt <= 34.9:
        return "⬛", "BLACK"
    else:
        return "🚫", "CUT OFF"

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

def fetch_uv():
    response = requests.get(UV_API, timeout=10)
    response.raise_for_status()
    data = response.json()
    index_list = data["data"]["records"][0]["index"]
    latest = index_list[0]
    return latest["value"]

def format_message(station_data, timestamp, uv_value):
    dt = datetime.fromisoformat(timestamp).strftime("%d %b %Y, %I:%M %p")
    wbgt = float(station_data["wbgt"])
    emoji, colour = get_colour_code(wbgt)
    uv_level, uv_advice = get_uv_level(uv_value)

    return (
       # f"🌡️ *WBGT Update* 🌡️\n"
        # f"🕐 {dt}\n\n"
       # f"WBGT: *{wbgt:.1f}°C*\n"
       # f"Colour Code: {emoji} *{colour}*\n\n"
        # f"━━━━━━━━━━━━━━━\n\n"
        f"☀️ *UV Index in Singapore* 🇸🇬\n\n"
        f"UV Index: *{uv_value}* ({uv_level})\n"
        f"Advisory: _{uv_advice}_\n\n"
        f"━━━━━━━━━━━━━━━\n"
       ' f"_{_sig}_"
    )

async def main():
    station_data, timestamp = fetch_wbgt()
    if not station_data:
        print("Station data not found.")
        return
    uv_value = fetch_uv()
    message = format_message(station_data, timestamp, uv_value)
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=message,
        parse_mode="Markdown",
        message_thread_id=THREAD_ID
    )
    print("Sent.")

if name == "__main__":
    asyncio.run(main())
