from telethon import TelegramClient, events
import logging
from datetime import datetime, timedelta
import requests
import re
import os
from sys import exit
from dotenv import load_dotenv
logging.basicConfig(level=logging.ERROR)
load_dotenv()

# Telegram API Keys
# Get your own values from https://my.telegram.org
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')

# OpenShock API Key
# Visit https://openshock.app/#/dashboard/tokens
# Make a new token and copy the API key 
SHOCK_API = os.environ.get('SHOCK_API')

# OpenShock Shock Collar ID
# Visit https://openshock.app/#/dashboard/shockers/own
# Click on 'Edit' and copy the ID
SHOCK_ID = os.environ.get('SHOCK_ID')

# Check if required variables are set
if None in [API_ID,API_HASH,SHOCK_API,SHOCK_ID]:
    print('ERROR: A required environment variable hasn\'t been set! Check the README!')
    exit(1)

# Create a Telegram client
client = TelegramClient('anon', API_ID, API_HASH)

# User preferences
SOUND_ALLOWED = os.environ.get('SOUND_ALLOWED', 'true').lower() == 'true'
SOUND_STR_MIN = int(os.environ.get('SOUND_STR_MIN', '0'))
SOUND_STR_MAX = int(os.environ.get('SOUND_STR_MAX', '100'))
SOUND_DUR_MIN = int(os.environ.get('SOUND_DUR_MIN', '300'))
SOUND_DUR_MAX = int(os.environ.get('SOUND_DUR_MAX', '1000'))
SOUND_COOLDOWN = int(os.environ.get('SOUND_COOLDOWN', '10'))

VIBE_ALLOWED = os.environ.get('VIBE_ALLOWED', 'true').lower() == 'true'
VIBE_STR_MIN = int(os.environ.get('VIBE_STR_MIN', '25'))
VIBE_STR_MAX = int(os.environ.get('VIBE_STR_MAX', '100'))
VIBE_DUR_MIN = int(os.environ.get('VIBE_DUR_MIN', '300'))
VIBE_DUR_MAX = int(os.environ.get('VIBE_DUR_MAX', '1000'))
VIBE_COOLDOWN = int(os.environ.get('VIBE_COOLDOWN', '10'))

SHOCK_ALLOWED = os.environ.get('SHOCK_ALLOWED', 'true').lower() == 'true'
SHOCK_STR_MIN = int(os.environ.get('SHOCK_STR_MIN', '1'))
SHOCK_STR_MAX = int(os.environ.get('SHOCK_STR_MAX', '1'))
SHOCK_DUR_MIN = int(os.environ.get('SHOCK_DUR_MIN', '300'))
SHOCK_DUR_MAX = int(os.environ.get('SHOCK_DUR_MAX', '300'))
SHOCK_COOLDOWN = int(os.environ.get('SHOCK_COOLDOWN', '60'))

BLACKLIST = os.environ.get('BLACKLIST', '')
blacklisted_ids = re.findall('-?\\d+',BLACKLIST)
blacklisted_ids = [int(x) for x in blacklisted_ids]

WHITELIST = os.environ.get('WHITELIST', 'false')
WHITELIST = WHITELIST.lower() == 'true'

OWNER_ID = int(os.environ.get('OWNER_ID', 0))
device = None

# OpenShock API endpoints
# View more at https://api.openshock.app/swagger/index.html (select a definition on the top right)
urls = {
    'shock': 'https://api.openshock.app/2/shockers/control', # (POST) Controls shockers
    'shock_status': 'https://api.openshock.app/1/shockers/', # (GET) Returns info about a shocker, including the device that controls it
    'device_status' : ['https://api.openshock.app/1/devices/','/lcg'] # (GET) Returns info about a device, including the online status
}

# Message header that will authenticate with OpenShock when sending requests
headers = {
    'accept': 'application/json',
    'OpenShockToken': SHOCK_API,
    'Content-Type': 'application/json'
}

# Initialise cooldowns (available immediately when bot started)
cooldowns = {
    'Sound': datetime.now(),
    'Vibrate': datetime.now(),
    'Shock': datetime.now()
}

# Friendly names for actions
action_friendly = {
    'Sound': 'beeped your shocker',
    'Vibrate': 'vibrated your shocker',
    'Shock': 'shocked you'
}

# Store permitted actions to look up later
actions_permitted = {
    'Sound': SOUND_ALLOWED,
    'Vibrate': VIBE_ALLOWED,
    'Shock': SHOCK_ALLOWED
}

