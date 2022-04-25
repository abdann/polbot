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
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

description = "BING CHILLING"

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='.pol ', description=description, intents=intents)

# @bot.event
# async def on_message(message):
#     if message.author.id == 731659389550985277:
#         react = discord.utils.get(message.guild.emojis, name="sus")
#         await message.add_reaction(react)
#         await message.reply("AMOGUS")

bot_owner_role_name = "PolBot's Dad"
def owner_check(ctx):
        """Checks if a command invoker is the owner"""
        return True if (bot_owner_role_name in [role.name for role in ctx.message.author.roles]) else False

@bot.command(name="stop")
@bot.check(owner_check)
async def stop(ctx):
    await ctx.reply("Attempting shutdown")
    await bot.close()
bot.run(TOKEN)
# import emojis

# # intended possible inputs to handle
# reaction = "rainbow_flag"
# reaction2 = ":rainbow_flag:"
# reaction3 = "🏳️‍🌈"
# reaction4 = ":sus:"
# reaction5 = "sus"

# def is_default_emoji(reaction):
#     # This case is for an input like this: rainbow_flag
#     if reaction.find(":") == -1 and len(emojis.get(reaction)) == 0:
#         found_reaction = emojis.db.get_emoji_by_alias(reaction)
#         if found_reaction is not None:
#             return (True, emojis.encode(":" + reaction + ":"))
#         return False
#     # This case is for an input like this: :rainbow_flag:
#     elif reaction.find(":") > -1 and len(emojis.get(reaction)) == 0:
#         found_reaction = emojis.db.get_emoji_by_alias(reaction.replace(":", ""))
#         if found_reaction is not None:
#             return (True, emojis.encode(reaction))
#         return False
#     # This case is for an input like this: 🏳️‍🌈
#     else:
#         decoded = emojis.decode(reaction)
#         found_reaction = emojis.db.get_emoji_by_alias(decoded.replace(":", ""))
#         if reaction == found_reaction.emoji:
#             return (True, reaction)
#         return False

# print(is_default_emoji(reaction))
# print(is_default_emoji(reaction2))
# print(is_default_emoji(reaction3))
# print(is_default_emoji(reaction4))
# print(is_default_emoji(reaction5))