import nextcord
import sys
import traceback

class CommandErrHandler(nextcord.ext.commands.Cog):
    """Single Error handler class for bot commands"""
    def __init__(self, bot):
        self.bot = bot
    
    @discord.ext.commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, nextcord.ext.commands.CommandNotFound):
            await ctx.send('I do not know that command.')
        else:
            print(f'Ignoring exception in command {ctx.command}', file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
