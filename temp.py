# temp.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    
    print(
        f'{client.user} is connected to the following server: \n'
        f'{guild.name}(id: {guild.id})'
        )
    
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.find("mod") != -1:
        emoji = '🏳️‍🌈'
        await message.add_reaction(emoji)
    
    if message.content.find("sus") != -1:
        guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
        emoji = discord.utils.get(guild.emojis, name='sus')
        await message.add_reaction(emoji)
    

client.run(TOKEN)