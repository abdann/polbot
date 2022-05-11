import discord
import json
import pathlib
from random import sample



class ServerConfigHandler:

    with open("default_parameters.json") as f:
        default_parameters = json.load(f)
    
    possible_parameters = default_parameters.keys()

    def __init__(self):
        # IDK if this line is correct
        self.servers = pathlib.Path("servers")

    def get_server_parameters(self, guild):
        """Retrieves the current server parameter list"""
        self._check_folder(guild)
        with open((self.servers / str(guild.id) / "parameters.json").resolve(), 'r') as f:
            parameters = json.load(f)
        return parameters
    
    def update_server_parameters(self, guild, parameters:dict):
        """Updates the server parameters"""
        self._check_folder(guild)
        with open((self.servers / str(guild.id) / "parameters.json").resolve(), 'w') as f:
            json.dump(parameters, f)
    
    def find_in_server_auto_ban_whitelist(self, guild, user:discord.User):
        """Finds the specified user in the auto-ban whitelist. Returns True if found, False otherwise."""
        self._check_folder(guild) 
        with open((self.servers / str(guild.id) / "auto_ban_whitelist.json").resolve(), 'r') as f:
            auto_ban_whitelist = json.load(f)
        if str(user.id) in auto_ban_whitelist.keys():
            return True
        return False
    
    def remove_in_server_auto_ban_whitelist(self, guild, user: discord.User):
        """Removes a user from the whitelist. Returns True if the user was found and removed, otherwise return False"""
        self._check_folder(guild)

        with open((self.servers / str(guild.id) / "auto_ban_whitelist.json").resolve(), 'r+') as f:
            auto_ban_whitelist = json.load(f)
        if not isinstance(auto_ban_whitelist.pop(str(user.id)), type(None)):
            with open((self.servers / str(guild.id) / "auto_ban_whitelist.json").resolve(), 'w') as f:
                json.dump(auto_ban_whitelist, f)
            return True
        return False

    def add_in_server_auto_ban_whitelist(self, guild, user:discord.User):
        """Adds a user to the auto-ban whitelist. Returns True if successfully added the user to the whitelist, False if they already are in the whitelist"""
        self._check_folder(guild)
        with open((self.servers / str(guild.id) / "auto_ban_whitelist.json").resolve(), 'r+') as f:
            auto_ban_whitelist = json.load(f)
        if str(user.id) in auto_ban_whitelist.keys():
            return False
        auto_ban_whitelist.update({str(user.id):user.name})
        with open((self.servers / str(guild.id) / "auto_ban_whitelist.json").resolve(), 'w') as f:
            json.dump(auto_ban_whitelist, f)
        return True
    
    def get_server_auto_ban_whitelist(self, guild):
        """Returns the entire server autoban whitelist"""
        self._check_folder(guild)
        with open((self.servers / str(guild.id) / "auto_ban_whitelist.json").resolve(), 'r') as f:
            return json.load(f)

    def get_server_reaction_triggers(self, guild):
        """Gets a dictionary of the emoji reactions available"""
        self._check_folder(guild)
        with open((self.servers / str(guild.id) /"reaction_triggers.json").resolve(), 'r') as f:
            return json.load(f)
    
    def update_server_reaction_triggers(self, guild, reaction_triggers):
        """Updates the reaction triggers dict"""
        self._check_folder(guild)
        with open((self.servers / str(guild.id) /"reaction_triggers.json").resolve(), 'w') as f:
            json.dump(reaction_triggers, f)
            
    def find_in_polder(self, guild, discord_media_link):
        """Finds a message ID corresponding to a piece of media (the link) stored in the polder database. Returns the discord message ID if the associated discord link is found, False otherwise"""
        self._check_folder(guild)
        with open((self.servers / str(guild.id) /"polder.json").resolve(), 'r') as f:
            polder = json.load(f)
            return polder.get(str(discord_media_link), False)
    
    def get_random_polder(self, guild):
        """Gets a random media link from polder"""
        self._check_folder(guild)
        with open((self.servers / str(guild.id) /"polder.json").resolve(), 'r') as f:
            polder = json.load(f)
            return sample(polder.keys(), 1)[0]

    def add_in_polder(self, guild, discord_media_link, message:discord.Message):
        """Adds a link to a piece of media. Returns True if successful, False otherwise."""
        self._check_folder(guild)
        with open((self.servers / str(guild.id) /"polder.json").resolve(), 'r') as f:
            polder = json.load(f)
        if str(discord_media_link) not in polder.keys():
            polder.update({str(discord_media_link): message.id})
            with open((self.servers / str(guild.id) /"polder.json").resolve(), 'w') as f:
                json.dump(polder, f)
            return True
        return False

    def remove_in_polder(self, guild, discord_media_link):
        """Removes a saved polder entry given a discord media link. Returns True if the link was found and removed, False otherwise"""
        self._check_folder(guild)
        with open((self.servers / str(guild.id) /"polder.json").resolve(), 'r') as f:
            polder = json.load(f)
            if polder.pop(str(discord_media_link), False):
                with open((self.servers / str(guild.id) /"polder.json").resolve(), 'w') as f:
                    json.dump(polder, f)
                return True
            return False

    def _create_server_config_folder(self, guild):
        """Makes a server config folder and creates the default parameters"""
        server_folder = self.servers / str(guild.id)
        server_folder.mkdir()
        with open((server_folder / "parameters.json").resolve(), 'x') as f:
            json.dump(self.default_parameters, f)
        with open((server_folder / "auto_ban_whitelist.json").resolve(), 'x') as f:
            json.dump(dict(), f)
        with open((server_folder / "reaction_triggers.json").resolve(), 'x') as f:
            json.dump(dict(), f)
        with open((server_folder / "polder.json").resolve(), 'x') as f:
            json.dump(dict(), f)

    def _check_folder(self, guild):
        """Checks and initializes folder if needed"""
        if not self._server_folder_exists(guild):
            self._create_server_config_folder(guild)

    def _server_folder_exists(self, guild):
        """Checks if a server folder is already stored and returns true or false"""
        return True if ((self.servers / str(guild.id)).exists()) else False