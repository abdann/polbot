def strtobool(string:str):
    """Parses a simple string as 'True' or 'False' """
    if string.casefold() == 'True'.casefold():
         return True
    elif string.casefold() == 'False'.casefold():
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