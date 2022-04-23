import nextcord


#Temporary hard coded role names. Plan to migrate to a better system
trial_moderator_role_name = "Trial Moderator"
moderator_role_name = "Moderator"
executive_moderator_role_name = "Executive Moderator"
admin_role_name = "Admin"


class PermissionsHandler(nextcord.ext.commands.Cog, name='PermissionsHandler'):
    """A class to handle all command permissions of the bot"""
    def __init__(self, bot):
        self.bot = bot
    
    def trial_moderator_check(self, ctx):
        """Checks if a command invoker is a moderator"""
        return True if trial_moderator_role_name in [role.name for role in ctx.message.author.roles] else False

    def moderator_check(self, ctx):
        """Checks if a command invoker is a moderator"""
        return True if moderator_role_name in [role.name for role in ctx.message.author.roles] else False

    def executive_moderator_check(self, ctx):
        """Checks if a command invoker is a moderator"""
        return True if executive_moderator_role_name in [role.name for role in ctx.message.author.roles] else False

    def admin_check(self, ctx):
        """Checks if a command invoker is a moderator"""
        return True if admin_role_name in [role.name for role in ctx.message.author.roles] else False

