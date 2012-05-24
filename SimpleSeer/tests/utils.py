import mongoengine
from ming import mim

def register_mim_connection():
    mongoengine.connection._connections[mongoengine.connection.DEFAULT_CONNECTION_NAME] = mim.Connection()
    mongoengine.connection._connection_settings[mongoengine.connection.DEFAULT_CONNECTION_NAME] = dict(
        name=None,
        username=None,
        password=None)
