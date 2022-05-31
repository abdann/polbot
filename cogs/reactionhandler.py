import discord
import emojis
from discord.ext import commands
import cogs.permissionshandler
import asyncio


class ReactionHandler(commands.Cog, name='Reaction'):
    """Handles all reaction functions of the bot as well as corresponding commands"""
    def __init__(self, bot):
        self.bot = bot
        # IDK if this line is correct
        # with open("reaction_triggers.json") as f:
        #     reaction_triggers = json.load(f)
        # self.bot.reaction_triggers = reaction_triggers
    
    #Decorators indicate that it is a command and you must have at least a role to use
    @commands.command(name="addcustomemojireactiontrigger", aliases=['addcustomrt'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def add_custom_reaction_trigger(self, ctx, triggerphrase, reaction: discord.Emoji):
        """[Executive Moderator command] Command to add a reaction triggerword. Requires a trigger phrase and a valid reaction present on the server"""
        
        # Some checking code to make sure that the info hasn't been added already
        reaction_triggers = self.bot.servers.get_server_reaction_triggers(ctx.guild)
        if triggerphrase in reaction_triggers.keys():
            await ctx.send(f'Trigger phrase {triggerphrase} already bound to an reaction!')
            return
        
        reaction_found = discord.utils.find(lambda x: x.name == reaction.name, ctx.guild.emojis)
        if reaction_found == None:
            await ctx.send('Reaction not found! Please use the name of the reaction without colons (ie: trollface)')
            return
        else:
            reaction_triggers.update({triggerphrase.replace(" ", ""): reaction_found.name})
            self.bot.servers.update_server_reaction_triggers(ctx.guild, reaction_triggers)
            await ctx.send('Reaction trigger added!')
            return
    
    @commands.command(name="adddefaultemojireactiontrigger", aliases=['adddefaultrt'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def add_default_reaction_trigger(self, ctx, triggerphrase, reaction):
        """[Executive Moderator command] Command to add a default emoji to a reaction trigger. Requires a trigger phrase and the emoji"""
        # Some checking code to make sure that the info hasn't been added already
        reaction_triggers = self.bot.servers.get_server_reaction_triggers(ctx.guild)
        if triggerphrase in reaction_triggers.keys():
            await ctx.send(f'Trigger phrase {triggerphrase} already bound to an reaction!')
            return
        
        emoji = self.is_default_emoji(reaction)
        if not emoji[0]:
            await ctx.reply(f'{reaction} is not a default emoji!')
            return
        
        reaction_triggers.update({triggerphrase.replace(" ", ""): emoji[1]})
        self.bot.servers.update_server_reaction_triggers(ctx.guild, reaction_triggers)
        await ctx.send('Reaction trigger added!')
        return


    @commands.command(name="removecustomemojireactiontrigger", aliases=['rmcustomrt'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def remove_custom_reaction_trigger(self, ctx, triggerphrase, reaction: discord.Emoji):
        """[Executive Moderator command] Command to remove an automatic reaction setting. Requires the trigger phrase and the reaction name"""
        triggerphrase = triggerphrase.replace(" ", "")
        reaction_triggers = self.bot.servers.get_server_reaction_triggers(ctx.guild)
        if not triggerphrase in reaction_triggers.keys():
            await ctx.reply(f'Trigger phrase {triggerphrase} not found in saved triggers!')
            return
        # logic here should work as intended since the previous if statement checked as needed
        if reaction_triggers.get(triggerphrase) != reaction.name:
            await ctx.reply(f'Trigger phrase {triggerphrase} not currently bound to reaction {reaction}')
            return
        reaction_triggers.pop(triggerphrase)
        self.bot.servers.update_server_reaction_triggers(ctx.guild, reaction_triggers)
        await ctx.reply('Reaction trigger removed!')
        return

    @commands.command(name="removedefaultemojireactiontrigger", aliases=['rmdefaultrt'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def remove_default_reaction_trigger(self, ctx, triggerphrase, reaction):
        """[Executive Moderator command] Command to remove an automatic reaction setting. Requires the trigger phrase and the reaction name"""
        reaction = self.is_default_emoji(reaction)[1]
        triggerphrase = triggerphrase.replace(" ", "")
        reaction_triggers = self.bot.servers.get_server_reaction_triggers(ctx.guild)
        if not triggerphrase in reaction_triggers.keys():
            await ctx.reply(f'Trigger phrase {triggerphrase} not found in saved triggers!')
            return
        # logic here should work as intended since the previous if statement checked as needed
        if reaction_triggers.get(triggerphrase) != reaction:
            await ctx.reply(f'Trigger phrase {triggerphrase} not currently bound to reaction {reaction}')
            return
        reaction_triggers.pop(triggerphrase)
        self.bot.servers.update_server_reaction_triggers(ctx.guild, reaction_triggers)
        await ctx.reply('Reaction trigger removed!')
        return

    @commands.command(name="listreactiontriggers", aliases=['listrt'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.trial_moderator_check)
    async def list_reaction_triggers(self, ctx):
        """[Moderator command] Lists all registered trigger phrases and the corresponding reaction name"""
        reaction_triggers = self.bot.servers.get_server_reaction_triggers(ctx.guild)
        if len(reaction_triggers) == 0:
            await ctx.reply('No reaction triggers are currently set')
            return
        await ctx.reply('\n'.join([f'{key}: {value}' for key, value in reaction_triggers.items()]))

    # def save_reaction_triggers(self):
    #     """Updates the reaction trigger file with the curent state."""
    #     with open('reaction_triggers.json', 'w', encoding='utf-8') as f:
    #         json.dump(self.bot.reaction_triggers, f, ensure_ascii=False, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        react_emojis = self.string_search(message)
        await self.listen_reactions(message, react_emojis)

        # # :christmas_troll: poor chaotic :amogus:
        if message.author.id == 731659389550985277:
            sussy = discord.utils.get(message.guild.emojis, name="sus")
            await message.add_reaction(sussy)

    async def listen_reactions(self, message, react_emojis):
        if len(react_emojis) != 0:
            coros = [self.coro_react(message, react_emoji) for react_emoji in react_emojis]
            await asyncio.gather(*coros)
    
    async def coro_react(self, message, react_emoji):
        await message.add_reaction(react_emoji)

    def string_search(self, message):
        reactions=[]
        # First combine message into single string with no spaces and lowercase
        content = message.content.replace(" ", "").casefold()
        # now append any positive hits (THIS IS BLOCKING CODE
        reaction_triggers = self.bot.servers.get_server_reaction_triggers(message.guild)
        for triggerphrase, reaction in reaction_triggers.items():
            if content.find(triggerphrase) != -1:
                react = discord.utils.get(message.guild.emojis, name=reaction)
                if react is not None:
                    if react not in reactions:
                        reactions.append(react)
                elif self.is_default_emoji(reaction):
                    if reaction not in reactions:
                        reactions.append(reaction)
                else:
                    pass
        return reactions
    
    def is_default_emoji(self, reaction):
        """Determines whether the input is a default emoji. If it is, returns a tuple of (True, EMOJI), where EMOJI is the literal emoji. If it is not, returns (False, None)"""
        # This case is for an input like this: rainbow_flag
        if reaction.find(":") == -1 and len(emojis.get(reaction)) == 0:
            found_reaction = emojis.db.get_emoji_by_alias(reaction)
            if found_reaction is not None:
                return (True, emojis.encode(":" + reaction + ":"))
            return (False, None)
        # This case is for an input like this: :rainbow_flag:
        elif reaction.find(":") > -1 and len(emojis.get(reaction)) == 0:
            found_reaction = emojis.db.get_emoji_by_alias(reaction.replace(":", ""))
            if found_reaction is not None:
                return (True, emojis.encode(reaction))
            return (False, None)
        # This case is for an input like this: 🏳️‍🌈
        else:
            decoded = emojis.decode(reaction)
            found_reaction = emojis.db.get_emoji_by_alias(decoded.replace(":", ""))
            if reaction == found_reaction.emoji:
                return (True, reaction)
            return (False, None)
    