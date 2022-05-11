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

params = {
    "shitposting_channels":[
        3245154145,
        2341235123,
        2341234123,
        9812358164
    ]
}
print(params)
params.get("shitposting_channels").append(9829546364)
print(params)