from discord.ext import commands
import discord
import cogs.serverhandler
import cogs.permissionshandler
import cogs.reactionhandler
import cogs.commanderrorhandler
import cogs.moderationhandler
import cogs.shitpostinghandler
import os
import asyncio
from pretty_help import PrettyHelp

class PolBot(commands.Bot):
    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!')

async def main():
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN_LIVE')
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = PolBot(
        command_prefix='.pol ',
        intents=intents,
        help_command=PrettyHelp()
    )
    bot.servers = cogs.serverhandler.ServerConfigHandler()
    await bot.add_cog(cogs.permissionshandler.PermissionsHandler(bot))
    await bot.add_cog(cogs.reactionhandler.ReactionHandler(bot))
    await bot.add_cog(cogs.commanderrorhandler.CommandErrHandler(bot))
    await bot.add_cog(cogs.moderationhandler.ModerationHandler(bot))
    await bot.add_cog(cogs.shitpostinghandler.ShitpostingHandler(bot))
    #Add cogs to bot before this line
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())