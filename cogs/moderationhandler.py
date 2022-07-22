import discord
import cogs.permissionshandler
from discord.ext import commands
import datetime

tz = discord.utils.utcnow().astimezone().tzinfo

class ModerationHandler(commands.Cog, name='Moderation'):
    """Handles all moderation functions of the bot as well as corresponding commands"""
    def __init__(self, bot):
        self.bot = bot
        # IDK if this line is correct
        # with open("parameters.json") as f:
        #     parameters = json.load(f)
        # self.bot.parameters = parameters
        # with open("auto_ban_whitelist.json") as f:
        #     auto_ban_whitelist = json.load(f)
        # self.bot.auto_ban_whitelist = auto_ban_whitelist
        self.ban_embed = discord.Embed(description="""We automatically ban new accounts because of frequent raids. If you believe this to be a mistake, please appeal to the staff in our appeals server. Here is the invite: https://discord.gg/7bST6Ha73X""", 
        title="""You have been automatically banned from Political Compass Memes because your account was younger than the minimum account age.""")

    @commands.command(name="stoppolbot", aliases=['stop'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.owner_check)
    async def stop_pol_bot(self, ctx):
        """[Admin command] Stops the monster when he's gone off the deep end (Shuts down the bot gracefully)"""
        await ctx.reply("Attempting shutdown. Further bot actions beyond this message indicate a failure to halt")
        await ctx.bot.close()


    @commands.command(name="enablelockdown", aliases=['elockdown'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def enablelockdown(self, ctx):
        """[Executive Moderator command] Command to enable a lockdown and disallow members to join"""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "lockdown")
        if not params["lockdown"]:
            params.update({"lockdown" : True})
            await self.bot.servers.update_server_parameters(ctx.guild, **params)
            await ctx.reply('Lockdown enabled! All members who try to join will be kicked and notified in DMs')
            return
        else:
            await ctx.reply('Lockdown is already enabled!')
    
    @commands.command(name="disablelockdown", aliases=['dlockdown'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def disablelockdown(self, ctx):
        """[Executive Moderator command] Command to disable a lockdown and allowed members to join"""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "lockdown")
        if params["lockdown"]:
            params.update({"lockdown" : False})
            await self.bot.servers.update_server_parameters(ctx.guild, **params)
            await ctx.reply('Lockdown disabled! All members who try to join will no longer be kicked.')
            return
        else:
            await ctx.reply('Lockdown is already disabled!')

    @commands.command(name='lockdownstatus', aliases=['lockdown?'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.trial_moderator_check)
    async def lockdown_status(self, ctx):
        """[Moderator command] Returns whether or not there is a lockdown in effect."""
        lockdown_status = await self.bot.servers.get_server_parameters(ctx.guild, 'lockdown')
        await ctx.reply(f"Lockdown enabled: {lockdown_status.get('lockdown')}")
        return

    @commands.command(name="setminimumautobanage", aliases=['setminage'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def set_autoban_age(self, ctx, age):
        """[Executive Moderator command] Command to set the minimum age an account must be to be able to join the server. age is an integer for account age in days"""
        try:
            age = int(age)
        except ValueError:
            await ctx.reply(f'{age} is not a valid integer')
            return
        params = await self.bot.servers.get_server_parameters(ctx.guild, "min_account_age")
        params.update({"min_account_age":age})
        await self.bot.servers.update_server_parameters(ctx.guild, **params)
        await ctx.reply(f'Set the minimum account age to {age} days old')

    @commands.command(name="getminimumautobanage", aliases=['minage'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.trial_moderator_check)
    async def get_autoban_age(self, ctx):
        """[Moderator command] Command to get the minimum age an account must be to be able to join the server without getting autobanned."""
        min_age = await self.bot.servers.get_server_parameters(ctx.guild, "min_account_age")
        await ctx.reply(f'Minimum account age: {min_age.get("min_account_age")} days')


    @commands.command(name="enableautoban", aliases=['eautoban'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def enableautoban(self, ctx):
        """[Executive Moderator command] Command to enable autoban system"""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "new_auto_ban")
        if params["new_auto_ban"]:
            await ctx.reply('autoban system already enabled!')
            return
        params.update({'new_auto_ban':True})
        await self.bot.servers.update_server_parameters(ctx.guild, **params)
        await ctx.reply('Auto ban enabled')
        return

    @commands.command(name="disableautoban", aliases=['dautoban'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def disableautoban(self, ctx):
        """[Executive Moderator command] Command to disable autoban system"""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "new_auto_ban")
        if not params["new_auto_ban"]:
            await ctx.reply('autoban system already disabled!')
            return
        params.update({'new_auto_ban':False})
        await self.bot.servers.update_server_parameters(ctx.guild, **params)
        await ctx.reply('Auto ban disabled')
        return

    @commands.command(name="autoban_status", aliases=['autoban?'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.trial_moderator_check)
    async def autoban_status(self, ctx):
        """[Moderator command] Returns whether or not the new account autoban feature is enabled"""
        auto_ban_status = await self.bot.servers.get_server_parameters(ctx.guild, 'new_auto_ban')
        await ctx.reply(f"New account autoban feature enabled: {auto_ban_status.get('new_auto_ban')}")
        return

    @commands.command(name="addwhitelist")
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def add_to_whitelist(self, ctx, user: discord.User):
        """[Moderator command] Adds a person to the auto-ban whitelist, allowing them to join the server although they are younger than the minimum age set. If the person if not already unbanned, this command also unbans them"""
        if await self.bot.servers.add_in_server_auto_ban_whitelist(ctx.guild, user):
            try:
                await ctx.guild.unban(user, reason='New account has been whitelisted by staff')
            except discord.errors.NotFound:
                await ctx.send(f'User {user.display_name} with ID {user.id} not found in server bans.')
            await ctx.reply(f'Added User {user.display_name} with ID {user.id} to whitelist.')
        else:
            await ctx.reply(f'User {user.display_name} with ID {user.id} already whitelisted!')
            return


    @commands.command(name="removewhitelist", aliases=['rmwhitelist'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def remove_from_whitelist(self, ctx, user:discord.User):
        """[Moderator command] Removes a person from the auto-ban whitelist."""

        if await self.bot.servers.remove_in_server_auto_ban_whitelist(ctx.guild, user):
            await ctx.reply(f'Removed User {user.display_name} with ID {user.id} from whitelist')
            return
        await ctx.reply(f'User {user.display_name} with ID {user.id} not found in whitelist.')
        return
    
    @commands.command(name="getwhitelist")
    @commands.check(cogs.permissionshandler.PermissionsHandler.trial_moderator_check)
    async def get_whitelist(self, ctx):
        """[Moderator command] Lists all whitelisted users"""
        whitelist = await self.bot.servers.get_server_auto_ban_whitelist(ctx.guild)
        if len(whitelist) != 0:
            await ctx.reply('\n'.join([f"ID: {user_id} ,User: {ctx.guild.get_member(user_id)}" for user_id in whitelist]))
            return
        await ctx.reply("No whitelisted users")

    @commands.command(name="ban")
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def ban(self, ctx, user:discord.User, *reason):
        reason = " ".join(reason)
        if reason == "":
            await ctx.reply("A reason must be supplied to ban someone")
            return
        await ctx.guild.ban(user, reason=reason, delete_message_days=0)
        await ctx.reply(f"Banned user {user.name}#{user.discriminator} (ID {user.id})")
        return
    
    @commands.command(name="unban")
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def unban(self, ctx, user:discord.User, *reason):
        reason = " ".join(reason)
        if reason == "":
            await ctx.reply("A reason must be supplied to unban someone")
            return
        await ctx.guild.unban(user, reason=reason)
        await ctx.reply(f"Unbanned user {user.name}#{user.discriminator} (ID {user.id})")
        return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        params = await self.bot.servers.get_server_parameters(member.guild, "lockdown", "new_auto_ban", "min_account_age")
        await self.lockdown_listener(member, params)
        await self.auto_ban_listener(member, params)

    async def lockdown_listener(self, member, params):
        if params.get("lockdown"):
            dms = await member.create_dm()
            await dms.send(content="The server Political Compass Memes is currently in lockdown due to an issue! Please try joining again soon.")
            await member.kick(reason="Lockdown Enabled.")
            return
    
    async def auto_ban_listener(self, member, params):
        if params.get("new_auto_ban"):
            if not await self.bot.servers.find_in_server_auto_ban_whitelist(member.guild, member):
                account_age = discord.utils.utcnow() - member.created_at
                if account_age.total_seconds() < datetime.timedelta(days=params.get('min_account_age')).total_seconds():
                    dm = await member.create_dm()
                    await dm.send(embed=self.ban_embed)
                    await member.ban(reason=f"Account age less than {params.get('min_account_age')} days old. Please appeal to staff in the appeals server.")
                    return
