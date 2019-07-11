from pymongo import MongoClient

from .config import config

COLLECTION_DOCUMENT = "document"

mydb = None


def get_database(client):
    database_name = config['database']['name']

    return client[database_name]


def get_table_document():
    return mydb[COLLECTION_DOCUMENT]


def create_connect():
    client = MongoClient(config['database']['url'])

    global mydb
    mydb = get_database(client)
