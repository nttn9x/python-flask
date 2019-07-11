import configparser

config = configparser.ConfigParser()


def read_config():
    global config

    config.read('config.ini')
