import discord
import json
import pathlib



class ServerConfigHandler:

    with open("default_parameters.json") as f:
        default_parameters = json.load(f)
    
    possible_parameters = default_parameters.keys()

    def __init__(self):
        # IDK if this line is correct
        self.servers = pathlib.Path("servers")

    def get_server_parameters(self, ctx):
        """Retrieves the current server parameter list"""
        self._check_folder(ctx)
        with open((self.servers / str(ctx.guild.id) / "parameters.json").resolve(), 'r') as f:
            parameters = json.load(f)
        return parameters
    
    def update_server_parameters(self, ctx, parameters:dict):
        """Updates the server parameters"""
        self._check_folder(ctx)
        with open((self.servers / str(ctx.guild.id) / "parameters.json").resolve(), 'w') as f:
            json.dump(parameters, f)
    
    def find_in_server_auto_ban_whitelist(self, ctx, user:discord.User):
        """Finds the specified user in the auto-ban whitelist. Returns True if found, False otherwise."""
        self._check_folder(ctx) 
        with open((self.servers / str(ctx.guild.id) / "auto_ban_whitelist.json").resolve(), 'r') as f:
            auto_ban_whitelist = json.load(f)
        if str(user.id) in auto_ban_whitelist.keys():
            return True
        return False
    
    def remove_in_server_auto_ban_whitelist(self, ctx, user: discord.User):
        """Removes a user from the whitelist. Returns True if the user was found and removed, otherwise return False"""
        self._check_folder(ctx)

        with open((self.servers / str(ctx.guild.id) / "auto_ban_whitelist.json").resolve(), '+') as f:
            auto_ban_whitelist = json.load(f)
            if not isinstance(auto_ban_whitelist.pop(str(user.id)), None):
                json.dump(auto_ban_whitelist, f)
                return True
            return False

    def add_in_server_auto_ban_whitelist(self, ctx, user:discord.User):
        """Adds a user to the auto-ban whitelist. Returns True if successfully added the user to the whitelist, False if they already are in the whitelist"""
        self._check_folder(ctx)
        with open((self.servers / str(ctx.guild.id) / "auto_ban_whitelist.json").resolve(), '+') as f:
            auto_ban_whitelist = json.load(f)
            if str(user.id) in auto_ban_whitelist.keys():
                return False
            auto_ban_whitelist.update({str(user.id):user.name})
            json.dump(auto_ban_whitelist, f)
        return True
    
    def find_in_polder(self, ctx, discord_media_link):
        """Finds a message corresponding to a piece of media (the link) stored in the polder database. Returns the discord message ID if the associated discord link is found, False otherwise"""
        self._check_folder(ctx)
        with open((self.servers / str(ctx.guild.id) /"polder.json").resolve(), 'r') as f:
            polder = json.load(f)
            return polder.get(str(discord_media_link), False)
    
    def add_in_polder(self, ctx, discord_media_link, message:discord.Message):
        """Adds a link to a piece of media. Returns True if successful, False otherwise."""
        self._check_folder(ctx)
        with open((self.servers / str(ctx.guild.id) /"polder.json").resolve(), '+') as f:
            polder = json.load(f)
            if str(discord_media_link) not in polder.keys():
                polder.update({str(discord_media_link): message.id})
                json.dump(polder, f)
                return True
            return False

    def remove_in_polder(self, ctx, discord_media_link):
        """Removes a saved polder entry given a discord media link. Returns True if the link was found and removed, False otherwise"""
        self._check_folder(ctx)
        with open((self.servers / str(ctx.guild.id) /"polder.json").resolve(), '+') as f:
            polder = json.load(f)
            if polder.pop(str(discord_media_link), False):
                json.dump(polder, f)
                return True
            return False

    def _create_server_config_folder(self, ctx):
        """Makes a server config folder and creates the default parameters"""
        server_folder = self.servers / str(ctx.guild.id)
        server_folder.mkdir()
        with open((server_folder / "parameters.json").resolve(), 'x') as f:
            json.dump(self.default_parameters, f)
        with open((server_folder / "auto_ban_whitelist.json").resolve(), 'x') as f:
            json.dump(dict(), f)
        with open((server_folder / "reaction_triggers.json").resolve(), 'x') as f:
            json.dump(dict(), f)
        with open((server_folder / "polder.json").resolve(), 'x') as f:
            json.dump(dict(), f)

    def _check_folder(self, ctx):
        """Checks and initializes folder if needed"""
        if not self._server_folder_exists(ctx):
            self._create_server_config_folder(ctx)

    def _server_folder_exists(self, ctx):
        """Checks if a server folder is already stored and returns true or false"""
        return True if ((self.servers / str(ctx.guild.id)).exists()) else False