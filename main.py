import os
import asyncio

from pretty_help import PrettyHelp
from discord.ext import commands
import discord

import cogs.serverhandler
import cogs.permissionshandler
import cogs.reactionhandler
import cogs.commanderrorhandler
import cogs.moderationhandler
import cogs.shitpostinghandler
import servers.models

class PolBot(commands.Bot):
    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!')

async def main():
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN_LIVE')
    DATABASEDRIVER = os.getenv('DATABASE_DRIVER_ASYNC')
    DATABASEURL = os.getenv('DATABASE_URL_LIVE')
    DATABASEURL = DATABASEDRIVER + DATABASEURL
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = PolBot(
        command_prefix='.pol ',
        intents=intents,
        help_command=PrettyHelp()
    )
    # Initialize database API
    bot.servers = cogs.serverhandler.ServerConfigHandler(DATABASEURL)
    
    #This must be done here since the __init__ method of ServerConfigHandler is synchronous only.
    async with bot.servers.engine.begin() as conn:
        await conn.run_sync(servers.models.Base.metadata.create_all)
    # Initialize cogs
    await bot.add_cog(cogs.permissionshandler.PermissionsHandler(bot))
    await bot.add_cog(cogs.reactionhandler.ReactionHandler(bot))
    await bot.add_cog(cogs.commanderrorhandler.CommandErrHandler(bot))
    await bot.add_cog(cogs.moderationhandler.ModerationHandler(bot))
    await bot.add_cog(cogs.shitpostinghandler.ShitpostingHandler(bot))
    #Add cogs to bot before this line

    #Login and connect to Discord
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())