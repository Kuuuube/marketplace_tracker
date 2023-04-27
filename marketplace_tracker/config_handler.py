from configparser import ConfigParser

def config_info(config_file):
    config = ConfigParser()
    config.read(config_file)
    return config

def read(config_file,section,name):
    config = config_info(config_file)
    return config.get(section,name)