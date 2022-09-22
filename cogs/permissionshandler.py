from discord.ext import commands
import discord

#Temporary hard coded role names. Plan to migrate to a better system
trial_moderator_role_name = "Trial Moderator"
moderator_role_name = "Moderator"
executive_moderator_role_name = "Executive Moderator"
admin_role_name = "Admin"


class PermissionsHandler(commands.Cog, name='Permissions'):
    """Handles all command permissions of the bot. Note that a linear role hierachy is presumed, from trial moderator up to bot owner, therefore allowing those higher in the hierarchy to execute commands that require having lower roles"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setstaffrole')
    @commands.check(commands.has_permissions(administrator=True))
    async def set_staff_role(self, ctx:commands.Context, role: discord.Role):
        """Administrator command.
        
        Sets the role that can use all bot commands. Note: Certain commands, like the ban command, require extra discord permissions."""
        await self.bot.servers.update_server_parameters(ctx.guild, staff_role=role.id)
        await ctx.reply(embed=discord.Embed(description=f"Set the staff role to {role.mention} with ID {role.id}"))
    
    @commands.command(name='staffrole?', aliases=['getstaffrole'])
    @commands.check(commands.has_permissions(manage_messages=True))
    async def get_staff_role(self, ctx:commands.Context):
        """Gets the role that can use all bot commands. Note: Certain commands, like the ban command, require extra discord permissions."""
        staff_role_id = (await self.bot.servers.get_server_parameters(ctx.guild, "staff_role")).get("staff_role")
        staff_role = discord.utils.get(ctx.guild.roles, id=staff_role_id)
        if staff_role is None:
            await ctx.reply(embed=discord.Embed(title="There is currently no staff role set! A user with administrator permissions must use the command `setstaffrole` to set the role."))
            return
        await ctx.reply(embed=discord.Embed(description=f"The current staff role is {staff_role.mention} with ID {staff_role_id}"))

    @classmethod
    def owner_check(cls, ctx:commands.Context):
            """Checks if a command invoker is the owner"""
            return True if (ctx.author.id == ctx.bot.BOTOWNERID) else False

def markov_command_running(ctx):
    return not ctx.bot.making_text

async def staff_check(ctx:commands.Context):
    if (ctx.author.id == ctx.bot.BOTOWNERID):
        return True
    staff_role_id = (await ctx.bot.servers.get_server_parameters(ctx.guild, "staff_role")).get("staff_role")
    if staff_role_id is None:
        return False
    return True if discord.utils.get(ctx.author.roles, id=staff_role_id) is not None else False