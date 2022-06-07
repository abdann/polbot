import discord
import sys
import traceback

class CommandErrHandler(discord.ext.commands.Cog):
    """Single Error handler class for bot commands"""
    def __init__(self, bot):
        self.bot = bot
    
    @discord.ext.commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.CommandNotFound):
            await ctx.reply('I do not know that command.')
        if isinstance(error, discord.ext.commands.errors.CheckFailure):
            await ctx.reply('You do not have the required privileges to run that command!')
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.reply(f'Insufficient arguments provided. Please type {self.bot.command_prefix} help {ctx.command.name} to see the correct usage.')
        if isinstance(error, discord.ext.commands.errors.EmojiNotFound):
            await ctx.reply(f'The emoji was not found!')
        else:
            print(f'Ignoring exception in command {ctx.command}', file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
