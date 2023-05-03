import configparser

def read(config_file, section, name = None):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(config_file)

    if section not in config or (name != None and name not in config[section]):
        return ""

    if name == None:
        return list(config[section])

    return config[section][name]