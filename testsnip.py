# from http import server
# import pathlib
# import json

# default_parameters = {
#     "min_account_age": 14,
#     "new_auto_ban_enabled": True,
#     "lockdown_enabled": False
# }
# server_folder = pathlib.Path("servers") / str(12914132)
# server_folder.mkdir()
# with open((server_folder / "parameters.json").resolve(), 'x') as f:
#     json.dump(default_parameters, f)
# with open((server_folder / "auto_ban_whitelist.json").resolve(), 'x') as f:
#     json.dump(dict(), f)
# with open((server_folder / "reaction_triggers.json").resolve(), 'x') as f:
#     json.dump(dict(), f)


# """Retrieves the current server parameter list"""
# with open((server_folder / "parameters.json").resolve(), 'r') as f:
#     parameters = json.load(f)
# print(parameters)


# """TESTING SERVER HANDLER ASYNCIO"""
# import asyncio
# import aiosqlite
# import pathlib
# import cogs.serverhandler

# #Server ID to test (already exists)
# server_id = 914603756136591380
# servers = pathlib.Path("servers")
# server_folder = servers / str(server_id)

# # Dummy classes to mimic live build
# class Guild:
#     def __init__(self, id) -> None:
#         self.id = id

# class User:
#     def __init__(self, name, id) -> None:
#         self.name = name
#         self.id = id

# #Instantiation
# guild = Guild(server_id)
# user = User("Bob#1263", 2381451425145)
# servers = cogs.serverhandler.ServerConfigHandler()

# async def print_json_files():
#     params = await servers.get_server_parameters(guild)
#     print("Initial params:")
#     print(params)
#     params.update({'min_account_age': 21, 'new_auto_ban_enabled': True, 'lockdown_enabled': False, 'polder_channel_id': 973983835698102373, 'shitposting_channels': [916708932460879952], 'polder_enabled': True, 'random_polder_posts_enabled': True, 'random_text_posts_enabled': False, 'shitpost_probability': 20.0})
#     await servers.update_server_parameters(guild, params)
#     print("Final params:")
#     print(await servers.get_server_parameters(guild))
#     # Above works fine
#     whitelist = await servers.get_server_auto_ban_whitelist(guild)
#     print("Initial Whitelist:")
#     print(whitelist)
#     print(await servers.add_in_server_auto_ban_whitelist(guild, user))
#     print("Final Whitelist")
#     print(await servers.get_server_auto_ban_whitelist(guild))
#     print("now remove him")
#     print(await servers.remove_in_server_auto_ban_whitelist(guild, user))
#     print(await servers.get_server_auto_ban_whitelist(guild))
#     print("Initial reaction Triggers")
#     rt = await servers.get_server_reaction_triggers(guild)
#     print(rt)
#     rt.update({"black":"black"})
#     await servers.update_server_reaction_triggers(guild, rt)
#     print("Final reaction triggers")
#     print(await servers.get_server_reaction_triggers(guild))
#     async with aiosqlite.connect((server_folder / "polder.db").resolve()) as db:
#         await db.execute("""CREATE TABLE IF NOT EXISTS polder (
#             message_id INTEGER PRIMARY KEY,
#             hash TEXT,
#             author_id INTEGER
#             )""")

# asyncio.run(print_json_files())

# """WORKS AS EXPECTED"""

# import hashlib

# string1 = "9"
# hash1 = hashlib.md5(string1.encode()).hexdigest()
# string2 = "8"
# hash2 = hashlib.md5(string2.encode()).hexdigest()
# print(hash1 == hash2)
# import hashlib
# def hasher(content):
#     return hashlib.md5(content.encode()).hexdigest()

# print(hasher("https://tenor.com/view/no-maidens-varre-elden-ring-varre-maidenless-elden-ring-maidens-gif-25161039"))

from os import walk
from pathlib import Path

import markovify
test = """Fascism is therefore opposed to all individualistic abstractions based on eighteenth century materialism; and it is opposed to all Jacobinistic utopias and innovations. It does not believe in the possibility of "happiness" on earth as conceived by the economistic literature of the XVIIIth century, and it therefore rejects the theological notion that at some future time the human family will secure a final settlement of all its difficulties. This notion runs counter to experience which teaches that life is in continual flux and in process of evolution. """
print("\n".join(markovify.split_into_sentences(test)))

for currentdirname, dirnames, filenames in walk(Path("corpi")):
    for filename in filenames:
        with open((Path("corpi") / filename).resolve(), "r") as f:
            text_newlined = "\n".join(markovify.split_into_sentences(f.read()))
        with open((Path("corpi") / filename).resolve(), "w") as f:
            f.write(text_newlined)