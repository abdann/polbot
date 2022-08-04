from discord.ext import commands
import sys
import traceback

class CommandErrHandler(commands.Cog):
    """Single Error handler class for bot commands"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.reply('I do not know that command.')
        if isinstance(error, commands.errors.CheckFailure):
            if ctx.command.name == "impact":
                await ctx.send(content="Currently generating text, please try again later", delete_after=5)
                return
            await ctx.reply('You do not have the required privileges to run that command!')
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.reply(f'Insufficient arguments provided. Please type {self.bot.command_prefix} help {ctx.command.name} to see the correct usage.')
        if isinstance(error, commands.errors.EmojiNotFound):
            await ctx.reply(f'The emoji was not found!')
        if isinstance(error, commands.UserNotFound):
            await ctx.reply("The user specified by the following was not found!: " + error.argument)
        if isinstance(error, commands.ChannelNotFound):
            await ctx.reply("The channel specified by the following was not found!: " + error.argument)
        if isinstance(error, commands.MessageNotFound):
            await ctx.reply("The message specified by the following was not found!: " + error.argument)
        else:
            print(f'Ignoring exception in command {ctx.command}', file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
