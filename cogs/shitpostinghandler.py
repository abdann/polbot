import discord
import asyncio
import cogs.permissionshandler
from discord.ext import commands

class ShitpostingHandler(commands.Cog, name='Shitposting'):
    """Handles all shitposting commands and features of the bot"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    @commands.command(name="setpolder")
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def set_polder(self, ctx, polder_channel:discord.TextChannel):
        """Sets the polder channel to the specified channel using the hashtag prefix"""
        self.bot.servers.get_server_parameters(ctx.guild)
