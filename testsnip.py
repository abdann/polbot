def string_search(defined_triggers: dict, message):
    reactions = []
    # First combine message into single string with no spaces
    content = message.content.replace(" ", "")
    # now append any positive hits
    for trigger, reaction in defined_triggers.items():
        if content.find(trigger) != -1:
            reactions.append(reaction)
    return reactions

class Message:
    def __init__(self) -> None:
        pass

message = Message()
message.content = "hello mods are gay among us"

defined_triggers = {
    "mods" : ":rainbow_flag:",
    "amongus" : ":sus:"
}

print(string_search(defined_triggers, message))