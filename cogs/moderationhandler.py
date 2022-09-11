import typing
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
    async def ban(self, ctx:commands.Context, user:typing.Union[discord.Member, discord.User], *reason): # must have member before user in Union to resolve correctly
        """Bans the user"""
        reason = " ".join(reason)
        if reason is None:  #enforces a reason requirement to ban someone
            await ctx.reply("A reason must be supplied to ban someone!")
            return
        if type(user) is discord.Member: #checks if the user supplied is a member already
            highest_author_role = ctx.author.top_role
            highest_member_role = user.top_role
            if (highest_member_role < highest_author_role or ctx.author == ctx.guild.owner) and user != ctx.guild.owner: #ensures that someone can not ban someone who has a higher role than they do AND that guild owners can ban people regardless of role hierarchy AND that owners can not be banned regardless of hierarchy
                await ctx.guild.ban(user, reason=reason, delete_message_days=0) #Proceeds with ban if the person to ban is lower in the role hierarchy than the banner
                await ctx.reply(f"Banned user {user.name}#{user.discriminator} (ID {user.id})")
                return
            await ctx.reply("You can not ban a member who has a higher role than you!")
            return
        await ctx.guild.ban(user, reason=reason, delete_message_days=0) #For the case when the user in not a member of the server
        await ctx.reply(f"Banned user {user.name}#{user.discriminator} (ID {user.id})")
    
    @commands.command(name="unban")
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def unban(self, ctx:commands.Context, user:discord.User, *reason):
        """Unbans a user"""
        reason = " ".join(reason)
        if reason is None: #enforces a reason requirement to unban someone
            await ctx.reply("A reason must be supplied to unban someone!")
            return
        await ctx.guild.unban(user, reason=reason) #No permission check is required as the person can not be on the server
        await ctx.reply(f"Unbanned user {user.name}#{user.discriminator} (ID {user.id})")
        return

    @commands.command(name="enablefamilyfriendlymode", aliases=['enableffmode', 'effmode'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def enable_family_friendly_mode(self, ctx:commands.Context):
        """Enables Family Friendly mode. 
        
        This functionality searches for specified banned words in the pre-specified family friendly channels and deletes the message, notifying the offender of the banned word. This is a server wide setting"""
        params:typing.Dict[str, typing.Union[bool, None]] = await self.bot.servers.get_server_parameters(ctx.guild, "family_friendly_mode")
        if params.get("family_friendly_mode") is None:
            await self.bot.servers.update_server_parameters(ctx.guild, family_friendly_mode=True)
            await ctx.reply("Family Friendly mode is now enabled in designated channels.")
            return
        if params.get("family_friendly_mode"): #already enabled
            await ctx.reply("Family Friendly mode is already enabled in designated channels.")
            return
        await self.bot.servers.update_server_parameters(ctx.guild, family_friendly_mode=True)
        await ctx.reply("Family Friendly mode is now enabled in designated channels.")
        return

    @commands.command(name="disablefamilyfriendlymode", aliases=['disableffmode', 'dffmode'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def disable_family_friendly_mode(self, ctx:commands.Context):
        """Disables Family Friendly mode. 
        
        This functionality searches for specified banned words in the pre-specified family friendly channels and deletes the message, notifying the offender of the banned word. This is a server wide setting"""
        params:typing.Dict[str, typing.Union[bool, None]] = await self.bot.servers.get_server_parameters(ctx.guild, "family_friendly_mode")
        if params.get("family_friendly_mode") is None:
            await self.bot.servers.update_server_parameters(ctx.guild, family_friendly_mode=False)
            await ctx.reply("Family Friendly mode is now disabled in designated channels.")
            return
        if not params.get("family_friendly_mode"): #already disabled
            await ctx.reply("Family Friendly mode is already disabled in designated channels.")
            return
        await self.bot.servers.update_server_parameters(ctx.guild, family_friendly_mode=False)
        await ctx.reply("Family Friendly mode is now disabled in designated channels.")
        return
    
    @commands.command(name="getfamilyfriendlymode", aliases=['getffmode', 'familyfriendlymode?', 'ffmode?'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def get_family_friendly_mode(self, ctx:commands.Context):
        """Checks if Family Friendly mode is enabled. 
        
        This functionality searches for specified banned words in the pre-specified family friendly channels and deletes the message, notifying the offender of the banned word. This is a server wide setting"""
        params:typing.Dict[str, typing.Union[bool, None]] = await self.bot.servers.get_server_parameters(ctx.guild, "family_friendly_mode")
        if params.get("family_friendly_mode") is None:
            await self.bot.servers.update_server_parameters(ctx.guild, family_friendly_mode=self.bot.servers.default_parameters.get("family_friendly_mode"))
            setting:str = "enabled" if self.bot.servers.default_parameters.get("family_friendly_mode") else "disabled"
            await ctx.reply(f"Family Friendly mode is {setting} in designated channels.")
            return
        setting:str = "enabled" if params.get("family_friendly_mode") else "disabled"
        await ctx.reply(f"Family Friendly mode is {setting} in designated channels.")

    @commands.command(name="addfamilyfriendlychannel", aliases=['addffchannel', 'addfamilyfriendlychannels', 'addffchannels'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def add_family_friendly_channel(self, ctx:commands.Context, channels:commands.Greedy[discord.TextChannel]):
        """Adds a channel (or multiple channels, as provided) to the list of designated Family Friendly channels."""
        added_channels = list()
        failed_channels = list()
        for channel in channels:
            if await self.bot.servers.add_family_friendly_channel(ctx.guild, channel):
                added_channels.append(channel.mention)
            else:
                failed_channels.append(channel.mention)
        embed = discord.Embed()
        added_reply = f"The following channels have been added to the list of Family Friendly channels: {', '.join(added_channels)}"
        if failed_channels:
            embed = embed.add_field(
                name="The following channels are already designated Family Friendly channels:",
                value=f"{', '.join(failed_channels)}")
        if added_channels:
            embed = embed.add_field(
                name="The following channels have been added to the list of Family Friendly channels:",
                value=f"{', '.join(added_channels)}"
            )
        await ctx.reply(embed=embed)

    @commands.command(name="removefamilyfriendlychannel", aliases=['removeffchannel', 'rmffchannel', 'removefamilyfriendlychannels','removeffchannels', 'rmffchannels'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def remove_family_friendly_channel(self, ctx:commands.Context, channels:commands.Greedy[discord.TextChannel]):
        """Removes a channel (or multiple channels, as provided) to the list of designated Family Friendly channels."""
        removed_channels = list()
        failed_channels = list()
        for channel in channels:
            if await self.bot.servers.remove_family_friendly_channel(ctx.guild, channel):
                removed_channels.append(channel.mention)
            else:
                failed_channels.append(channel.mention)
        embed = discord.Embed()
        if failed_channels:
            embed = embed.add_field(
                name="The following channels are NOT already designated Family Friendly channels:",
                value=f"{', '.join(failed_channels)}")
        if removed_channels:
            embed = embed.add_field(
                name="The following channels have been removed from the list of Family Friendly channels:",
                value=f"{', '.join(removed_channels)}"
            )
        await ctx.reply(embed=embed)

    @commands.command(name="listfamilyfriendlychannels", aliases=['listffchannels', 'getfamilyfriendlychannels', 'getffchannels', 'familyfriendlychannels?', 'ffchannels?'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def get_family_friendly_channels(self, ctx:commands.Context):
        """Gets the list of designated Family Friendly channels."""
        ffchannel_ids:typing.List[int] = await self.bot.servers.get_family_friendly_channels(ctx.guild)
        ffchannels:typing.List[discord.TextChannel] = [(await ctx.guild.fetch_channel(channel_id)).mention for channel_id in ffchannel_ids]
        embed = discord.Embed()
        if ffchannels: #channels already set
            embed = embed.add_field(
            name="The following channels are designated Family Friendly channels:",
            value=f"{', '.join(ffchannels)}"
            )
        else:
            embed.title = "There are no designated Family Friendly channels."
        await ctx.reply(embed=embed)
    
    @commands.command(name='addbannedword')
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def add_banned_word(self, ctx:commands.Context, word:str):
        """Adds a word to the list of banned words under Family Friendly mode. This must be a single word."""
        if await self.bot.servers.add_banned_word(ctx.guild, word):
            embed = discord.Embed()
            embed = embed.add_field(
                name="Added the following word to the list of banned words under Family Friendly mode:",
                value=word
            )
            await ctx.reply(embed=embed)
            return
        embed = discord.Embed().add_field(
            name="The following word is already a banned word!:",
            value=word
        )
        await ctx.reply(embed=embed)
    
    @commands.command(name='removebannedword', aliases=['rmbannedword'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def remove_banned_word(self, ctx:commands.Context, word:str):
        """Removes a word from the list of banned words under Family Friendly mode. This must be a single word."""
        if await self.bot.servers.remove_banned_word(ctx.guild, word):
            embed = discord.Embed()
            embed = embed.add_field(
                name="Removed the following word from the list of banned words under Family Friendly mode:",
                value=word
            )
            await ctx.reply(embed=embed)
            return
        embed = discord.Embed().add_field(
            name="The following word is not a banned word!:",
            value=word
        )
        await ctx.reply(embed=embed)

    @commands.command(name='listbannedwords', aliases=['getbannedwords', 'bannedwords?'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def get_banned_words(self, ctx:commands.Context):
        """Gets the list of banned words under Family Friendly mode."""
        banned_words:typing.List[str] = await self.bot.servers.get_banned_words(ctx.guild)
        embed = discord.Embed()
        if not banned_words:
            embed.title = "There are no banned words under Family Friendly mode."
        else:
            embed = embed.add_field(
                name="The following words are banned words under Family Friendly mode:",
                value='\n'.join(banned_words)
            )
        await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        params = await self.bot.servers.get_server_parameters(member.guild, "lockdown", "new_auto_ban", "min_account_age")
        await self.lockdown_listener(member, params)
        await self.auto_ban_listener(member, params)

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        params = await self.bot.servers.get_server_parameters(message.guild, "family_friendly_mode")
        await self.ban_word_listener(message, params)
    
    async def ban_word_listener(self, message:discord.Message, params:dict):
        if message.author.bot or message.content.startswith(self.bot.command_prefix): #Ignore bot messages and commands
            return
        family_friendly_mode:typing.Union[bool, None] = params.get("family_friendly_mode") #check if family friendly mode is enabled
        if family_friendly_mode is None: #Checks if parameter is in the parameter JSON for that server and if it isn't, it updates the parameters
            await self.bot.servers.update_server_parameters(message.guild, family_friendly_mode=self.bot.servers.default_parameters.get("family_friendly_mode"))
            return
        if family_friendly_mode: #Checks if family friendly mode is enabled on the server
            if await self.bot.servers.find_in_family_friendly_channels(message.guild, message.channel): #Checks if the channel is a moderated channel
                banned_words:typing.List[str] = await self.bot.servers.get_banned_words(message.guild)
                for word in banned_words: #loop over this because it will almost always be smaller than the message
                    word = word.casefold() #Normalize the words to catch lowercase
                    if word in message.content:
                        author:discord.Member = message.author
                        channel = message.channel
                        await message.delete()
                        await channel.send(f"{author.mention}: The word `{word}` is banned in this channel. Watch your language!")
                        return #Decide to only notify them of the first banned word found, rather than every word found
    
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
