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

`SHOCK_API` and `SHOCK_ID` is an API token and Shocker ID fetched from [ShockLink](https://shocklink.net/).
To get your Shocker ID, find the shocker you want and click the 3 dots, Edit, then copy the ID.

## Additional parameters (Optional)
`VIBE_STR_MIN` `VIBE_STR_MAX` controls the min-max strength of vibration requests. (Default `25`-`100`)

`VIBE_DUR_MIN` `VIBE_DUR_MAX` controls the min-max duration of vibration requests in milliseconds (Min `300`, Max `30000`) (Default `300`-`1000`)

`VIBE_COOLDOWN` controls the cooldown between permitting vibration requests in seconds. (Default `10`)

`SHOCK_STR_MIN` `SHOCK_STR_MAX` controls the min-max strength of shock requests. (Default `1`-`1`)

`SHOCK_DUR_MIN` `SHOCK_DUR_MAX` controls the min-max duration of shock requests in milliseconds (Min `300`, Max `30000`) (Default `300`-`300`)

`SHOCK_COOLDOWN` controls the cooldown between permitting shock requests in seconds. (Default `60`)

`BLACKLIST` is a list of Telegram profile IDs to block from sending commands, seperated with commas (e.g: `1234567,9876543`) (Default None)

`WHITELIST` controls if the blacklist should be treated as a whitelist instead (`True`/`False`) (Default `False`)

## Commands

(These can be used by anyone not on the blacklist, must be sent as a PM)

`/shock` sends a shock request of varying strength and duration depending on your configuration

`/vibrate` sends a vibrate request of varying strength and duration depending on your configuration

## Notes
Currently the program does not support specifying strength and duration through Telegram, it picks random values from the ranges specified in the environment variables.
