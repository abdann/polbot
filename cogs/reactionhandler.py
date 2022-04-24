import discord
import emoji
from discord.ext import commands
import cogs.permissionshandler
import json
import asyncio


class ReactionHandler(commands.Cog, name='ReactionHandler'):
    """A class to handle all reaction functions of the bot as well as corresponding commands"""
    def __init__(self, bot):
        self.bot = bot
        # IDK if this line is correct
        with open("reaction_triggers.json") as f:
            reaction_triggers = json.load(f)
        self.bot.reaction_triggers = reaction_triggers
    
    #Decorators indicate that it is a command and you must have at least a role to use
    @commands.command(name="addreactiontrigger")
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def add_reaction_trigger(self, ctx, triggerphrase, reaction):
        """Command to add a reaction triggerword to the bot. Requires a trigger phrase and a valid reaction present on the server"""
        
        # Some checking code to make sure that the info hasn't been added already
        if triggerphrase in self.bot.reaction_triggers.keys():
            await ctx.send(f'Trigger phrase {triggerphrase} already bound to an reaction!')
            return
        
        reaction_found = discord.utils.find(lambda x: x.name == reaction, ctx.guild.emojis)
        if reaction_found == None:
            await ctx.send('Reaction not found! Please use the name of the reaction without colons (ie: trollface)')
            return
        else:
            self.bot.reaction_triggers.update({triggerphrase: reaction_found.name})
            self.save_reaction_triggers()
            await ctx.send('Reaction trigger added!')
            return
    
    @commands.command(name="removereactiontrigger")
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def remove_reaction_trigger(self, ctx, triggerphrase, reaction):
        """Command to remove an automatic reaction setting. Requires the trigger phrase and the reaction name"""
        if not triggerphrase in self.bot.reaction_triggers.keys():
            await ctx.reply(f'Trigger phrase {triggerphrase} not found in saved triggers!')
            return
        # logic here should work as intended since the previous if statement checked as needed
        if self.bot.reaction_triggers.get(triggerphrase) != reaction:
            await ctx.reply(f'Trigger phrase {triggerphrase} not currently bound to reaction {reaction}')
            return
        self.bot.reaction_triggers.pop(triggerphrase)
        self.save_reaction_triggers()
        await ctx.reply('Reaction trigger removed!')
        return
    
    @commands.command(name="listreactiontriggers")
    @commands.check(cogs.permissionshandler.PermissionsHandler.trial_moderator_check)
    async def list_reaction_triggers(self, ctx):
        """Lists all registered trigger phrases and the corresponding reaction name"""
        await ctx.reply('\n'.join([f'{key}: {value}' for key, value in self.bot.reaction_triggers.items()]))

    def save_reaction_triggers(self):
        """Updates the reaction trigger file with the curent state."""
        with open('reaction_triggers.json', 'w', encoding='utf-8') as f:
            json.dump(self.bot.reaction_triggers, f, ensure_ascii=False, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        react_emojis = self.string_search(message)
        if len(react_emojis) != 0:
            coros = [self.coro_react(message, react_emoji) for react_emoji in react_emojis]
            await asyncio.gather(*coros)
    
    async def coro_react(self, message, react_emoji):
        await message.add_reaction(react_emoji)

    def string_search(self, message):
        reactions=[]
        # First combine message into single string with no spaces and lowercase
        content = message.content.replace(" ", "").casefold()
        # now append any positive hits (THIS IS BLOCKING CODE)
        for triggerphrase, reaction in self.bot.reaction_triggers.items():
            if content.find(triggerphrase) != -1:
                react = discord.utils.get(message.guild.emojis, name=reaction)
                if (react is not None) and (react not in reactions):
                    reactions.append(react)
        return reactions
