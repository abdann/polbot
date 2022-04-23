import nextcord
import cogs.permissionshandler
import json

with open("reactiontriggers.json") as f:
    reaction_triggers = json.load(f)

class ReactionHandler(nextcord.ext.commands.Cog, name='ReactionHandler'):
    """A class to handle all reaction functions of the bot as well as corresponding commands"""
    def __init__(self, bot, reaction_triggers):
        self.bot = bot
        # IDK if this line is correct
        self.bot.reactions_triggers = reaction_triggers
    
    #Decorators indicate that it is a command and you must have at least a role to use
    @nextcord.ext.commands.command(name="addreactiontrigger")
    @nextcord.ext.commands.check(nextcord.ext.commands.has_role(cogs.permissionhandler.executive_moderator_check))
    async def add_reaction_trigger(self, ctx, triggerphrase, reaction):
        """Command to add a reaction triggerword to the bot. Requires a trigger phrase and a valid reaction present on the server"""
        