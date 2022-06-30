from sys import prefix
from typing import Optional
import typing
import emojis
import discord
from discord.ext import commands

class Emoji(commands.Converter):
    """Tries to convert an input emoji into a custom emoji first, and if not found into a default emoji"""
    async def convert(self, ctx, argument):
        try:
            emoji_converter = commands.EmojiConverter()
            custom_emoji = await emoji_converter.convert(ctx, argument)
            return custom_emoji
        except commands.EmojiNotFound:
            return get_default_emoji(argument)

class SayFlags(commands.FlagConverter, delimiter=' ', prefix='-'):
    replyto: discord.Message = commands.flag(name='replyto', default=None)
    text: typing.List[str]

class MarkovFlags(commands.FlagConverter, delimiter=' ', prefix='-'):
    dump: discord.TextChannel = commands.flag(name="dump", default=None)
    limit: int = 5000
    cweight: float = 100
    dweight: float = 1
    tries: int = 100

class TextTriggerFlags(commands.FlagConverter, delimiter=' ', prefix='-'):
    trigger: str
    text: str

def strtobool(string:str):
    """Parses a simple string as 'True' or 'False' """
    if string.casefold() == 'true':
         return True
    elif string.casefold() == 'false':
         return False
    else:
         raise ValueError

colons = [":", ":"]

def get_default_emoji(emoji:str):
    """Converts a default emoji to the literal representation in Unicode"""
    # This case is for an input like this: rainbow_flag
    if emoji.find(":") == -1 and len(emojis.get(emoji)) == 0:
        found_reaction = emojis.db.get_emoji_by_alias(emoji)
        if found_reaction is not None:
            return emojis.encode(emoji.join(colons))
        return None
    # This case is for an input like this: :rainbow_flag:
    elif emoji.find(":") > -1 and len(emojis.get(emoji)) == 0:
        found_reaction = emojis.db.get_emoji_by_alias(emoji.replace(":", ""))
        if found_reaction is not None:
            return emojis.encode(emoji)
        return None
    # This case is for an input like this: 🏳️‍🌈
    else:
        decoded = emojis.decode(emoji)
        found_reaction = emojis.db.get_emoji_by_alias(decoded.replace(":", ""))
        if emoji == found_reaction.emoji:
            return emoji
        return None

def get_emoji(guild, emoji_string:str): #For converting from SQL format to discord.Emoji or Unicode emoji
    """Tries to resolve an input emoji into either a discord.Emoji object or the literal emoji (if it is a default emoji). Raises Error("Not an emoji") if neither case matches"""
    try: # Try to see if it is an ID for an emoji, and retreive the discord.Emoji object from the ID
        emoji = int(emoji_string)
        custom_emoji = discord.utils.get(guild.emojis, id=emoji)
        if custom_emoji is not None:
            return custom_emoji
        else:
            return None
    except ValueError: # Try to interpret it as a default emoji and return the encoded Unicode representation
        return get_default_emoji(emoji_string)

def stringify_emoji(emoji_like) -> str: #For converting from discord.Emoji or Unicode emoji to SQL format
    """Inverse function of get_emoji"""
    if isinstance(emoji_like, discord.Emoji):
        return str(emoji_like.id)
    else:
        return get_default_emoji(emoji_like)

def convert_dict_to_sql_update(dictionary:list):
    """Converts a dictionary of columns and values into an SQLite UPDATE string and a tuple of values from the dict, example: ('key1 = (:key1), key2 = (:key2), ...', {"key1" : value1, "key2" : value2, ...}) """
    columns = ", ".join([f"{key} = :{key}" for key in dictionary])
    return columns

def convert_list_to_sql_select(columns:list):
    """Converts a list of columns to the standard form for SELECT queries, ie: ("column1", "column2", ...) becomes "column1, column2, ..."."""
    return ", ".join(columns)

def convert_dict_to_sql_insert(dictionary:dict):
    """Converts a dictionary of columns and values into an SQLite INSERT string and a tuple of values from the dict, example: ('(key1, key2 ...)', '(:key1, :key2, ...)') """
    keys = "(" + ", ".join(dictionary.keys()) + ")"
    values = "(" + ", ".join([f":{key}" for key in dictionary.keys()]) + ")"
    return (keys, values)

def build_sql_and(column_conditions:list):
    """Builds an AND condition from a list of conditions: ['condition1', 'condition2', ...]"""
    return " AND ".join([f"{key} = :{key}" for key in column_conditions])

# params = {
#     "min_account_age": 14,
#     "new_auto_ban": True,
#     "lockdown": False,
#     "polder_channel_id": None,
#     "polder":False,
#     "random_polder_posts":False,
#     "random_text_posts":False,
#     "shitpost_probability":3
# }
