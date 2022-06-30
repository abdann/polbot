import discord
from discord.ext import commands
import asyncio
import cogs.permissionshandler
import utils

class ReactionHandler(commands.Cog, name='Reaction'):
    """Handles all reaction functions of the bot as well as corresponding commands"""
    def __init__(self, bot):
        self.bot = bot

    # #Decorators indicate that it is a command and you must have at least a role to use
    # @commands.command(name="addcustomemojireactiontrigger", aliases=['addcustomrt'])
    # @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    # async def add_custom_reaction_trigger(self, ctx, triggerphrase, reaction: discord.Emoji):
    #     """[Executive Moderator command] Command to add a reaction triggerword. Requires a trigger phrase and a valid reaction present on the server"""
        
    #     # Some checking code to make sure that the info hasn't been added already
    #     reaction_triggers = await self.bot.servers.get_emoji_reaction_triggers(ctx.guild)
    #     if triggerphrase in reaction_triggers.keys():
    #         await ctx.send(f'Trigger phrase "{triggerphrase}" already bound to an reaction!')
    #         return
        
    #     reaction_found = discord.utils.find(lambda x: x.name == reaction.name, ctx.guild.emojis)
    #     if reaction_found == None:
    #         await ctx.send('Reaction not found! Please use the name of the reaction without colons (ie: trollface)')
    #         return
    #     else:
    #         reaction_triggers.update({triggerphrase.replace(" ", ""): reaction_found.name})
    #         await self.bot.servers.update_server_reaction_triggers(ctx.guild, reaction_triggers)
    #         await ctx.send('Reaction trigger added!')
    #         return
    
    # @commands.command(name="adddefaultemojireactiontrigger", aliases=['adddefaultrt'])
    # @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    # async def add_default_reaction_trigger(self, ctx, triggerphrase, reaction):
    #     """[Executive Moderator command] Command to add a default emoji to a reaction trigger. Requires a trigger phrase and the emoji"""
    #     # Some checking code to make sure that the info hasn't been added already
    #     reaction_triggers = await self.bot.servers.get_emoji_reaction_triggers(ctx.guild)
    #     if triggerphrase in reaction_triggers.keys():
    #         await ctx.send(f'Trigger phrase {triggerphrase} already bound to an reaction!')
    #         return
        
    #     emoji = utils.is_default_emoji(reaction)
    #     if not emoji[0]:
    #         await ctx.reply(f'{reaction} is not a default emoji!')
    #         return
        
    #     reaction_triggers.update({triggerphrase.replace(" ", ""): emoji[1]})
    #     await self.bot.servers.update_server_reaction_triggers(ctx.guild, reaction_triggers)
    #     await ctx.send('Reaction trigger added!')
    #     return


    # @commands.command(name="removecustomemojireactiontrigger", aliases=['rmcustomrt'])
    # @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    # async def remove_custom_reaction_trigger(self, ctx, triggerphrase, reaction: discord.Emoji):
    #     """[Executive Moderator command] Command to remove an automatic reaction setting. Requires the trigger phrase and the reaction name"""
    #     triggerphrase = triggerphrase.replace(" ", "")
    #     reaction_triggers = await self.bot.servers.get_emoji_reaction_triggers(ctx.guild)
    #     if not triggerphrase in reaction_triggers.keys():
    #         await ctx.reply(f'Trigger phrase {triggerphrase} not found in saved triggers!')
    #         return
    #     # logic here should work as intended since the previous if statement checked as needed
    #     if reaction_triggers.get(triggerphrase) != reaction.name:
    #         await ctx.reply(f'Trigger phrase {triggerphrase} not currently bound to reaction {reaction}')
    #         return
    #     reaction_triggers.pop(triggerphrase)
    #     await self.bot.servers.update_server_reaction_triggers(ctx.guild, reaction_triggers)
    #     await ctx.reply('Reaction trigger removed!')
    #     return

    # @commands.command(name="removedefaultemojireactiontrigger", aliases=['rmdefaultrt'])
    # @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    # async def remove_default_reaction_trigger(self, ctx, triggerphrase, reaction):
    #     """[Executive Moderator command] Command to remove an automatic reaction setting. Requires the trigger phrase and the reaction name"""
    #     reaction = utils.is_default_emoji(reaction)[1]
    #     triggerphrase = triggerphrase.replace(" ", "")
    #     reaction_triggers = await self.bot.servers.get_emoji_reaction_triggers(ctx.guild)
    #     if not triggerphrase in reaction_triggers.keys():
    #         await ctx.reply(f'Trigger phrase {triggerphrase} not found in saved triggers!')
    #         return
    #     # logic here should work as intended since the previous if statement checked as needed
    #     if reaction_triggers.get(triggerphrase) != reaction:
    #         await ctx.reply(f'Trigger phrase {triggerphrase} not currently bound to reaction {reaction}')
    #         return
    #     reaction_triggers.pop(triggerphrase)
    #     await self.bot.servers.update_server_reaction_triggers(ctx.guild, reaction_triggers)
    #     await ctx.reply('Reaction trigger removed!')
    #     return

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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id or message.author.bot:
            return
        
        reactions = await self._string_search(message)
        await self.listen_reactions(message, reactions[0], reactions[1])

        # # :christmas_troll: poor chaotic :amogus:
        if message.author.id == 731659389550985277:
            sussy = discord.utils.get(message.guild.emojis, name="sus")
            await message.add_reaction(sussy)

    # async def listen_reactions(self, message, react_emojis):
    #     if len(react_emojis) != 0:
    #         coros = [self._coro_react(message, react_emoji) for react_emoji in react_emojis]
    #         await asyncio.gather(*coros)
    
    async def listen_reactions(self, message, reactions_to_add, messages_to_send):
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