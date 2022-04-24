from discord.ext import commands

#Temporary hard coded role names. Plan to migrate to a better system
trial_moderator_role_name = "Trial Moderator"
moderator_role_name = "Moderator"
executive_moderator_role_name = "Executive Moderator"
admin_role_name = "Admin"


class PermissionsHandler(commands.Cog, name='PermissionsHandler'):
    """A class to handle all command permissions of the bot"""
    def __init__(self, bot):
        self.bot = bot

    @classmethod
    def trial_moderator_check(cls, ctx):
        """Checks if a command invoker is a trial moderator or higher"""
        return True if (trial_moderator_role_name in [role.name for role in ctx.message.author.roles] or cls.moderator_check(ctx)) else False

    @classmethod
    def moderator_check(cls, ctx):
        """Checks if a command invoker is a moderator"""
        return True if (moderator_role_name in [role.name for role in ctx.message.author.roles] or cls.executive_moderator_check(ctx)) else False

    @classmethod
    def executive_moderator_check(cls, ctx):
        """Checks if a command invoker is an executive moderator"""
        return True if (executive_moderator_role_name in [role.name for role in ctx.message.author.roles] or cls.admin_check(ctx)) else False

    @classmethod
    def admin_check(cls, ctx):
        """Checks if a command invoker is an admin"""
        return True if admin_role_name in [role.name for role in ctx.message.author.roles] else False

