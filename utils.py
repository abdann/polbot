def strtobool(string:str):
    """Parses a simple string as 'True' or 'False' """
    if string.casefold() == 'true':
         return True
    elif string.casefold() == 'false':
         return False
    else:
         raise ValueError

value_types = {
    "int":int,
    "str":str,
    "bool":strtobool
}

def convert_type(text_value:str, value_type:str):
    """Converts text_value to the usual Python object using value_type"""
    if value_type in value_types.keys():
        return value_types.get(value_type)(text_value)
    else:
        raise ValueError

def string_type(value):
    """Converts the object to a string respresentation"""
    return str(value).casefold()
