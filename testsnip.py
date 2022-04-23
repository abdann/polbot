def string_search(defined_triggers: dict, message):
    reactions = []
    # First combine message into single string with no spaces and lowercase
    content = message.content.replace(" ", "").casefold()
    # now append any positive hits (THIS IS BLOCKING CODE)
    for trigger, reaction in defined_triggers.items():
        if content.find(trigger) != -1:
            reactions.append(reaction)
    return reactions

# Testing string_search, made a dummy class
class Message:
    def __init__(self) -> None:
        pass

message = Message()
message.content = "hello MODSamonGus are gay among us"

import json

with open("reactiontriggers.json") as f:
    reaction_triggers = json.load(f)

def add_reaction_trigger(trigger_phrase, reactionID):
    