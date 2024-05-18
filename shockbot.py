from telethon import TelegramClient, events
import asyncio
import logging
from datetime import datetime, timedelta
import requests
import re
import os
import random
from dotenv import load_dotenv
logging.basicConfig(level=logging.ERROR)
load_dotenv()

# Get your own values from https://my.telegram.org
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')

# Visit https://shocklink.net/#/dashboard/tokens
# Make a new token and copy the API key 
SHOCK_API = os.environ.get('SHOCK_API')

# Visit https://shocklink.net/#/dashboard/shockers/own
# Click on 'Edit' and copy the ID
SHOCK_ID = os.environ.get('SHOCK_ID')

# Check if stuff is set
if None in [API_ID,API_HASH,SHOCK_API,SHOCK_ID]:
    print('ERROR: A required environment variable hasn\'t been set! Check the README!')
    exit()

# Create a Telegram client
client = TelegramClient('anon', API_ID, API_HASH)

# User preferences
VIBE_STR_MIN = int(os.environ.get('VIBE_STR_MIN', '25'))
VIBE_STR_MAX = int(os.environ.get('VIBE_STR_MAX', '100'))
VIBE_DUR_MIN = int(os.environ.get('VIBE_DUR_MIN', '300'))
VIBE_DUR_MAX = int(os.environ.get('VIBE_DUR_MAX', '1000'))
VIBE_COOLDOWN = int(os.environ.get('VIBE_COOLDOWN', '10'))
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


# API endpoint, view more at https://api.shocklink.net/swagger/index.html (select a definition on the top right)
url = 'https://api.shocklink.net/2/shockers/control'
# Authenticate with OpenShock
headers = {'accept': 'application/json', 'OpenShockToken': SHOCK_API, 'Content-Type': 'application/json'}

# Initialise shock cooldowns (available immediately when bot started)
next_shock = datetime.now()
next_vibe = datetime.now()

# On new message received that starts with "/"
@client.on(events.NewMessage(pattern='^/.+'))
async def main(event):
    global next_shock
    global next_vibe
    
    # Is it a PM?
    if event.is_private:
    
        # Is the message is a valid command?
        if event.raw_text.lower() == '/shock' or event.raw_text.lower() == '/vibrate':
        
            # Fetches the user, checks if they are not on the blacklist (or are on the whitelist if in whitelist mode)
            sender = await client.get_entity(event.sender_id)
            if (event.sender_id not in blacklisted_ids and not WHITELIST) or (event.sender_id in blacklisted_ids and WHITELIST):
            
                # Was it a shock command?
                if event.raw_text.lower() == '/shock':
                
                    # If enough time has passed since last shock
                    if datetime.now() > next_shock:
                        print('Shock request received from {} ({})'.format(sender.first_name,event.sender_id))
                    
                        # Disable shocking for SHOCK_COOLDOWN seconds
                        next_shock = datetime.now() + timedelta(seconds=SHOCK_COOLDOWN)
                        
                        # Message to send to the API, choses a random strength and duration
                        payload = {'shocks': [{'id': SHOCK_ID, 'type': 'Shock', 'intensity': random.randint(SHOCK_STR_MIN,SHOCK_STR_MAX), 'duration': random.randint(SHOCK_DUR_MIN,SHOCK_DUR_MAX), 'exclusive': True}], 'customName': 'string'}
                        
                        # Send the request and save the response
                        response = requests.post(url=url,headers=headers,json=payload)
                        
                        # If everything went okay, reply with success
                        if response.status_code == 200:
                            await event.reply('(OpenShock) Shock sent successfully.')
                        print(response.content)
                        
                    # If not enough time has passed, say how long is left
                    else:
                        print('Shock request from {} ({}) denied due to cooldown.'.format(sender.first_name,event.sender_id))
                        await event.reply('(OpenShock) Next shock available in '+str((next_shock-datetime.now()).seconds)+' seconds.')
                
                
                # Repeated code but for vibrations (TODO: Turn into a function so less code is repeated)
                if event.raw_text.lower() == '/vibrate':
                    if datetime.now() > next_vibe:
                        print('Vibration request received from {} ({})'.format(sender.first_name,event.sender_id))
                        next_vibe = datetime.now() + timedelta(seconds=VIBE_COOLDOWN)
                        payload = {'shocks': [{'id': SHOCK_ID, 'type': 'Vibrate', 'intensity': random.randint(VIBE_STR_MIN,VIBE_STR_MAX), 'duration': random.randint(VIBE_DUR_MIN,VIBE_DUR_MAX), 'exclusive': True}], 'customName': 'string'}
                        response = requests.post(url=url,headers=headers,json=payload)
                        if response.status_code == 200:
                            await event.reply('(OpenShock) Vibration sent successfully.')
                        print(response.content)
                    else:
                        print('Vibration request from {} ({}) denied due to cooldown.'.format(sender.first_name,event.sender_id))
                        await event.reply('(OpenShock) Next vibration available in '+str((next_vibe-datetime.now()).seconds)+' seconds.')
            
            # User that sent the request was denied, print in console.
            else:
                print('Command received from {} ({}) but was ignored due to your settings.'.format(sender.first_name,event.sender_id))

# Message to let you know the bot is working
async def welcome_msg():
    me = await client.get_me()
    print('Python script running as {} ({})'.format(me.first_name,me.id))

# Run the bot
client.start()
client.loop.run_until_complete(welcome_msg())
client.run_until_disconnected()