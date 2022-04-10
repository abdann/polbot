"""This file contains functions that implement bot
 commands to add/remove trigger words and emojis
  as well as report errors"""

import discord
import json
from client import client


command_prefix = 



# listen for a message and see if it contains the command prefix
@client.event
async def on_message(message):
    if message.content.startswith()