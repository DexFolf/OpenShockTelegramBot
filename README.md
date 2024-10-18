# OpenShock Telegram Bot

A simple python script to allow control of OpenShock devices from Telegram commands via POST requests.

Tested on Python 3.12.1 on Windows.

## [Download](https://github.com/DexFolf/OpenShockTelegramBot/releases/latest)

## Requirements
[Python3](https://www.python.org/downloads/)

[telethon](https://pypi.org/project/Telethon/)
[requests](https://pypi.org/project/requests/)
[python-dotenv](https://pypi.org/project/python-dotenv/)
(or alternatively, run `pip install -r requirements.txt`)

## Configuration
Set environment variables via the .env file or through your terminal.

`API_ID` and `API_HASH` is from your Telegram application (my.telegram.org)

`SHOCK_API` and `SHOCK_ID` is an API token and Shocker ID fetched from [ShockLink](https://openshock.app/).
To get your Shocker ID, find the shocker you want and click the 3 dots, Edit, then copy the ID.

## Additional parameters (Optional)
`SOUND_ALLOWED` `VIBE_ALLOWED` `SHOCK_ALLOWED` controls if the bot permits usage of the respective command. (Default `True`)

`SOUND_STR_MIN` `SOUND_STR_MAX` controls the min-max strength of beep requests. *Seems to have no effect.* (Default `0`-`100`)

`SOUND_DUR_MIN` `SOUND_DUR_MAX` controls the min-max duration of beep requests in milliseconds (Min `300`, Max `30000`) (Default `300`-`1000`)

`SOUND_COOLDOWN` controls the cooldown between permitting beep requests in seconds. (Default `10`)

`VIBE_STR_MIN` `VIBE_STR_MAX` controls the min-max strength of vibration requests. (Default `25`-`100`)

`VIBE_DUR_MIN` `VIBE_DUR_MAX` controls the min-max duration of vibration requests in milliseconds (Min `300`, Max `30000`) (Default `300`-`1000`)

`VIBE_COOLDOWN` controls the cooldown between permitting vibration requests in seconds. (Default `10`)

`SHOCK_STR_MIN` `SHOCK_STR_MAX` controls the min-max strength of shock requests. (Default `1`-`1`)

`SHOCK_DUR_MIN` `SHOCK_DUR_MAX` controls the min-max duration of shock requests in milliseconds (Min `300`, Max `30000`) (Default `300`-`300`)

`SHOCK_COOLDOWN` controls the cooldown between permitting shock requests in seconds. (Default `60`)

`BLACKLIST` is a list of Telegram profile IDs to block from sending commands, seperated with commas (e.g: `1234567,9876543`) (Default None)

`WHITELIST` controls if the blacklist should be treated as a whitelist instead. (Default `False`)

`OWNER_ID` will make the bot send successful command notices to a specified account. Will always be printed in console regardless. (Default None)

Not sure what your Telegram user ID is? Message a bot like [userinfobot](https://t.me/userinfobot) to find out. (Not affiliated with this project)

## Usage

The bot can be run by running `shockbot.py` in Python.
Windows users can also just use the .exe provided in the [Releases](https://github.com/DexFolf/OpenShockTelegramBot/releases).
Press Ctrl+C in the terminal at any point to stop the bot.

Upon launching the bot for the first time, you will be prompted to enter a phone number or bot token. Either enter your full phone number (including area code) or a bot token acquired from [Bot Father](https://t.me/BotFather)

If everything goes well, your account name and ID will show up signifying the bot is running correctly. Commands can then be sent to that account within Telegram itself to control your shocker.

If you wish to use another account, simply delete the `anon.session` file while the bot isn't running, or terminate the session through the Telegram app.

## Commands

(These can be used by anyone not on the blacklist, must be sent as a PM)

`/sound <strength> <duration>` sends a sound request of a given strength and duration. Strength can be any number, as it doesn't make a difference in my experience.

`/shock <strength> <duration>` sends a shock request of a given strength and duration.

`/vibrate <strength> <duration>` sends a vibrate request of a given strength and duration.