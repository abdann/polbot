import discord
import cogs.permissionshandler
from discord.ext import commands
import json
import datetime

class ModerationHandler(commands.Cog, name='ModerationHandler'):
    """A class to handle all moderation functions of the bot as well as corresponding commands"""
    def __init__(self, bot):
        self.bot = bot
        # IDK if this line is correct
        with open("parameters.json") as f:
            parameters = json.load(f)
        self.bot.parameters = parameters
        with open("auto_ban_whitelist.json") as f:
            auto_ban_whitelist = json.load(f)
        self.bot.auto_ban_whitelist = auto_ban_whitelist

    @commands.command(name="enablelockdown")
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def enablelockdown(self, ctx):
        """Command to enable a lockdown and disallow members to join"""

        if not self.bot.parameters["lockdown_enabled"]:
            self.bot.parameters.update({"lockdown_enabled" : True})
            await ctx.reply('Lockdown enabled! All members who try to join will be kicked and notified in DMs')
            self.save_parameters()
            return
        else:
            await ctx.reply('Lockdown is already enabled!')
    
    @commands.command(name="disablelockdown")
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def disablelockdown(self, ctx):
        """Command to disable a lockdown and allowed members to join"""
        if self.bot.parameters["lockdown_enabled"]:
            self.bot.parameters.update({"lockdown_enabled" : False})
            await ctx.reply('Lockdown disabled! All members who try to join will no longer be kicked.')
            self.save_parameters()
            return
        else:
            await ctx.reply('Lockdown is already disabled!')

    @commands.command(name="setminimumautobanage")
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def set_autoban_age(self, ctx, age:int):
        """Command to set the minimum age an account must be to be able to join the server. age is an integer for account age in days"""
        self.bot.parameters["min_account_age"] = age
        self.save_parameters()
        await ctx.reply(f'Set the minimum account age to {age} days old')
        return
        # else:
        #     await ctx.reply('Invalid age provided. Enter an integer, such as 14')
        #     return
    


    @commands.command(name="enableautoban")
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def enableautoban(self, ctx):
        """Command to enable autoban system"""
        if self.bot.parameters["new_auto_ban_enabled"]:
            await ctx.reply('autoban system already enabled!')
            return
        self.bot.parameters['new_auto_ban_enabled'] = True
        self.save_parameters()
        await ctx.reply('Auto ban enabled')
        return

    @commands.command(name="disableautoban")
    @commands.check(cogs.permissionshandler.PermissionsHandler.executive_moderator_check)
    async def disableautoban(self, ctx):
        """Command to disable autoban system"""
        if not self.bot.parameters["new_auto_ban_enabled"]:
            await ctx.reply('autoban system already disabled!')
            return
        self.bot.parameters['new_auto_ban_enabled'] = False
        self.save_parameters()
        await ctx.reply('Auto ban disabled')
        return

    @commands.command(name="addwhitelist")
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def add_to_whitelist(self, ctx, user: discord.User):
        """Adds a person to the auto-ban whitelist, allowing them to join the server although they are younger than the minimum age set."""
        if user.id in self.bot.auto_ban_whitelist.keys():
            await ctx.reply(f'User {user.display_name} with ID {user.id} already whitelisted!')
            return
        self.bot.auto_ban_whitelist[user.id] = user.display_name
        self.save_auto_ban_whitelist()
        await ctx.reply(f'Added User {user.display_name} with ID {user.id} to whitelist.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.bot.parameters["lockdown_enabled"]:
            dms = await member.create_dm()
            await dms.send(content="The server is currently in lockdown! Please try joining again soon.")
            await member.kick(reason="Lockdown Enabled.")
            return
        if self.bot.parameters["new_auto_ban_enabled"]:
            if member.id not in self.bot.auto_ban_whitelist.keys():
                account_age = datetime.datetime.now() - member.created_at
                if account_age.total_seconds() < datetime.timedelta(days=self.bot.parameters["min_account_age"]).total_seconds():
                    await member.ban(reason=f'Account age less than {self.bot.parameters["min_account_age"]} days old')
                    return

    

    def save_auto_ban_whitelist(self):
        """Saves the auto ban whitelist"""
        with open('auto_ban_whitelist.json', 'w', encoding='utf-8') as f:
            json.dump(self.bot.auto_ban_whitelist, f, ensure_ascii=False, indent=4)
      
    def save_parameters(self):
        """Saves the parameter list"""
        with open('parameters.json', 'w', encoding='utf-8') as f:
            json.dump(self.bot.parameters, f, ensure_ascii=False, indent=4)