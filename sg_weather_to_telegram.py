import requests
from telegram import Bot
import asyncio
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

UV_API = "https://api-open.data.gov.sg/v2/real-time/api/uv"
PSI_API = "https://api-open.data.gov.sg/v2/real-time/api/psi"

# Files to remember the previous category for each metric
UV_STATE_FILE = "last_uv_status.txt"
PSI_STATE_FILE = "last_psi_status.txt"


def fetch_uv():
    response = requests.get(UV_API, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["data"]["records"][0]["index"][0]["value"]


def fetch_psi():
    response = requests.get(PSI_API, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["data"]["items"][0]["readings"]["psi_twenty_four_hourly"]["national"]


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


def get_psi_status(psi):
    if psi <= 50:
        return "GOOD"
    elif psi <= 100:
        return "MODERATE"
    elif psi <= 200:
        return "UNHEALTHY"
    elif psi <= 300:
        return "VERY UNHEALTHY"
    else:
        return "HAZARDOUS"


def get_uv_message(status, uv):
    if status == "LOW":
        return (
            "*☀️ UV Index in Singapore 🇸🇬*\n\n"
            # f"Current UV Index: *{uv}*\n"
            "Risk Level: *LOW*\n\n"
            "UV levels have dropped to a low level.\n"
            "No sun protection is required."
        )
    elif status == "MODERATE":
        return (
            "*☀️ UV Index in Singapore 🇸🇬*\n\n"
            # f"Current UV Index: *{uv}*\n"
            "Risk Level: *MODERATE*\n\n"
            "Some protection against sunburn is needed."
        )
    elif status == "HIGH":
        return (
            "*☀️ UV Index in Singapore 🇸🇬*\n\n"
            # f"Current UV Index: *{uv}*\n"
            "Risk Level: *HIGH*\n\n"
            "Reduce prolonged exposure to the sun."
        )
    elif status == "VERY HIGH":
        return (
            "*☀️ UV Index in Singapore 🇸🇬*\n\n"
            # f"Current UV Index: *{uv}*\n"
            "Risk Level: *VERY HIGH*\n\n"
            "Extra sun protection is strongly recommended."
        )
    else:
        return (
            "*☀️ UV Index in Singapore 🇸🇬*\n\n"
            # f"Current UV Index: *{uv}*\n"
            "Risk Level: *EXTREME*\n\n"
            "Avoid outdoor activities where possible."
        )


def get_psi_message(status, psi):
    if status == "GOOD":
        return (
            "*🌫️ PSI in Singapore 🇸🇬*\n\n"
            # f"Current PSI: *{psi}*\n"
            "Risk Level: *GOOD*\n\n"
            "Air quality has returned to a good level.\n"
            "No precautions are needed."
        )
    elif status == "MODERATE":
        return (
            "*🌫️ PSI in Singapore 🇸🇬*\n\n"
            # f"Current PSI: *{psi}*\n"
            "Risk Level: *MODERATE*\n\n"
            "Air quality is acceptable for most people."
        )
    elif status == "UNHEALTHY":
        return (
            "*🌫️ PSI in Singapore 🇸🇬*\n\n"
            # f"Current PSI: *{psi}*\n"
            "Risk Level: *UNHEALTHY*\n\n"
            "Reduce prolonged or outdoor exertion."
        )
    elif status == "VERY UNHEALTHY":
        return (
            "*🌫️ PSI in Singapore 🇸🇬*\n\n"
            # f"Current PSI: *{psi}*\n"
            "Risk Level: *VERY UNHEALTHY*\n\n"
            "Avoid prolonged or outdoor exertion."
        )
    else:
        return (
            "*🌫️ PSI in Singapore 🇸🇬*\n\n"
            # f"Current PSI: *{psi}*\n"
            "Risk Level: *HAZARDOUS*\n\n"
            "Avoid outdoor activities where possible."
        )


def load_previous_status(state_file):
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            return f.read().strip()
    return None


def save_status(state_file, status):
    with open(state_file, "w") as f:
        f.write(status)


async def main():
    bot = Bot(token=TELEGRAM_TOKEN)

    # --- UV Index ---
    uv = fetch_uv()
    current_uv_status = get_uv_status(uv)
    previous_uv_status = load_previous_status(UV_STATE_FILE)

    # Only send when the UV category changes
    if current_uv_status != previous_uv_status:
        # Skip the very first run if UV is LOW
        if not (previous_uv_status is None and current_uv_status == "LOW"):
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=get_uv_message(current_uv_status, uv),
                parse_mode="Markdown",
            )
            print(f"UV notification sent: {current_uv_status}")
    save_status(UV_STATE_FILE, current_uv_status)

    # --- PSI (haze) ---
    psi = fetch_psi()
    current_psi_status = get_psi_status(psi)
    previous_psi_status = load_previous_status(PSI_STATE_FILE)

    # Only send when the PSI category changes
    if current_psi_status != previous_psi_status:
        # Skip the very first run if PSI is GOOD
        if not (previous_psi_status is None and current_psi_status == "GOOD"):
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=get_psi_message(current_psi_status, psi),
                parse_mode="Markdown",
            )
            print(f"PSI notification sent: {current_psi_status}")
    save_status(PSI_STATE_FILE, current_psi_status)


if __name__ == "__main__":
    asyncio.run(main())
