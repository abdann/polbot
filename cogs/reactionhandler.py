import discord
from discord.ext import commands
import asyncio
import typing
import datetime

import cogs.permissionshandler
import utils

class ReactionHandler(commands.Cog, name='Reaction'):
    """Handles all reaction functions of the bot as well as corresponding commands. Note: The autonomous effects of this category are only observed in allowed shitposting channels"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addemojitrigger", aliases=['addemoji'])
    @commands.check(cogs.permissionshandler.staff_check)
    async def add_emoji_trigger(self, ctx, trigger_phrase:str, emoji:utils.Emoji):
        """Adds an emoji reaction trigger"""
        if emoji is None:
            raise commands.EmojiNotFound
        if await self.bot.servers.add_emoji_reaction_trigger(ctx.guild, trigger_phrase, emoji):
            await ctx.reply("Emoji reaction trigger added!")
            return
        await ctx.reply("Emoji reaction trigger already present.")

    
    @commands.command(name="removeemojitrigger", aliases=['rmemoji'])
    @commands.check(cogs.permissionshandler.staff_check)
    async def remove_emoji_trigger(self, ctx, trigger_phrase:str, emoji:utils.Emoji):
        """Removes an emoji reaction trigger"""
        if emoji is None:
            raise commands.EmojiNotFound
        if await self.bot.servers.remove_emoji_reaction_trigger(ctx.guild, trigger_phrase=trigger_phrase, emoji=emoji):
            await ctx.reply("Emoji reaction trigger removed")
            return
        await ctx.reply("Emoji reaction trigger not found.")
        

    @commands.command(name="listemojitriggers", aliases=['listemojis'])
    @commands.check(cogs.permissionshandler.staff_check)
    async def list_emoji_reaction_triggers(self, ctx):
        """Lists all registered trigger phrases and the corresponding reaction name"""
        reaction_triggers = await self.bot.servers.get_emoji_reaction_triggers(ctx.guild)
        if len(reaction_triggers) == 0:
            await ctx.reply('No reaction triggers are currently set')
            return
        await ctx.reply('\n'.join([f'{key}: {value}' for key, value in reaction_triggers.items()]))

    @commands.command(name="addtexttrigger", aliases=['addtext'])
    @commands.check(cogs.permissionshandler.staff_check)
    async def add_text_trigger(self, ctx, *, flags: utils.TextTriggerFlags):
        """Adds a text trigger.
        When the trigger phrase is detected, the bot sends a message containing the text.
        
        valid flags:
        -trigger: Required; The trigger phrase to respond to.
        -text: Required; The text to send.
        """
        if await self.bot.servers.add_text_trigger(ctx.guild, flags.trigger.casefold(), flags.text):
            await ctx.reply("Text trigger added!")
            return
        await ctx.reply("Text trigger is already present.")

    @commands.command(name="removetexttrigger", aliases=['rmtext'])
    @commands.check(cogs.permissionshandler.staff_check)
    async def remove_text_trigger(self, ctx, *, flags: utils.TextTriggerFlags):
        """Removes a text trigger.
        When the trigger phrase is detected, the bot sends a message containing the text.
        
        valid flags:
        -trigger: Required; The trigger phrase to respond to.
        -text: Required; The text to send.
        """
        
        if await self.bot.servers.remove_text_trigger(ctx.guild, trigger_phrase=flags.trigger.casefold(), message=flags.text):
            await ctx.reply("Text trigger removed")
            return
        await ctx.reply("Text trigger not found.")

    @commands.command(name="listtexttriggers", aliases=['listtexts'])
    @commands.check(cogs.permissionshandler.staff_check)
    async def list_text_triggers(self, ctx):
        """Lists all registered trigger phrases and the corresponding texts to reply with"""
        text_triggers = await self.bot.servers.get_text_triggers(ctx.guild)
        if len(text_triggers) == 0:
            await ctx.reply('No text triggers are currently set')
            return
        await ctx.reply('\n'.join([f'{key}: {value}' for key, value in text_triggers.items()]))

    @commands.command(name="cleartexttriggers", aliases=['clearalltexts'])
    @commands.check(cogs.permissionshandler.staff_check)
    async def clear_text_triggers(self, ctx):
        """Clears all currently set text triggers. This is irreversible."""
        async with ctx.channel.typing():
            text_triggers = await self.bot.servers.get_text_triggers(ctx.guild)
            for trigger_phrase, text in text_triggers.items():
                await self.bot.servers.remove_text_trigger(ctx.guild, trigger_phrase=trigger_phrase.casefold(), message=text)
        await ctx.reply("All text triggers have been removed.")
    
    @commands.command(name="settexttriggercooldown", aliases=['settextcooldown'])
    @commands.check(cogs.permissionshandler.staff_check)
    async def set_text_trigger_cooldown(self, ctx:commands.Context, interval: utils.TimeDelta):
        """Set a cooldown on the automatic text trigger functionality of the bot. Text triggers are ignored during cooldown periods. This is server wide and not channel specific.
        
        This command takes one argument, an interval, which is specified as so: 5w4d3h2m1s. This equates to an interval of 5 weeks, 4 days, 3 hours, 2 minutes, and 1 second. Default interval is 0 seconds (ie: no cooldown)"""
        interval:datetime.timedelta = interval
        await self.bot.servers.update_server_parameters(ctx.guild, random_text_trigger_cooldown=interval.total_seconds())
        await ctx.reply(f"Set the text trigger cooldown to {interval}")

    @commands.command(name="gettexttriggercooldown", aliases=['texttriggercooldown?', 'textcooldown?', 'gettextcooldown'])
    @commands.check(cogs.permissionshandler.staff_check)
    async def get_text_trigger_cooldown(self, ctx:commands.Context):
        """Gets the cooldown on the automatic text trigger functionality of the bot. Text triggers are ignored during cooldown periods. This is server wide and not channel specific."""
        cooldown:typing.Dict[str, typing.Union[float, None]] = await self.bot.servers.get_server_parameters(ctx.guild, "random_text_trigger_cooldown")
        if cooldown.get("random_text_trigger_cooldown") is None:
            await self.bot.servers.update_server_parameters(ctx.guild, random_text_trigger_cooldown=self.bot.servers.default_parameters.get("random_text_trigger_cooldown"))
            await ctx.reply(f"Text trigger cooldown `days, HH:MM:SS.MS`: {datetime.timedelta(seconds=self.bot.servers.default_parameters.get('random_text_trigger_cooldown'))}")
            return
        cooldown:float = cooldown.get("random_text_trigger_cooldown")
        cooldown:datetime.timedelta = datetime.timedelta(seconds=cooldown)
        await ctx.reply(f"Text trigger cooldown `days, HH:MM:SS.MS`: {cooldown}")

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.author.id == self.bot.user.id or message.author.bot:
            return
        
        reactions = await self._string_search(message)
        if reactions is not None:
            await self._listen_reactions(message, reactions[0], reactions[1])

        # # # :christmas_troll: poor chaotic :amogus:
        # if message.author.id == 731659389550985277:
        #     sussy = discord.utils.get(message.guild.emojis, name="sus")
        #     await message.add_reaction(sussy)
    
    async def _listen_reactions(self, message, reactions_to_add, messages_to_send):
        if len(reactions_to_add) != 0:
            reactions_to_add = [self._coro_react(message, react_emoji) for react_emoji in reactions_to_add]
            await asyncio.gather(*reactions_to_add)
        if len(messages_to_send) != 0:
            messages_to_send = [self._coro_send_text(message, text) for text in messages_to_send]
            self.bot.servers.text_cooldown.update({str(message.guild.id) : datetime.datetime.now()})
            await asyncio.gather(*messages_to_send)

    async def _coro_react(self, message, react_emoji):
        await message.add_reaction(react_emoji)

    async def _coro_send_text(self, message, text):
        await message.channel.send(text)

    async def _string_search(self, message:discord.Message) -> typing.Union[typing.Tuple[typing.Union[typing.List[utils.Emoji], typing.List], typing.Union[typing.List[str], typing.List]], None]:
        """Searches a string for trigger phrases. Returns a tuple of lists, where the first is the list of reactions to add and the second is the list of messages to send"""
        if await self.bot.servers.find_in_shitposting_channels(message.guild, message.channel.id):
            reaction_triggers:typing.Dict[str, utils.Emoji] = await self.bot.servers.get_emoji_reaction_triggers(message.guild)
            reactions_to_add:typing.List[utils.Emoji] = [reaction for trigger_phrase, reaction in reaction_triggers.items() if trigger_phrase in message.content]
            cooldown:typing.Dict[str, float] = await self.bot.servers.get_server_parameters(message.guild, "random_text_trigger_cooldown")
            cooldown:datetime.timedelta = datetime.timedelta(seconds=cooldown.get("random_text_trigger_cooldown"))
            last_trigger:typing.Union[datetime.datetime, None] = self.bot.servers.text_cooldown.get(str(message.guild.id))
            if last_trigger is not None:
                if datetime.datetime.now() - last_trigger < cooldown:
                    return (reactions_to_add, list())
            text_triggers:typing.Dict[str, str] = await self.bot.servers.get_text_triggers(message.guild)
            messages_to_send:typing.List[str] = [text_to_send for trigger_phrase, text_to_send in text_triggers.items() if trigger_phrase in message.content]
            return (reactions_to_add, messages_to_send)
        else:
            return None