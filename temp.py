# temp.py
import os

import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

description = "BING CHILLING"

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='.pol', description=description, intents=intents)

@bot.event
async def on_ready():
    guild = nextcord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    
    print(
        f'{bot.user} is connected to the following server: \n'
        f'{guild.name}(id: {guild.id})'
        )
    

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.find("mod") != -1:
        emoji = '🏳️‍🌈'
        await message.add_reaction(emoji)
    
    if message.content.find("sus") != -1:
        guild = nextcord.utils.find(lambda g: g.name == GUILD, client.guilds)
        emoji = nextcord.utils.get(guild.emojis, name='sus')
        await message.add_reaction(emoji)
    
    react_emojis = string_search()
    if len(react_emojis) != 0:
        


# tested in testsnip.py
# Search a message for any substrings present, and if found, return the corresponding emojis to react
def string_search(defined_triggers: dict, message):
    reactions = []
    # First combine message into single string with no spaces
    content = message.content.replace(" ", "")
    # Now iterate through trigger list and add positive hits to the list reactions
    for trigger, reaction in defined_triggers:
        if content.find(trigger) != -1:
            reactions.append(reaction)
    return reactions


client.run(TOKEN)