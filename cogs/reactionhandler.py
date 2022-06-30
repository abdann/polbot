import discord
from discord.ext import commands
import asyncio
import cogs.permissionshandler
import utils

class ReactionHandler(commands.Cog, name='Reaction'):
    """Handles all reaction functions of the bot as well as corresponding commands. Note: The autonomous effects of this category are only observed in allowed shitposting channels"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addemojitrigger", aliases=['addemoji'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def add_emoji_trigger(self, ctx, trigger_phrase:str, emoji:utils.Emoji):
        """[Executive Moderator command] Adds an emoji reaction trigger"""
        if emoji is None:
            raise commands.EmojiNotFound
        if await self.bot.servers.add_emoji_reaction_trigger(ctx.guild, trigger_phrase, emoji):
            await ctx.reply("Emoji reaction trigger added!")
            return
        await ctx.reply("Emoji reaction trigger already present.")

    
    @commands.command(name="removeemojitrigger", aliases=['rmemoji'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def remove_emoji_trigger(self, ctx, trigger_phrase:str, emoji:utils.Emoji):
        """[Executive Moderator command] Removes an emoji reaction trigger"""
        if emoji is None:
            raise commands.EmojiNotFound
        if await self.bot.servers.remove_emoji_reaction_trigger(ctx.guild, trigger_phrase=trigger_phrase, emoji=emoji):
            await ctx.reply("Emoji reaction trigger removed")
            return
        await ctx.reply("Emoji reaction trigger not found.")
        

    @commands.command(name="listemojitriggers", aliases=['listemojis'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.trial_moderator_check)
    async def list_emoji_reaction_triggers(self, ctx):
        """[Moderator command] Lists all registered trigger phrases and the corresponding reaction name"""
        reaction_triggers = await self.bot.servers.get_emoji_reaction_triggers(ctx.guild)
        if len(reaction_triggers) == 0:
            await ctx.reply('No reaction triggers are currently set')
            return
        await ctx.reply('\n'.join([f'{key}: {value}' for key, value in reaction_triggers.items()]))

    @commands.command(name="addtexttrigger", aliases=['addtext'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def add_text_trigger(self, ctx, trigger_phrase:str, text:str):
        """[Executive Moderator command] Adds a text trigger.
        When the trigger phrase is detected, the bot sends a message containing the text."""
        if await self.bot.servers.add_text_trigger(ctx.guild, trigger_phrase, text):
            await ctx.reply("Text trigger added!")
            return
        await ctx.reply("Text trigger is already present.")

    @commands.command(name="removetexttrigger", aliases=['rmtext'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def remove_text_trigger(self, ctx, trigger_phrase:str, text:str):
        """[Executive Moderator command] Removes a text trigger.
        When the trigger phrase is detected, the bot sends a message containing the text."""
        if await self.bot.servers.remove_text_trigger(ctx.guild, trigger_phrase=trigger_phrase, message=text):
            await ctx.reply("Text trigger removed")
            return
        await ctx.reply("Text trigger not found.")

    @commands.command(name="listtexttriggers", aliases=['listtexts'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.trial_moderator_check)
    async def list_text_triggers(self, ctx):
        """[Moderator command] Lists all registered trigger phrases and the corresponding texts to reply with"""
        text_triggers = await self.bot.servers.get_text_triggers(ctx.guild)
        if len(text_triggers) == 0:
            await ctx.reply('No text triggers are currently set')
            return
        await ctx.reply('\n'.join([f'{key}: {value}' for key, value in text_triggers.items()]))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id or message.author.bot:
            return
        
        reactions = await self._string_search(message)
        if reactions is not None:
            await self._listen_reactions(message, reactions[0], reactions[1])

        # # :christmas_troll: poor chaotic :amogus:
        if message.author.id == 731659389550985277:
            sussy = discord.utils.get(message.guild.emojis, name="sus")
            await message.add_reaction(sussy)

    # async def listen_reactions(self, message, react_emojis):
    #     if len(react_emojis) != 0:
    #         coros = [self._coro_react(message, react_emoji) for react_emoji in react_emojis]
    #         await asyncio.gather(*coros)
    
    async def _listen_reactions(self, message, reactions_to_add, messages_to_send):
        if len(reactions_to_add) != 0:
            reactions_to_add = [self._coro_react(message, react_emoji) for react_emoji in reactions_to_add]
            await asyncio.gather(*reactions_to_add)
        if len(messages_to_send) != 0:
            messages_to_send = [self._coro_send_text(message, text) for text in messages_to_send]
            await asyncio.gather(*messages_to_send)

    async def _coro_react(self, message, react_emoji):
        await message.add_reaction(react_emoji)

    async def _coro_send_text(self, message, text):
        await message.channel.send(text)

    async def _string_search(self, message):
        """Searches a string for trigger phrases. Returns a tuple of lists, where the first is the list of reactions to add and the second is the list of messages to send"""
        if await self.bot.servers.find_in_shitposting_channels(message.guild, message.channel.id):
            content = message.content.casefold()
            reaction_triggers = await self.bot.servers.get_emoji_reaction_triggers(message.guild)
            reactions_to_add = [reaction for trigger_phrase, reaction in reaction_triggers.items() if trigger_phrase in content]
            text_triggers = await self.bot.servers.get_text_triggers(message.guild)
            messages_to_send = [text_to_send for trigger_phrase, text_to_send in text_triggers.items() if trigger_phrase in content]
            return (reactions_to_add, messages_to_send)
        else:
            return None