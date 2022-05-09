from http import server
import pathlib
import json

default_parameters = {
    "min_account_age": 14,
    "new_auto_ban_enabled": True,
    "lockdown_enabled": False
}
server_folder = pathlib.Path("servers") / str(12914132)
server_folder.mkdir()
with open((server_folder / "parameters.json").resolve(), 'x') as f:
    json.dump(default_parameters, f)
with open((server_folder / "auto_ban_whitelist.json").resolve(), 'x') as f:
    json.dump(dict(), f)
with open((server_folder / "reaction_triggers.json").resolve(), 'x') as f:
    json.dump(dict(), f)


"""Retrieves the current server parameter list"""
with open((server_folder / "parameters.json").resolve(), 'r') as f:
    parameters = json.load(f)
print(parameters)