"""
Singapore PSI + UV Index -> Telegram

- PSI (haze): posts the latest national/regional PSI reading every run
  (intended to be run hourly).
- UV Index: only posts when the UV risk category changes (LOW / MODERATE /
  HIGH / VERY HIGH / EXTREME), so the channel isn't spammed every hour.

Data sources (official, no API key required for basic use):
  https://api-open.data.gov.sg/v2/real-time/api/psi
  https://api-open.data.gov.sg/v2/real-time/api/uv

Requires: requests, python-telegram-bot
  pip install requests python-telegram-bot
"""

import os
import asyncio
import requests
from telegram import Bot

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

PSI_API = "https://api-open.data.gov.sg/v2/real-time/api/psi"
UV_API = "https://api-open.data.gov.sg/v2/real-time/api/uv"

# File to remember the previous UV category between runs
UV_STATE_FILE = "last_uv_status.txt"

REGIONS = ["north", "south", "east", "west", "central"]


# ---------------------------------------------------------------------------
# PSI (haze)
# ---------------------------------------------------------------------------

def fetch_psi():
    """Return (timestamp, {region: value}) for the latest PSI reading."""
    response = requests.get(PSI_API, timeout=10)
    response.raise_for_status()
    payload = response.json()

    if payload.get("code") != 0:
        raise RuntimeError(f"PSI API returned error: {payload.get('errorMsg')}")

    items = payload["data"]["items"]
    if not items:
        raise RuntimeError("No PSI items returned by API")

    latest = items[0]
    readings = latest["readings"]["psi_twenty_four_hourly"]
    timestamp = latest.get("timestamp", "unknown time")
    values = {region: readings.get(region) for region in ["national"] + REGIONS}
    return timestamp, values


def psi_band(value):
    if value is None:
        return "N/A"
    if value <= 50:
        return "Good"
    if value <= 100:
        return "Moderate"
    if value <= 200:
        return "Unhealthy"
    if value <= 300:
        return "Very Unhealthy"
    return "Hazardous"


def get_psi_message(timestamp, readings):
    national = readings.get("national")
    lines = [
        "*🌫️ PSI in Singapore 🇸🇬*",
        f"_As of {timestamp}_\n",
        f"National (24-hr PSI): *{national}* ({psi_band(national)})\n",
        "Regional breakdown:",
    ]
    for region in REGIONS:
        val = readings.get(region)
        lines.append(f"  • {region.capitalize()}: {val} ({psi_band(val)})")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# UV Index
# ---------------------------------------------------------------------------

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


def get_uv_message(status, uv):
    if status == "LOW":
        return (
            "*☀️ UV Index in Singapore 🇸🇬*\n\n"
            "Risk Level: *LOW*\n\n"
            "UV levels have dropped to a low level.\n"
            "No sun protection is required."
        )
    elif status == "MODERATE":
        return (
            "*☀️ UV Index in Singapore 🇸🇬*\n\n"
            "Risk Level: *MODERATE*\n\n"
            "Some protection against sunburn is needed."
        )
    elif status == "HIGH":
        return (
            "*☀️ UV Index in Singapore 🇸🇬*\n\n"
            "Risk Level: *HIGH*\n\n"
            "Reduce prolonged exposure to the sun."
        )
    elif status == "VERY HIGH":
        return (
            "*☀️ UV Index in Singapore 🇸🇬*\n\n"
            "Risk Level: *VERY HIGH*\n\n"
            "Extra sun protection is strongly recommended."
        )
    else:
        return (
            "*☀️ UV Index in Singapore 🇸🇬*\n\n"
            "Risk Level: *EXTREME*\n\n"
            "Avoid outdoor activities where possible."
        )


def load_previous_uv_status():
    if os.path.exists(UV_STATE_FILE):
        with open(UV_STATE_FILE, "r") as f:
            return f.read().strip()
    return None


def save_uv_status(status):
    with open(UV_STATE_FILE, "w") as f:
        f.write(status)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    bot = Bot(token=TELEGRAM_TOKEN)

    # --- PSI: post every run ---
    try:
        timestamp, readings = fetch_psi()
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=get_psi_message(timestamp, readings),
            parse_mode="Markdown",
        )
        print(f"PSI notification sent (national={readings.get('national')})")
    except Exception as e:
        print(f"Failed to fetch/send PSI: {e}")

    # --- UV: post only when the category changes ---
    try:
        uv = fetch_uv()
        current_status = get_uv_status(uv)
        previous_status = load_previous_uv_status()

        if current_status != previous_status:
            # Skip the very first run if UV is LOW (avoid a noisy "welcome" message)
            if not (previous_status is None and current_status == "LOW"):
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=get_uv_message(current_status, uv),
                    parse_mode="Markdown",
                )
                print(f"UV notification sent: {current_status}")
        save_uv_status(current_status)
    except Exception as e:
        print(f"Failed to fetch/send UV: {e}")


if __name__ == "__main__":
    asyncio.run(main())
