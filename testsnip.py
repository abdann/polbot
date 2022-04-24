# def string_search(defined_triggers: dict, message):
#     reactions = []
#     # First combine message into single string with no spaces and lowercase
#     content = message.content.replace(" ", "").casefold()
#     # now append any positive hits (THIS IS BLOCKING CODE)
#     for trigger, reaction in defined_triggers.items():
#         if content.find(trigger) != -1:
#             reactions.append(reaction)
#     return reactions

# # Testing string_search, made a dummy class
# class Message:
#     def __init__(self) -> None:
#         pass

# message = Message()
# message.content = "hello MODSamonGus are gay among us"
# import os
# import discord
# from discord.ext import commands
# from dotenv import load_dotenv

# load_dotenv()
# TOKEN = os.getenv('DISCORD_TOKEN')
# GUILD = os.getenv('DISCORD_GUILD')

# description = "BING CHILLING"

# intents = discord.Intents.default()
# intents.members = True

# bot = commands.Bot(command_prefix='.pol ', description=description, intents=intents)


# import emoji

# @bot.event
# async def on_message(message):
#     if message.author.id == 731659389550985277:
#         react = discord.utils.get(message.guild.emojis, name="sus")
#         await message.add_reaction(react)
#         await message.reply("AMOGUS")
# bot.run(TOKEN)
parameters = {
    "min_account_age":14
}

import datetime
account_age = datetime.datetime.now() - datetime.datetime(month=1, day=1, year=1)
if account_age.total_seconds() < datetime.timedelta(days=self.bot.parameters["min_account_age"]).total_seconds()
    await member.ban(reason=f'Account age less than {self.bot.parameters["min_account_age"]}')
    return