import json
import pathlib
import aiosqlite
import aiofiles
import hashlib
import utils



class ServerConfigHandler:

    def __init__(self):

        
        # possible_parameters = default_parameters.keys()
        # IDK if this line is correct
        self.servers = pathlib.Path("servers")

    # async def get_server_parameters(self, guild):
    #     """Retrieves the current server parameter list"""
    #     await self._check_folder(guild)
    #     async with aiofiles.open((self.servers / str(guild.id) / "parameters.json").resolve(), 'r') as f:
    #         parameters = await f.read()
    #     parameters = json.loads(parameters)
    #     return parameters

        # Would use aiofiles, but can't make __init__ an async method
        with open("default_parameters.json", "r") as f:
            self.default_parameters = json.load(f)

    async def get_server_parameters(self, guild, *parameters):
        """Fetches the server parameters specified in :parameters: for the server :guild:. Returns a dictionary of type "parameter" : value, where value is the corresponding parameter value"""
        params_to_fetch = [parameter for parameter in parameters if parameter in self.default_parameters.keys()]
        selection = f"SELECT parameter, type, value FROM server_parameters INNER JOIN parameters ON parameters.parameter = server_parameters.parameter_name WHERE (server_id = {guild.id} AND parameter IN {tuple(params_to_fetch)})"
        params = dict()
        async with aiosqlite.connect((self.servers / "server_data.db").resolve()) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(selection) as cursor:
                async for row in cursor:
                    params.update({row[0] : utils.convert_type(row[2], row[1])})
        return params
    
    async def update_server_parameters(self, guild, **parameters):
        """Updates the server parameters specified in :parameters: for the server :guild:. values of parameters can be natural objects."""

        params_to_update = [(parameter, utils.string_type(value), guild.id) for parameter, value in parameters if parameter in self.default_parameters.keys()]
        # ASSUMPTION: This assumes that the records already exist. Enforce this on server_load by running an async method called _check_server
        async with aiosqlite.connect((self.servers / "server_data.db").resolve()) as db:
            db.executemany("""UPDATE server_parameters SET parameter_name = (?), value = (?) WHERE (server_id = (?))""", params_to_update)
            db.commit()
        
    # async def update_server_parameters(self, guild, parameters:dict):
    #     """Updates the server parameters"""
    #     await self._check_folder(guild)
    #     parameters = json.dumps(parameters)
    #     async with aiofiles.open((self.servers / str(guild.id) / "parameters.json").resolve(), 'w') as f:
    #         await f.write(parameters)

    async def find_in_server_auto_ban_whitelist(self, guild, user):
        """Finds the specified user in the auto-ban whitelist. Returns True if found, False otherwise."""
        await self._check_folder(guild) 
        async with aiofiles.open((self.servers / str(guild.id) / "auto_ban_whitelist.json").resolve(), 'r') as f:
            auto_ban_whitelist = await f.read()
        auto_ban_whitelist = json.loads(auto_ban_whitelist)
        if str(user.id) in auto_ban_whitelist.keys():
            return True
        return False
    
    async def remove_in_server_auto_ban_whitelist(self, guild, user):
        """Removes a user from the whitelist. Returns True if the user was found and removed, otherwise return False"""
        await self._check_folder(guild)

        async with aiofiles.open((self.servers / str(guild.id) / "auto_ban_whitelist.json").resolve(), 'r+') as f:
            auto_ban_whitelist = await f.read()
        auto_ban_whitelist = json.loads(auto_ban_whitelist)
        if not isinstance(auto_ban_whitelist.pop(str(user.id)), type(None)):
            auto_ban_whitelist = json.dumps(auto_ban_whitelist)
            async with aiofiles.open((self.servers / str(guild.id) / "auto_ban_whitelist.json").resolve(), 'w') as f:
                await f.write(auto_ban_whitelist)
            return True
        return False

    async def add_in_server_auto_ban_whitelist(self, guild, user):
        """Adds a user to the auto-ban whitelist. Returns True if successfully added the user to the whitelist, False if they already are in the whitelist"""
        await self._check_folder(guild)
        async with aiofiles.open((self.servers / str(guild.id) / "auto_ban_whitelist.json").resolve(), 'r+') as f:
            auto_ban_whitelist = await f.read()
        auto_ban_whitelist = json.loads(auto_ban_whitelist)
        if str(user.id) in auto_ban_whitelist.keys():
            return False
        auto_ban_whitelist.update({str(user.id):user.name})
        auto_ban_whitelist = json.dumps(auto_ban_whitelist)
        async with aiofiles.open((self.servers / str(guild.id) / "auto_ban_whitelist.json").resolve(), 'w') as f:
            await f.write(auto_ban_whitelist)
        return True
    
    async def get_server_auto_ban_whitelist(self, guild):
        """Returns the entire server autoban whitelist"""
        await self._check_folder(guild)
        async with aiofiles.open((self.servers / str(guild.id) / "auto_ban_whitelist.json").resolve(), 'r') as f:
            auto_ban_whitelist = await f.read()
        return json.loads(auto_ban_whitelist)

    async def get_server_reaction_triggers(self, guild):
        """Gets a dictionary of the emoji reactions available"""
        await self._check_folder(guild)
        async with aiofiles.open((self.servers / str(guild.id) /"reaction_triggers.json").resolve(), 'r') as f:
            reaction_triggers = await f.read()
        return json.loads(reaction_triggers)
    
    async def update_server_reaction_triggers(self, guild, reaction_triggers:dict):
        """Updates the reaction triggers dict"""
        await self._check_folder(guild)
        reaction_triggers = json.dumps(reaction_triggers)
        async with aiofiles.open((self.servers / str(guild.id) /"reaction_triggers.json").resolve(), 'w') as f:
            await f.write(reaction_triggers)
    

    async def find_in_polder(self, guild, content, message_id=None, author_id=None):
        """Finds the message IDs corresponding to a piece of content from a message stored in the polder database. Returns the discord message IDs and associated authors if the associated content is found, False otherwise"""
        await self._check_folder(guild)
        async with aiosqlite.connect((self.servers / str(guild.id) / "polder.db").resolve()) as db:
            async with db.execute("""SELECT message_id, author_id FROM polder WHERE hash = (?)""", (hashlib.md5(content.encode()).hexdigest())) as cursor:
                ids = await cursor.fetchall()
        return ids
        # with open((self.servers / str(guild.id) /"polder.json").resolve(), 'r') as f:
        #     polder = json.load(f)
        #     return polder.get(str(content), False)
    
    async def get_random_polder(self, guild):
        """Gets a random piece of content from polder. Returns a message_id. If the database is empty, it returns None instead"""
        await self._check_folder(guild)
        async with aiosqlite.connect((self.servers / str(guild.id) / "polder.db").resolve()) as db:
            async with db.execute("""SELECT message_id FROM polder ORDER BY RANDOM() LIMIT 1;""") as cursor:
                message_id = await cursor.fetchall()
        if len(message_id) != 0:
            return message_id[0][0]
        else:
            return None

        # with open((self.servers / str(guild.id) /"polder.json").resolve(), 'r') as f:
        #     polder = json.load(f)
        #     return sample(polder.keys(), 1)[0]
    async def add_in_polder(self, guild, content, message_id, author_id):
        """Adds a piece of content (text or link) to polder table. Returns True if successful, False otherwise."""
        await self._check_folder(guild)
        async with aiosqlite.connect((self.servers / str(guild.id) / "polder.db").resolve()) as db:
            print(message_id, str(hashlib.md5(content.encode()).hexdigest()), author_id)
            await db.execute("""INSERT INTO polder VALUES (?, ?, ?)""", (message_id, str(hashlib.md5(content.encode()).hexdigest()), author_id))
            await db.commit()
        return True
        # with open((self.servers / str(guild.id) /"polder.json").resolve(), 'r') as f:
        #     polder = json.load(f)
        # if str(content) not in polder.keys():
        #     polder.update({str(content): message_id})
        #     with open((self.servers / str(guild.id) /"polder.json").resolve(), 'w') as f:
        #         json.dump(polder, f)
        #     return True
        # return False

    async def remove_in_polder(self, guild, content, message_id=None, author_id=None):
        """Removes a saved polder entry given a piece of content (text or link). Returns True if the content was found and removed, False otherwise"""
        await self._check_folder(guild)
        if content and not (message_id and author_id):
            async with aiosqlite.connect((self.servers / str(guild.id) / "polder.db").resolve()) as db:
                await db.execute("""DELETE FROM polder WHERE content = (?)""", (hashlib.md5(content.encode()).hexdigest()))
                await db.commit()
        ### Implement other variables later
        

        # with open((self.servers / str(guild.id) /"polder.json").resolve(), 'r') as f:
        #     polder = json.load(f)
        #     if polder.pop(str(content), False):
        #         with open((self.servers / str(guild.id) /"polder.json").resolve(), 'w') as f:
        #             json.dump(polder, f)
        #         return True
        #     return False

    async def _create_server_config_folder(self, guild):
        """Makes a server config folder and creates the default parameters"""

        server_folder = self.servers / str(guild.id)
        server_folder.mkdir()
        async with aiofiles.open("default_parameters.json") as f:
            default_parameters = await f.read()
        async with aiofiles.open((server_folder / "parameters.json").resolve(), 'x') as f:
            await f.write(default_parameters)
        async with aiofiles.open((server_folder / "auto_ban_whitelist.json").resolve(), 'x') as f:
            await f.write(json.dumps(dict()))
        async with aiofiles.open((server_folder / "reaction_triggers.json").resolve(), 'x') as f:
            await f.write(json.dumps(dict()))
        async with aiofiles.open((server_folder / "polder.json").resolve(), 'x') as f:
            await f.write(json.dumps(dict()))
        # creating polder table 
        async with aiosqlite.connect((server_folder / "polder.db").resolve()) as db:
                await db.executescript("""CREATE TABLE IF NOT EXISTS polder (
                    message_id INTEGER PRIMARY KEY,
                    hash TEXT,
                    author_id INTEGER
                    )""")
    
    async def _create_db(self):
        """"""
        async with aiosqlite.connect((self.servers / "server_data.db").resolve()) as db:
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS "auto_ban_whitelist" (
	"server_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id")
);
CREATE TABLE IF NOT EXISTS "commands" (
	"command"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("command")
);
CREATE TABLE IF NOT EXISTS "emoji_triggers" (
	"server_id"	INTEGER NOT NULL,
	"trigger_phrase"	TEXT NOT NULL,
	"emoji_id"	INTEGER NOT NULL,
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id")
);
CREATE TABLE IF NOT EXISTS "parameters" (
	"parameter"	TEXT NOT NULL UNIQUE,
	"type"	TEXT NOT NULL,
	PRIMARY KEY("parameter")
);
CREATE TABLE IF NOT EXISTS "polder" (
	"server_id"	INTEGER NOT NULL,
	"message_id"	INTEGER NOT NULL UNIQUE,
	"content"	INTEGER NOT NULL,
	"author_id"	INTEGER,
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id"),
	PRIMARY KEY("message_id")
);
CREATE TABLE IF NOT EXISTS "server_commands" (
	"server_id"	INTEGER NOT NULL,
	"command_name"	TEXT NOT NULL,
	"role_id"	INTEGER NOT NULL,
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id"),
	FOREIGN KEY("command_name") REFERENCES "commands"("command")
);
CREATE TABLE IF NOT EXISTS "server_parameters" (
	"server_id"	INTEGER NOT NULL,
	"parameter_name"	TEXT NOT NULL,
	"value"	TEXT NOT NULL,
	FOREIGN KEY("parameter_name") REFERENCES "parameters"("parameter"),
	FOREIGN KEY("server_id") REFERENCES "servers"
);
CREATE TABLE IF NOT EXISTS "servers" (
	"server_id"	INTEGER NOT NULL UNIQUE,
	PRIMARY KEY("server_id")
);
CREATE TABLE IF NOT EXISTS "shitposting_channels" (
	"server_id"	INTEGER NOT NULL,
	"channel_id"	INTEGER NOT NULL,
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id")
);
CREATE TABLE IF NOT EXISTS "text_triggers" (
	"server_id"	INTEGER NOT NULL,
	"trigger_phrase"	TEXT NOT NULL,
	"message"	TEXT NOT NULL,
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id")
);
                """
            )
            await db.commit()

    # async def _check_folder(self, guild):
    #     """Checks and initializes folder if needed"""
    #     if not self._server_folder_exists(guild):
    #         await self._create_server_config_folder(guild)

    # def _server_folder_exists(self, guild):
    #     """Checks if a server folder is already stored and returns true or false"""
    #     return True if ((self.servers / str(guild.id)).exists()) else False