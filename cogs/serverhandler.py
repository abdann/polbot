import json
import asyncio
import pathlib
import aiosqlite
import utils


class ServerConfigHandler:

    def __init__(self):
        self.serverdata = (pathlib.Path("servers") / "server_data.db").resolve()
        # Would use aiofiles, but can't make __init__ an async method
        with open("default_parameters.json", "r") as f:
            self.default_parameters = json.load(f)
    
    async def get_server_parameters(self, guild, *parameters) -> dict:
        """Fetches the server parameters specified in :parameters: for the server :guild:. Returns a dictionary of type "parameter" : value, where value is the corresponding parameter value. if "a" is passed, all server parameters are returned"""
        await self._checks(guild)
        if "a" in parameters:
            params_to_get = list(self.default_parameters.keys())
        else:
            params_to_get = [param for param in parameters if (param in self.default_parameters.keys())] # sanitizes request
        selection = f"SELECT {utils.convert_list_to_sql_select(params_to_get)} FROM parameters WHERE (server_id = ?)"
        async with aiosqlite.connect(self.serverdata) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(selection, (guild.id,)) as cursor:
                row = await cursor.fetchone()
                return {param : row[param] for param in params_to_get} # Assume parameters have all been initialized (no null columns)
    
    async def update_server_parameters(self, guild, **parameters):
        """Updates the server parameters specified in :parameters: for the server :guild:. values of parameters can be natural objects."""
        await self._checks(guild)
        # First get the valid parameters dict
        valid_parameters = {parameter : value for parameter, value in parameters.items() if parameter in self.default_parameters.keys()} #sanitizes parameters
        # Then build the update query
        sql_update = utils.convert_dict_to_sql_update(list(valid_parameters.keys()))
        valid_parameters.update({"server_id" : guild.id}) # adding the server_id for the WHERE clause
        async with aiosqlite.connect(self.serverdata) as db:
            await db.execute(f"UPDATE parameters SET {sql_update} WHERE server_id = :server_id", valid_parameters)
            await db.commit()

    async def find_in_server_auto_ban_whitelist(self, guild, user) -> bool:
        """Finds the specified user in the auto-ban whitelist. Returns True if found, False otherwise."""
        await self._checks(guild)
        async with aiosqlite.connect(self.serverdata) as db:
            async with db.execute("""SELECT user_id FROM auto_ban_whitelist WHERE (server_id = (?) AND user_id = (?))""", (guild.id, user.id)) as cursor:
                existing_rows = await cursor.fetchone()
        if existing_rows is not None:
            return True
        else:
            return False
    
    async def get_server_auto_ban_whitelist(self, guild):
        """Gets the entire auto ban whitelist for a server"""
        await self._checks(guild)
        whitelisted_users = list()
        async with aiosqlite.connect(self.serverdata) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""SELECT user_id FROM auto_ban_whitelist WHERE (server_id = (?))""", (guild.id,)) as cursor:
                async for row in cursor:
                    whitelisted_users.append(row[0])
        return whitelisted_users
    
    async def remove_in_server_auto_ban_whitelist(self, guild, user) -> bool:
        """Removes a user from the whitelist. Returns True if the user was found and removed, otherwise return False"""
        await self._checks(guild)
        async with aiosqlite.connect(self.serverdata) as db:
            # Checks if the user is not in the ban whitelist
            async with db.execute("""SELECT user_id FROM auto_ban_whitelist WHERE (server_id = (?) AND user_id = (?))""", (guild.id, user.id)) as cursor:
                existing_rows = await cursor.fetchone()
            if existing_rows is None:
                return False # Indicates that the user is not already whitelisted for that server and was not found
            # Delete the entry
            await db.execute("""DELETE FROM auto_ban_whitelist WHERE (server_id = (?) AND user_id = (?))""", (guild.id, user.id))
            await db.commit()
            return True

    async def add_in_server_auto_ban_whitelist(self, guild, user) -> bool:
        """Adds a user to the auto-ban whitelist. Returns True if successfully added the user to the whitelist, False if they already are in the whitelist"""
        await self._checks(guild)
        async with aiosqlite.connect(self.serverdata) as db:
            # Checks if the user is already in the ban whitelist
            async with db.execute("""SELECT user_id FROM auto_ban_whitelist WHERE (server_id = (?) AND user_id = (?))""", (guild.id, user.id)) as cursor:
                existing_rows = await cursor.fetchone()
            if existing_rows is not None:
                return False # Indicates that the user is already whitelisted for that server
            # If the entry doesn't already exist, then insert it
            await db.execute("""INSERT INTO auto_ban_whitelist VALUES ((?), (?))""", (guild.id, user.id))
            await db.commit()
            return True        

    async def get_text_triggers(self, guild) -> dict:
        """Gets a dictionary of the text triggers set for that server"""
        await self._checks(guild)
        async with aiosqlite.connect(self.serverdata) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""SELECT trigger_phrase, message FROM text_triggers WHERE (server_id = (?))""", (guild.id,)) as cursor:
                text_triggers = {row[0] : row[1] async for row in cursor} # asserts that trigger_phrases are unique for a given server by building a dictionary
        return text_triggers
    
    async def add_text_trigger(self, guild, trigger_phrase:str, message:str) -> bool:
        """Adds a text trigger for a server. Returns True if the trigger was added and False if the trigger is already present"""
        await self._checks(guild)
        async with aiosqlite.connect(self.serverdata) as db:
            # Checks if the trigger is already set
            async with db.execute("""SELECT trigger_phrase, message FROM text_triggers WHERE (server_id = (?) AND trigger_phrase = (?))""", (guild.id, trigger_phrase)) as cursor:
                existing_rows = await cursor.fetchone()
            if existing_rows is not None:
                return False # Indicates that the specific combination is already set for that server
            # If the entry doesn't already exist, then insert it
            await db.execute("""INSERT INTO text_triggers VALUES ((?), (?), (?))""", (guild.id, trigger_phrase, message))
            await db.commit()
        return True

    async def remove_text_trigger(self, guild, **kwargs) -> bool:
        """Removes a text trigger :trigger_phrase: or :message: for a server. Returns True if the trigger was removed and False if the trigger was not found"""
        await self._checks(guild)
        if kwargs is None:
            raise ValueError("Must pass at least one argument")
        valid_columns = ["trigger_phrase", "message"] # allowed keywords
        params = {k : v for k, v in kwargs.items() if k in valid_columns and v is not None} # sanitizes kwargs
        conditions = utils.build_sql_and(list(params.keys())) # build or statement for passed params
        select_statement = f"SELECT {utils.convert_list_to_sql_select(list(params.keys()))} FROM text_triggers WHERE server_id = :server_id AND {conditions}" # build select statement
        params.update({"server_id" : guild.id}) # update params for db.execute's second parameter
        async with aiosqlite.connect(self.serverdata) as db:
            async with db.execute(select_statement, params) as cursor:
                existing_trigger = await cursor.fetchone()
            if existing_trigger is None:
                return False
            delete_statement = f"DELETE FROM text_triggers WHERE server_id = :server_id AND {conditions}" #Build delete statement
            await db.execute(delete_statement, params)
            await db.commit()
            return True

    async def get_emoji_reaction_triggers(self, guild) -> dict:
        """Gets a dictionary of the emoji reaction triggers set for that server"""
        await self._checks(guild)
        async with aiosqlite.connect(self.serverdata) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""SELECT trigger_phrase, emoji FROM emoji_triggers WHERE (server_id = (?))""", (guild.id,)) as cursor:
                emoji_reaction_triggers = {row[0] : utils.get_emoji(guild, row[1]) async for row in cursor} # asserts the one trigger policy
        return emoji_reaction_triggers

    async def add_emoji_reaction_trigger(self, guild, trigger_phrase:str, emoji_like) -> bool:
        """Adds an emoji reaction trigger for a server. Returns True if the trigger was added and False if the trigger is already present"""
        await self._checks(guild)
        emoji_like = utils.stringify_emoji(emoji_like)
        async with aiosqlite.connect(self.serverdata) as db:
            # Checks if the trigger is already set
            async with db.execute("""SELECT trigger_phrase, emoji FROM emoji_triggers WHERE (server_id = (?) AND trigger_phrase = (?))""", (guild.id, trigger_phrase)) as cursor:
                existing_rows = await cursor.fetchone()
            if existing_rows is not None:
                return False # Indicates that the specific combination is already set for that server
            # If the entry doesn't already exist, then insert it
            await db.execute("""INSERT INTO emoji_triggers VALUES ((?), (?), (?))""", (guild.id, trigger_phrase, emoji_like))
            await db.commit()
            return True

    async def remove_emoji_reaction_trigger(self, guild, **kwargs) -> bool:
        """Removes an emoji reaction trigger given the :trigger_phrase: and/or :emoji: for a server. Returns True if the trigger was removed and False if the trigger was not found"""
        await self._checks(guild)
        if kwargs is None:
            raise ValueError("Must pass at least one argument")
        valid_columns = ["trigger_phrase", "emoji"] # allowed keywords
        params = {k : v for k, v in kwargs.items() if k in valid_columns and v is not None} # sanitizes kwargs
        conditions = utils.build_sql_and(list(params.keys())) # build or statement
        if "emoji" in params.keys(): # only done if emoji is part of parameters
            params.update({"emoji" : utils.stringify_emoji(params.get("emoji"))})
        select_statement = f"SELECT {utils.convert_list_to_sql_select(list(params.keys()))} FROM emoji_triggers WHERE server_id = :server_id AND {conditions}" # build select statement
        params.update({"server_id" : guild.id}) # update for db.execute's second parameter
        async with aiosqlite.connect(self.serverdata) as db:
            async with db.execute(select_statement, params) as cursor:
                existing_trigger = await cursor.fetchone()
            if existing_trigger is None:
                return False
            delete_statement = f"DELETE FROM emoji_triggers WHERE server_id = :server_id AND {conditions}" # build delete statement
            await db.execute(delete_statement, params)
            await db.commit()
            return True
    
    async def get_random_polder(self, guild):
        """Gets a random piece of content from polder. Returns a string if found, else None."""
        await self._checks(guild)
        async with aiosqlite.connect(self.serverdata) as db:
            async with db.execute("""SELECT content FROM polder WHERE server_id = (?) ORDER BY RANDOM() LIMIT 1""", (guild.id,)) as cursor:
                random_row = await cursor.fetchone()
        if random_row is not None: # Found content for that server
            return random_row[0]
        else: # RARE CASE where polder is empty for that server
            return None

    async def add_in_polder(self, guild, *, content:str, message_id:int, author_id:int):
        """Adds a piece of content (text or link) to polder table. """
        await self._checks(guild)
        async with aiosqlite.connect(self.serverdata) as db:
            await db.execute("""INSERT INTO polder VALUES (?, ?, ?, ?)""", (guild.id, message_id, content, author_id))
            await db.commit()

    async def remove_in_polder(self, guild, **kwargs) -> bool:
        """Removes a saved polder entry given a piece of content (text or link). Returns True if the content was found and removed, False otherwise"""
        await self._checks(guild)
        if kwargs is None:
            raise ValueError("Must pass at least one argument")
        valid_columns = ["content", "message_id", "author_id"] # allowed keywords
        
        params = {k : v for k, v in kwargs.items() if k in valid_columns and v is not None} # sanitizes kwargs
        conditions = utils.build_sql_and(list(params.keys())) # build or statement for passed params
        select_statement = f"SELECT {utils.convert_list_to_sql_select(list(params.keys()))} FROM polder WHERE server_id = :server_id AND {conditions}" # build select statement
        params.update({"server_id" : guild.id}) # update params for db.execute's second parameter
        async with aiosqlite.connect(self.serverdata) as db:
            async with db.execute(select_statement, params) as cursor:
                existing_row = await cursor.fetchone()
            if existing_row is None:
                return False
            delete_statement = f"DELETE FROM polder WHERE server_id = :server_id AND {conditions}" #Build delete statement
            await db.execute(delete_statement, params)
            await db.commit()
            return True

    async def add_in_shitposting_channels(self, guild, channel_id:int) -> bool:
        """Adds a shitposting channel for a server. Returns True if the channel was added and False if the channel is already present"""
        await self._checks(guild)
        async with aiosqlite.connect(self.serverdata) as db:
            async with db.execute("SELECT channel_id FROM shitposting_channels WHERE channel_id = ?", (channel_id,)) as cursor:
                existing_row = await cursor.fetchone()
            if existing_row is not None:
                return False
            await db.execute("INSERT INTO shitposting_channels VALUES (?, ?)", (guild.id, channel_id))
            await db.commit()
            return True
    
    async def remove_in_shitposting_channels(self, guild, channel_id:int) -> bool:
        await self._checks(guild)
        async with aiosqlite.connect(self.serverdata) as db:
            # Checks if the channel is not in the table
            async with db.execute("""SELECT channel_id FROM shitposting_channels WHERE server_id = ? AND channel_id = ?""", (guild.id, channel_id)) as cursor:
                existing_rows = await cursor.fetchone()
            if existing_rows is None:
                return False # Indicates that the channel is not already present for that server and was not found
            # Delete the entry
            await db.execute("""DELETE FROM shitposting_channels WHERE (server_id = (?) AND channel_id = (?))""", (guild.id, channel_id))
            await db.commit()
            return True
    
    async def find_in_shitposting_channels(self, guild, channel_id:int) -> bool:
        await self._checks(guild)
        async with aiosqlite.connect(self.serverdata) as db:
            async with db.execute("""SELECT channel_id FROM shitposting_channels WHERE (server_id = (?) AND channel_id = (?))""", (guild.id, channel_id)) as cursor:
                existing_rows = await cursor.fetchone()
        if existing_rows is not None:
            return True
        else:
            return False
    
    async def get_shitposting_channels(self, guild) -> list:
        await self._checks(guild)
        shitposting_channels = list()
        async with aiosqlite.connect(self.serverdata) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""SELECT channel_id FROM shitposting_channels WHERE (server_id = (?))""", (guild.id,)) as cursor:
                async for row in cursor:
                    shitposting_channels.append(row[0])
        return shitposting_channels

    async def _create_db(self):
        """Creates the database if one doesn't already exist."""
        async with aiosqlite.connect(self.serverdata) as db:
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS "auto_ban_whitelist" (
	"server_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "emoji_triggers" (
	"server_id"	INTEGER NOT NULL,
	"trigger_phrase"	TEXT NOT NULL,
	"emoji"	TEXT NOT NULL,
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "parameters" (
	"server_id"	INTEGER NOT NULL,
	"min_account_age"	INTEGER NOT NULL,
	"new_auto_ban"	INTEGER NOT NULL,
	"lockdown"	INTEGER NOT NULL,
	"polder_channel_id"	INTEGER,
	"polder"	INTEGER NOT NULL,
	"random_polder_posts"	INTEGER NOT NULL,
	"random_text_posts"	INTEGER NOT NULL,
	"shitpost_probability"	INTEGER NOT NULL,
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id") ON DELETE CASCADE,
	PRIMARY KEY("server_id")
);
CREATE TABLE IF NOT EXISTS "polder" (
	"server_id"	INTEGER NOT NULL,
	"message_id"	INTEGER NOT NULL,
	"content"	TEXT NOT NULL,
	"author_id"	INTEGER,
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "servers" (
	"server_id"	INTEGER NOT NULL,
	PRIMARY KEY("server_id")
);
CREATE TABLE IF NOT EXISTS "shitposting_channels" (
	"server_id"	INTEGER NOT NULL,
	"channel_id"	INTEGER NOT NULL,
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "text_triggers" (
	"server_id"	INTEGER NOT NULL,
	"trigger_phrase"	TEXT NOT NULL,
	"message"	TEXT NOT NULL,
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id") ON DELETE CASCADE
);
                """
            )
            await db.commit()

    async def _initialize_server_parameters(self, guild):
        """Initializes a server's parameters to the default values"""
        async with aiosqlite.connect(self.serverdata) as db:
            await db.execute("""INSERT INTO servers VALUES (?)""", (guild.id,))
            insert_dict = self.default_parameters
            insert_dict.update({"server_id" : guild.id})
            insert = utils.convert_dict_to_sql_insert(insert_dict)
            await db.execute(f"INSERT INTO parameters {insert[0]} VALUES {insert[1]}", insert_dict)
            await db.commit()
    
    async def _check_server(self, guild):
        """Checks if a guild is in the servers table. If not, initialize server parameters"""
        async with aiosqlite.connect(self.serverdata) as db:
            async with db.execute("""SELECT server_id FROM servers WHERE (server_id = (?))""", (guild.id,)) as cursor:
                server = await cursor.fetchone()
        if server is None:
            await self._initialize_server_parameters(guild)
            return
    
    async def _check_db(self):
        """Checks and initializes database if needed"""
        if not self._db_exists():
            await self._create_db()

    def _db_exists(self) -> bool:
        """Checks if the database exists"""
        return True if (self.serverdata.exists()) else False

    async def _checks(self, guild):
        await self._check_db()
        await self._check_server(guild)

if __name__ == "__main__":
    class Guild:
        def __init__(self, id:int) -> None:
            self.id = id
    
    class User:
        def __init__(self, id:int) -> None:
            self.id = id
    
    async def main():
        """Testing"""
        pcm = Guild(123)
        bob = User(456)
        not_bob = User(654)
        alice = User(546)
        servers = ServerConfigHandler()
        await servers._check_db() #Works
        await servers._check_server(pcm) #works

        # Testing polder
        print(await servers.get_random_polder(pcm)) #should be None
        await servers.add_in_polder(pcm, content="hello", message_id=0, author_id=bob.id)
        await servers.add_in_polder(pcm, content="hello", message_id=1, author_id=bob.id)
        await servers.add_in_polder(pcm, content="hello", message_id=2, author_id=bob.id)
        await servers.add_in_polder(pcm, content="hello", message_id=3, author_id=alice.id)
        await servers.add_in_polder(pcm, content="hello", message_id=4, author_id=alice.id)
        await servers.add_in_polder(pcm, content="hello citizens", message_id=5, author_id=alice.id)
        await servers.add_in_polder(pcm, content="hello citizens", message_id=6, author_id=alice.id)
        await servers.add_in_polder(pcm, content="hello citizens", message_id=7, author_id=alice.id)
        await servers.add_in_polder(pcm, content="hello citizens", message_id=8, author_id=bob.id)

        print(await servers.get_random_polder(pcm))
        print(await servers.get_random_polder(pcm))
        print(await servers.get_random_polder(pcm))
        print(await servers.get_random_polder(pcm))
        print(await servers.get_random_polder(pcm))

        print(await servers.remove_in_polder(pcm, content="hello", message_id=0)) #remove 1 entry
        print(await servers.remove_in_polder(pcm, content="hello", author_id=alice.id)) #remove 2 entries
        print(await servers.remove_in_polder(pcm, content="hello")) #remove 2 entries
        print(await servers.remove_in_polder(pcm, author_id=alice.id)) #remove 3 entries
        #should be one entry in polder remaining

        print(await servers.add_in_shitposting_channels(pcm, 123)) #should be true
        print(await servers.add_in_shitposting_channels(pcm, 456)) #should be true
        print(await servers.add_in_shitposting_channels(pcm, 789)) #should be true
        print(await servers.add_in_shitposting_channels(pcm, 789)) #should be false
        print(await servers.get_shitposting_channels(pcm)) #should get list of channels
        print(await servers.find_in_shitposting_channels(pcm, 123)) #should be true
        print(await servers.remove_in_shitposting_channels(pcm, 123)) # should be true
        print(await servers.remove_in_shitposting_channels(pcm, 123)) # should be false
        print(await servers.find_in_shitposting_channels(pcm, 123)) #should be false

        print(await servers.add_text_trigger(pcm, "pedo", "kill all pedos NOW")) #should be true
        print(await servers.add_text_trigger(pcm, "pedo", "kill all pedos NOW")) #should be false
        print(await servers.add_text_trigger(pcm, "pedo", "lol")) #should be true
        print(await servers.add_text_trigger(pcm, "p", "kill all pedos NOW")) #should be true
        print(await servers.get_text_triggers(pcm)) #should be dict
        print(await servers.remove_text_trigger(pcm, trigger_phrase="pedo", message="kill all pedos NOW")) #should be true and remove one entry
        print(await servers.get_text_triggers(pcm)) #check output
        print(await servers.add_text_trigger(pcm, "pedo", "kill all pedos NOW")) #should be true
        print(await servers.remove_text_trigger(pcm, trigger_phrase="pedo")) #should get rid of two entries
        print(await servers.get_text_triggers(pcm))#one entry should remain





    
    asyncio.run(main())