# Define a general usage string
USAGE = f'''Usage: /shock|vibrate|sound <strength> <duration>
Shocks: **{SHOCK_STR_MIN}** - **{SHOCK_STR_MAX}**% strength for **{SHOCK_DUR_MIN / 1000}** - **{SHOCK_DUR_MAX / 1000}**s
Vibrations: **{VIBE_STR_MIN}** - **{VIBE_STR_MAX}**% strength for **{VIBE_DUR_MIN / 1000}** - **{VIBE_DUR_MAX / 1000}**s
Sounds: **{SOUND_STR_MIN}** - **{SOUND_STR_MAX}**% strength for **{SOUND_DUR_MIN / 1000}** - **{SOUND_DUR_MAX / 1000}**s'''

# This function checks if the shocker controller is online
async def checkOnline(SHOCK_API,SHOCK_ID):
    global device
    print(f'{neatTime()} | Checking if your shocker can be reached...')

    # Send a request to get shocker info
    if device is None:
        response = requests.get(url = urls['shock_status']+SHOCK_ID, headers = headers)
        if response.status_code == 200:
            try:
                device = response.json()['data']['device']
            except:
                print(f'{neatTime()} | Something went wrong when trying to fetch the device ID of your shocker:\n{response.content}')
                exit(1)
        else:
            print(f'{neatTime()} | An error occured when trying to check your shocker ID:\n{response.content}')
            exit(1)
        
    # Fetch the online status of the device that controls your shocker
    response = requests.get(url = urls['device_status'][0]+device+urls['device_status'][1], headers = headers)
    if response.status_code == 200:
        print(f'{neatTime()} | Hooray! Your shocker is online and functional!')
        return True
    elif response.status_code == 404:
        if response.json()['type'] == 'Device.NotOnline':
            errormsg = 'WARNING: OpenShock reports the device your shocker is paired to is currently offline. The bot will continue to run, but you should probably get that checked out.'
            print(f'{neatTime()} | {errormsg}')
            await logToOwner(errormsg)
            return False
        else:
            print(f'{neatTime()} | An error occured when trying to check your shock controller:\n{response.content}')
            exit(1)


# This function returns the current time in a neater format
def neatTime():
    return datetime.now().strftime('%H:%M:%S')

# This function clamps supplied values to a specified range
def clamp(min_val, max_val, default_val):
    return max(min_val, min(default_val, max_val))

# This function handles logging messages to the owner if an ID is set
async def logToOwner(msgtosend):
    if owner is not None:
        await client.send_message(owner.id, f'{msg_prefix}{msgtosend}')

# This function checks if a user is allowed to use commands
def is_allowed(event):
    return (event.sender_id not in blacklisted_ids and not WHITELIST) or (event.sender_id in blacklisted_ids and WHITELIST)

# This function handles the three actions
async def command(event, sender, cmd):
    global cooldowns

    # Get action and its parameters from the command args
    action = cmd[0].split('/')[1].capitalize()
    action_strength = cmd[1]
    action_length = int(cmd[2] * 1000)

    # Determine the correct length and strength depending on the type of the action
    match action:
        case 'Beep' | 'Sound':
            action_strength = clamp(SOUND_STR_MIN, SOUND_STR_MAX, action_strength)
            action_length = clamp(SOUND_DUR_MIN, SOUND_DUR_MAX, action_length)
            action_cooldown = SOUND_COOLDOWN
            action = 'Sound'
        case 'Vibrate' | 'Vibe':
            action_strength = clamp(VIBE_STR_MIN, VIBE_STR_MAX, action_strength)
            action_length = clamp(VIBE_DUR_MIN, VIBE_DUR_MAX, action_length)
            action_cooldown = VIBE_COOLDOWN
            action = 'Vibrate'
        case 'Shock' | 'Zap':
            action_strength = clamp(SHOCK_STR_MIN, SHOCK_STR_MAX, action_strength)
            action_length = clamp(SHOCK_DUR_MIN, SHOCK_DUR_MAX, action_length)
            action_cooldown = SHOCK_COOLDOWN
            action = 'Shock'

    # Is the action permitted in your config
    if actions_permitted[action]:

        # If enough time has passed since last action
        if datetime.now() > cooldowns[action]:
            print(f'{neatTime()} | {action} request received from {sender.first_name} ({event.sender_id})')
        
            # Disable action for <action>_COOLDOWN seconds
            cooldowns[action] = datetime.now() + timedelta(seconds = action_cooldown)
            
            # Message to send to the API
            payload = {
                'shocks': [{
                    'id': SHOCK_ID,
                    'type': action,
                    'intensity': action_strength,
                    'duration': action_length, 
                    'exclusive': True
                }],
                # Message that will show up in Logs and OSC
                'customName': 'Telegram'}
            
            # Send the request and save the response
            response = requests.post(url = urls['shock'], headers = headers, json = payload)
            
            print(f'{neatTime()} | {response.content}; {action} at {action_strength}% for {action_length / 1000}s')
            # If everything went okay, reply with success
            if response.status_code == 200:
                await event.reply(f'{msg_prefix}{action} sent successfully.')
                action_verb = action_friendly[action]
                await logToOwner(f'{sender.first_name} ({event.sender_id}) just {action_verb} at {action_strength}% for {action_length / 1000}s')
            else:
                await event.reply(f'Something went wrong.')
                await logToOwner(f'An error occured: {response.status_code} {response.json()['message']}')
            
        # If not enough time has passed, say how long is left
        else:
            print(f'{neatTime()} | {action} request from {sender.first_name} ({event.sender_id}) denied due to cooldown.')
            await event.reply(f'{msg_prefix}Next {action.lower()} available in {str((cooldowns[action] - datetime.now()).seconds)} second(s).')
    else:
        print(f'{neatTime()} | {action} request from {sender.first_name} ({event.sender_id}) denied due to being disabled.')
        await event.reply(f'{msg_prefix}Sorry, that action is disabled.')


