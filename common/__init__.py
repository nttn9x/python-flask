from .config import read_config
from .database import create_connect


def init_config():
    read_config()

    create_connect()
