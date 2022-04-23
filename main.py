import nextcord
import cogs.permissionshandler

class PolBot(nextcord.ext.commands.Bot):
    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!')

def main():
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')

    bot = PolBot(
        command_prefix='.pol '
    )

    #Add cogs to bot before this line
    bot.run(TOKEN)

if __name__ == "__main__":
    main()