from discord.ext import commands
import discord
import cogs.serverhandler
import cogs.permissionshandler
import cogs.reactionhandler
import cogs.commanderrorhandler
import cogs.moderationhandler
import os
from pretty_help import PrettyHelp

class PolBot(commands.Bot):
    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!')

def main():
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN_LIVE')
    GUILD = os.getenv('DISCORD_GUILD')
    intents = discord.Intents.default()
    intents.members = True
    bot = PolBot(
        command_prefix='.pol ',
        intents=intents,
        help_command=PrettyHelp()
    )
    bot.servers = cogs.serverhandler.ServerConfigHandler()
    bot.add_cog(cogs.permissionshandler.PermissionsHandler(bot))
    bot.add_cog(cogs.reactionhandler.ReactionHandler(bot))
    bot.add_cog(cogs.commanderrorhandler.CommandErrHandler(bot))
    bot.add_cog(cogs.moderationhandler.ModerationHandler(bot))
    #Add cogs to bot before this line
    bot.run(TOKEN)

if __name__ == "__main__":
    main()