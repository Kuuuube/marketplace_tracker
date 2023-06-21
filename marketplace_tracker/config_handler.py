import configparser

def read(config_file, section, name = None, delimiters = ['=', ':']):
    config = configparser.ConfigParser(allow_no_value=True, delimiters=delimiters)
    config.optionxform = str #makes it case sensitive
    config.read(config_file, encoding="utf-8")

    if section not in config and name == None:
        return []
    elif section not in config or (name != None and name not in config[section]):
        return ""

    if name == None:
        return list(config[section])

    return config[section][name]