# On new message received that starts with "/"
@client.on(events.NewMessage(pattern='^/.+'))
async def main(event):
    # Is it a PM?
    if event.is_private:
        # Split arguments by space to a list
        cmd = event.raw_text.lower().split(' ')

        # Try to convert the strength and duration arguments to numbers from string, if missing, set them to 0
        try:
            # Use regex to strip away anything that isn't a number
            cmd[1] = int(re.search('[0-9]*',cmd[1])[0])
            cmd[2] = float(re.search('[0-9]*[.]?[0-9]*',cmd[2])[0])
        except IndexError:
            cmd.extend([0, 0])
        # Reply with the usage if the arguments are not numbers
        except ValueError:
            if is_allowed(event):
                await event.reply(f'{msg_prefix}The supplied arguments are not numbers. {USAGE}')
            return
        
        sender = await event.get_sender() #client.get_entity(event.sender_id) will fail on first interaction from a user, so this is used instead

        if is_allowed(event):
            # Handle individual commands
            # Only responds to certain commands if running as a bot account to avoid potentially conflicting with a selfbot
            match cmd[0]:
                case '/beep' | '/sound' | '/vibrate' | '/vibe' | '/shock' | '/zap':
                    await command(event, sender, cmd)
                case '/help' | '/start':
                    if not (cmd[0] == '/start' and not me.bot):
                        await event.reply(f'{msg_prefix}{USAGE}')
                        print(f'{neatTime()} | {sender.first_name} ({event.sender_id}) used the {cmd[0]} command.')
                case _ if me.bot:
                    await event.reply(f'{msg_prefix}Unknown command. {USAGE}')
                    print(f'{neatTime()} | Unknown command sent by {sender.first_name} ({event.sender_id})')
        else:
            print(f'{neatTime()} | Disallowed user {sender.first_name} ({event.sender_id}) tried to use {cmd[0]}!')
            return

# Messages to let you know the bot is working
async def welcome_msg():
    global me
    global owner
    global msg_prefix

    nolog_msg = 'Messages will only be printed to console.'
    
    # Fetch the current account info
    me = await client.get_me()
    # Now that we know who we are, determine if we need a prefix for every message
    if not me.bot:
        msg_prefix = '**(OpenShock)** '
    else:
        msg_prefix = ''
    
    print(f'{neatTime()} | Python script running as {me.first_name} ({me.id})')

    # Let you know if logging messages will be sent, and to whom
    if OWNER_ID != 0:
        owner = await client.get_entity(OWNER_ID)
        # Double check that this isn't a bot messaging a bot, Telegram doesn't like that.
        if not me.bot or not owner.bot:
            print(f'{neatTime()} | Messages will be sent to {owner.first_name} ({owner.id})')
        else:
            print(f'{neatTime()} | Telegram disallows bots messaging bots. {nolog_msg}')
            owner = None
    else:
        print(f'{neatTime()} | No Owner ID specified. {nolog_msg}')
        owner = None

    # Check if your specified shocker can actually be reached then announce that the bot is ready
    await checkOnline(SHOCK_API,SHOCK_ID)
    await logToOwner('Bot Ready!')

# Run the bot
client.start()
client.loop.run_until_complete(welcome_msg())
client.run_until_disconnected()
