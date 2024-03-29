import json
import asyncio
import typing
import datetime

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import sqlalchemy.future

import utils
from servers import models



class ServerConfigHandler:

    def __init__(self, database_url:str):
        self.engine = create_async_engine(database_url, future=True)
        self.Session = sqlalchemy.orm.sessionmaker(self.engine, class_=AsyncSession, future=True)
        # Would use aiofiles, but can't make __init__ an async method
        with open("default_parameters.json", "r") as f:
            self.default_parameters:dict = json.load(f)
        self.text_cooldown:typing.Dict[str, datetime.datetime] = dict()
    
    async def get_server_parameters(self, guild, *parameters) -> dict:
        """Fetches the server parameters specified in :parameters: for the server :guild:. Returns a dictionary of type "parameter" : value, where value is the corresponding parameter value. if "a" is passed, all server parameters are returned"""
        await self._checks(guild)
        if "a" in parameters:
            params_to_get = list(self.default_parameters.keys())
        else:
            params_to_get = [param for param in parameters if (param in self.default_parameters.keys())] # sanitizes request
        async with self.Session() as session:
            results = await session.execute(
                sqlalchemy.select(
                    models.Parameter.parameters
                ).
                where(
                    models.Parameter.server_id == guild.id
                )
            )
            results = results.scalars().first()
            return {k : results.get(k) for k in params_to_get}
    
    async def update_server_parameters(self, guild, **parameters):
        """Updates the server parameters specified in :parameters: for the server :guild:. values of parameters can be natural objects."""
        await self._checks(guild)
        # First get the valid parameters dict
        valid_parameters = {parameter : value for parameter, value in parameters.items() if parameter in self.default_parameters.keys()} #sanitizes parameters
        # Then build the update query
        async with self.Session() as session:
            results = await session.execute(
                sqlalchemy.select(
                    models.Parameter.parameters
                ).
                where(
                    models.Parameter.server_id == guild.id
                )
            )
            results = results.scalars().first()
            results.update(valid_parameters)
            await session.execute(
                sqlalchemy.update(models.Parameter).
                where(models.Parameter.server_id == guild.id).
                values(parameters=results)
            )
            await session.commit()

    async def find_in_server_auto_ban_whitelist(self, guild, user) -> True:
        """Finds the specified user in the auto-ban whitelist. Returns True if found, False otherwise."""
        await self._checks(guild)
        async with self.Session() as session:
            user_found = await session.get(models.AutoBanWhitelist, {"server_id" : guild.id, "user_id" : user.id})
            return True if user_found else False
            
    async def get_server_auto_ban_whitelist(self, guild) -> typing.List[int]:
        """Gets the entire auto ban whitelist for a server"""
        await self._checks(guild)
        async with self.Session() as session:
            selection = await session.execute(
                sqlalchemy.future.select(models.AutoBanWhitelist.user_id).
                where(models.AutoBanWhitelist.server_id == guild.id)
            )
            return selection.scalars().all()
    
    async def remove_in_server_auto_ban_whitelist(self, guild, user) -> bool:
        """Removes a user from the whitelist. Returns True if the user was found and removed, otherwise return False"""
        await self._checks(guild)
        async with self.Session() as session:
            found_user = await session.get(models.AutoBanWhitelist, {"server_id" : guild.id, "user_id" : user.id})
            if not found_user:
                return False
            await session.delete(found_user)
            await session.commit()
            return True

    async def add_in_server_auto_ban_whitelist(self, guild, user) -> bool:
        """Adds a user to the auto-ban whitelist. Returns True if successfully added the user to the whitelist, False if they already are in the whitelist"""
        await self._checks(guild)
        async with self.Session() as session:
            found_user = await session.get(models.AutoBanWhitelist, {"server_id" : guild.id, "user_id" : user.id})
            if found_user:
                return False
            session.add(models.AutoBanWhitelist(server_id=guild.id, user_id=user.id))
            await session.commit()
            return True

    async def get_text_triggers(self, guild) -> typing.Dict[str, str]:
        """Gets a dictionary of the text triggers set for that server"""
        await self._checks(guild)
        async with self.Session() as session:
            selection = await session.execute(
                sqlalchemy.future.select(models.TextTrigger.trigger_phrase, models.TextTrigger.message).
                where(models.TextTrigger.server_id == guild.id)
            ) # Must list each column to select to get row objects rather than ORM objects, otherwise return statement raises KeyError
            return {row['trigger_phrase'] : row['message'] for row in selection.fetchall()}
            
    async def add_text_trigger(self, guild, trigger_phrase:str, message:str) -> bool:
        """Adds a text trigger for a server. Returns True if the trigger was added and False if the trigger is already present"""
        await self._checks(guild)
        async with self.Session() as session:
            found_text_trigger = await session.get(models.TextTrigger, {"server_id" : guild.id, "trigger_phrase" : trigger_phrase, "message" : message})
            if found_text_trigger is not None:
                return False
            session.add(models.TextTrigger(server_id=guild.id, trigger_phrase=trigger_phrase, message=message))
            await session.commit()
            return True

    async def remove_text_trigger(self, guild, **kwargs) -> bool:
        """Removes a text trigger :trigger_phrase: or :message: for a server. Returns True if the trigger was removed and False if the trigger was not found"""
        await self._checks(guild)
        if kwargs is None:
            raise ValueError("Must pass at least one argument")
        valid_columns = ["trigger_phrase", "message"] # allowed keywords
        criteria = {k : v for k, v in kwargs.items() if k in valid_columns and v is not None} # sanitizes kwargs
        async with self.Session() as session:
            selection = sqlalchemy.future.select(models.TextTrigger).\
                where(*[sqlalchemy.Column(column) == value for column, value in criteria.items()],
                 models.TextTrigger.server_id == guild.id) #This building column BS is weird and deprecated, I should find a better way
            results = await session.execute(selection)
            results = results.scalars().all()
            if not results:
                return False
            await session.execute(
                sqlalchemy.delete(models.TextTrigger).
                where(*[sqlalchemy.Column(column) == value for column, value in criteria.items()],
                 models.TextTrigger.server_id == guild.id))
            await session.commit()
            return True

    async def get_emoji_reaction_triggers(self, guild) -> typing.Dict[str, utils.Emoji]:
        """Gets a dictionary of the emoji reaction triggers set for that server"""
        await self._checks(guild)    
        async with self.Session() as session:
            selection = await session.execute(
                sqlalchemy.future.select(models.EmojiTrigger.trigger_phrase, models.EmojiTrigger.emoji).
                where(models.EmojiTrigger.server_id == guild.id)
            )
            emoji_triggers = selection.fetchall()
            return {emoji_trigger['trigger_phrase'] : utils.get_emoji(guild, emoji_trigger['emoji'])  for emoji_trigger in emoji_triggers}

    async def add_emoji_reaction_trigger(self, guild, trigger_phrase:str, emoji_like) -> bool:
        """Adds an emoji reaction trigger for a server. Returns True if the trigger was added and False if the trigger is already present"""
        await self._checks(guild)
        emoji_like = utils.stringify_emoji(emoji_like)
        async with self.Session() as session:
            selection = await session.get(models.EmojiTrigger, {'server_id' : guild.id, 'trigger_phrase' : trigger_phrase, 'emoji' : emoji_like})
            if selection is not None:
                return False
            session.add(models.EmojiTrigger(server_id=guild.id, trigger_phrase=trigger_phrase, emoji=emoji_like))
            await session.commit()
            return True

    async def remove_emoji_reaction_trigger(self, guild, **kwargs) -> bool:
        """Removes an emoji reaction trigger given the :trigger_phrase: and/or :emoji: for a server. Returns True if the trigger was removed and False if the trigger was not found"""
        await self._checks(guild)
        if kwargs is None:
            raise ValueError("Must pass at least one argument")
        valid_columns = ["trigger_phrase", "emoji"] # allowed keywords
        params = {k : v for k, v in kwargs.items() if k in valid_columns and v is not None} # sanitizes kwargs
        if "emoji" in params.keys(): # only done if emoji is part of parameters
            params.update({"emoji" : utils.stringify_emoji(params.get("emoji"))})
        async with self.Session() as session:
            selection = await session.execute(
                sqlalchemy.future.select(models.EmojiTrigger).
                where(*[sqlalchemy.Column(column) == value for column, value in params.items()],
                 models.EmojiTrigger.server_id == guild.id)
            )
            selection = selection.scalars().all()
            if not selection:
                return False
            await session.execute(
                sqlalchemy.delete(models.EmojiTrigger).
                where(*[sqlalchemy.Column(column) == value for column, value in params.items()],
                 models.EmojiTrigger.server_id == guild.id))
            await session.commit()
            return True
    
    async def get_random_polder(self, guild) -> typing.Union[typing.Tuple[int, int], None]:
        """Gets a random piece of content from polder. Returns a tuple of (message_id, channel_id) if found, else None."""
        await self._checks(guild)
        async with self.Session() as session:
            random_row = await session.execute(
                sqlalchemy.future.select(models.Polder.message_id, models.Polder.channel_id).
                where(models.Polder.server_id == guild.id).
                order_by(sqlalchemy.func.random()).limit(1)
            )
            random_row = random_row.fetchone()
            if random_row:
                return random_row
            else:
                return None

    async def add_in_polder(self, guild, *, content:str, message_id:int, author_id:int, channel_id:int):
        """Adds a piece of content (text or link) to polder table. """
        await self._checks(guild)
        async with self.Session() as session:
            session.add(
                models.Polder(
                    server_id=guild.id,
                     content=content,
                      message_id=message_id,
                       author_id=author_id,
                        channel_id=channel_id))
            await session.commit()

    async def remove_in_polder(self, guild, **kwargs) -> bool:
        """Removes a saved polder entry given a piece of content (text or link). Returns True if the content was found and removed, False otherwise"""
        await self._checks(guild)
        if kwargs is None:
            raise ValueError("Must pass at least one argument")
        valid_columns = ["content", "message_id", "author_id, channel_id"] # allowed keywords
        params = {k : v for k, v in kwargs.items() if k in valid_columns and v is not None} # sanitizes kwargs
        async with self.Session() as session:
            selection = sqlalchemy.future.select(models.Polder).\
                where(*[sqlalchemy.Column(column) == value for column, value in params.items()],
                 models.Polder.server_id == guild.id) #This building column BS is weird and deprecated, I should find a better way
            results = await session.execute(selection)
            results = results.scalars().all()
            if results is None:
                return False
            await session.execute(
                sqlalchemy.delete(models.Polder).
                where(*[sqlalchemy.Column(column) == value for column, value in params.items()],
                 models.Polder.server_id == guild.id))
            await session.commit()
            return True

    async def add_in_shitposting_channels(self, guild, channel_id:int) -> bool:
        """Adds a shitposting channel for a server. Returns True if the channel was added and False if the channel is already present"""
        await self._checks(guild)
        async with self.Session() as session:
            found_channel = await session.get(models.ShitpostingChannel, {"channel_id" : channel_id})
            if found_channel is not None:
                return False
            session.add(models.ShitpostingChannel(server_id=guild.id, channel_id=channel_id))
            await session.commit()
            return True
    
    async def remove_in_shitposting_channels(self, guild, channel_id:int) -> bool:
        await self._checks(guild)
        async with self.Session() as session:
            found_channel = await session.get(models.ShitpostingChannel, {"channel_id" : channel_id})
            if found_channel is None:
                return False
            await session.delete(found_channel)
            await session.commit()
            return True
    
    async def find_in_shitposting_channels(self, guild, channel_id:int) -> bool:
        await self._checks(guild)
        async with self.Session() as session:
            found_channel = await session.get(models.ShitpostingChannel, {"channel_id" : channel_id})
            return True if found_channel is not None else False
    
    async def get_shitposting_channels(self, guild) -> typing.List[int]:
        await self._checks(guild)
        async with self.Session() as session:
            results = await session.execute(
                sqlalchemy.select(models.ShitpostingChannel.channel_id).
                where(models.ShitpostingChannel.server_id == guild.id)
            )
            return results.scalars().all()

    async def add_family_friendly_channel(self, guild, channel) -> bool:
        await self._checks(guild)
        async with self.Session() as session:
            found_channel = await session.get(models.FamilyFriendlyChannel, {"channel_id" : channel.id})
            if found_channel is not None:
                return False
            session.add(models.FamilyFriendlyChannel(server_id=guild.id, channel_id=channel.id))
            await session.commit()
            return True
    
    async def remove_family_friendly_channel(self, guild, channel) -> bool:
        await self._checks(guild)
        async with self.Session() as session:
            found_channel = await session.get(models.FamilyFriendlyChannel, {"channel_id" : channel.id})
            if found_channel is None:
                return False
            await session.delete(found_channel)
            await session.commit()
            return True

    async def find_in_family_friendly_channels(self, guild, channel) -> bool:
        await self._checks(guild)
        async with self.Session() as session:
            found_channel = await session.get(models.FamilyFriendlyChannel, {"channel_id" : channel.id})
            return True if found_channel is not None else False

    async def get_family_friendly_channels(self, guild) -> typing.List[int]:
        await self._checks(guild)
        async with self.Session() as session:
            results = await session.execute(
                sqlalchemy.select(models.FamilyFriendlyChannel.channel_id).
                where(models.FamilyFriendlyChannel.server_id == guild.id)
            )
            return results.scalars().all()
    
    async def add_banned_word(self, guild, word:str):
        await self._checks(guild)
        async with self.Session() as session:
            found_banned_word = await session.get(models.ProhibitedWord, {"server_id" : guild.id, "word" : word})
            if found_banned_word is not None:
                return False
            session.add(models.ProhibitedWord(server_id=guild.id, word=word))
            await session.commit()
            return True

    async def remove_banned_word(self, guild, word:str) -> bool:
        await self._checks(guild)
        async with self.Session() as session:
            found_word = await session.get(models.ProhibitedWord, {"server_id" : guild.id, "word" : word})
            if found_word is None:
                return False
            await session.delete(found_word)
            await session.commit()
            return True

    async def get_banned_words(self, guild) -> typing.List[str]:
        await self._checks(guild)
        async with self.Session() as session:
            results = await session.execute(
                sqlalchemy.select(models.ProhibitedWord.word).
                where(models.ProhibitedWord.server_id == guild.id)
            )
            return results.scalars().all()

    async def _check_server(self, guild):
        """Checks if a guild is in the servers table. If not, initialize server parameters"""
        async with self.Session() as session:
            selection = await session.execute(
                sqlalchemy.select(models.Server).where(models.Server.server_id == guild.id))
            selection = selection.scalars().first()
            if selection is None:
                server = models.Parameter(server_id=guild.id, parameters=self.default_parameters)
                session.add(server)
                await session.commit()
    
    async def _check_db(self):
        """Checks and initializes database if needed"""
        if not self._db_exists():
            await self._create_db()

    async def _checks(self, guild):
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
        servers = ServerConfigHandler("sqlite+aiosqlite:///servers/server_data_test.db")
        async with servers.engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        async with servers.Session() as session:
            results = await session.execute(
                sqlalchemy.select(models.ShitpostingChannel).
                where(models.ShitpostingChannel.server_id == 991869391350288424)
            )
            print([row.channel_id for row in results.scalars().all()])
        # await servers._check_db() #Works
        # await servers._check_server(pcm) #works
        # print(await servers.add_in_server_auto_ban_whitelist(pcm, bob))
        # print(await servers.add_text_trigger(pcm, "bepis", "pepsi"))
        # print(await servers.remove_text_trigger(pcm, trigger_phrase="beps", message="pepsi"))
        # print(await servers.get_text_triggers(pcm))
        # print(await servers.add_text_trigger(pcm, "bepiss", "ispep"))
        # print(await servers.add_text_trigger(pcm, "bepsi", "ispep"))
        # print(await servers.remove_text_trigger(pcm, message="ispep"))
        # print(await servers.get_text_triggers(pcm))
        # REAL USER ID in autoban whitelist
        real_user = User(1004537043805798411)
        # REAL PCM SERVER ID
        real_server = Guild(923301520819253268)
        # print(await servers.get_random_polder(real_server))
        # print(await servers.get_shitposting_channels(real_server))

        # print(await servers.get_server_auto_ban_whitelist(real_server))
        # print(await servers.find_in_server_auto_ban_whitelist(real_server, real_user))
        # print(await servers.get_server_parameters(real_server, "min_account_age"))
        # print(await servers.update_server_parameters(real_server, min_account_age=1))
        # print(await servers.get_server_parameters(real_server, "min_account_age")) #should be 1
        # print(await servers.get_server_auto_ban_whitelist(real_server))

        # print(await servers.get_text_triggers(real_server))
        # print(await servers.add_text_trigger(real_server, trigger_phrase="octo", message="i miss triplea"))
        # print(await servers.remove_text_trigger(real_server, trigger_phrase="octo", message="i miss triplea"))

        # # Testing polder
        # print(await servers.get_random_polder(pcm)) #should be None
        # await servers.add_in_polder(pcm, content="hello", message_id=0, author_id=bob.id)
        # await servers.add_in_polder(pcm, content="hello", message_id=1, author_id=bob.id)
        # await servers.add_in_polder(pcm, content="hello", message_id=2, author_id=bob.id)
        # await servers.add_in_polder(pcm, content="hello", message_id=3, author_id=alice.id)
        # await servers.add_in_polder(pcm, content="hello", message_id=4, author_id=alice.id)
        # await servers.add_in_polder(pcm, content="hello citizens", message_id=5, author_id=alice.id)
        # await servers.add_in_polder(pcm, content="hello citizens", message_id=6, author_id=alice.id)
        # await servers.add_in_polder(pcm, content="hello citizens", message_id=7, author_id=alice.id)
        # await servers.add_in_polder(pcm, content="hello citizens", message_id=8, author_id=bob.id)

        # print(await servers.get_random_polder(pcm))
        # print(await servers.get_random_polder(pcm))
        # print(await servers.get_random_polder(pcm))
        # print(await servers.get_random_polder(pcm))
        # print(await servers.get_random_polder(pcm))

        # print(await servers.remove_in_polder(pcm, content="hello", message_id=0)) #remove 1 entry
        # print(await servers.remove_in_polder(pcm, content="hello", author_id=alice.id)) #remove 2 entries
        # print(await servers.remove_in_polder(pcm, content="hello")) #remove 2 entries
        # print(await servers.remove_in_polder(pcm, author_id=alice.id)) #remove 3 entries
        # #should be one entry in polder remaining

        # print(await servers.add_in_shitposting_channels(pcm, 123)) #should be true
        # print(await servers.add_in_shitposting_channels(pcm, 456)) #should be true
        # print(await servers.add_in_shitposting_channels(pcm, 789)) #should be true
        # print(await servers.add_in_shitposting_channels(pcm, 789)) #should be false
        # print(await servers.get_shitposting_channels(pcm)) #should get list of channels
        # print(await servers.find_in_shitposting_channels(pcm, 123)) #should be true
        # print(await servers.remove_in_shitposting_channels(pcm, 123)) # should be true
        # print(await servers.remove_in_shitposting_channels(pcm, 123)) # should be false
        # print(await servers.find_in_shitposting_channels(pcm, 123)) #should be false

        # print(await servers.add_text_trigger(pcm, "pedo", "kill all pedos NOW")) #should be true
        # print(await servers.add_text_trigger(pcm, "pedo", "kill all pedos NOW")) #should be false
        # print(await servers.add_text_trigger(pcm, "pedo", "lol")) #should be true
        # print(await servers.add_text_trigger(pcm, "p", "kill all pedos NOW")) #should be true
        # print(await servers.get_text_triggers(pcm)) #should be dict
        # print(await servers.remove_text_trigger(pcm, trigger_phrase="pedo", message="kill all pedos NOW")) #should be true and remove one entry
        # print(await servers.get_text_triggers(pcm)) #check output
        # print(await servers.add_text_trigger(pcm, "pedo", "kill all pedos NOW")) #should be true
        # print(await servers.remove_text_trigger(pcm, trigger_phrase="pedo")) #should get rid of two entries
        # print(await servers.get_text_triggers(pcm))#one entry should remain





    
    asyncio.run(main())