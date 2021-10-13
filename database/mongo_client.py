"""El módulo mongo_client se encarga de la creacion del cliente de mongo y la conexion con la base de datos de Mongo"""

import pymongo

from bot.bot_utils import get_global_settings

mongo_client = None
global_settings = get_global_settings()


def init_database(user: str, password: str):
    """Inicializa el Cliente de la base de datos

        Args:
                user (str): Usuario del Cluster de MongoDB
                password (str): Contraseña del usuario del Cluster de MongoDB
    """

    global mongo_client

    # URL de la base de datos en Mongo Atlas
    url_db = f"mongodb+srv://{user}:{password}" \
             f"@migalabotcluster.ksrmy.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    mongo_client = pymongo.MongoClient(url_db)
    print("data base initialized")


def get_mongo_client() -> pymongo.MongoClient:
    """Esta función retorna un singleton de pymongo.MongoClient

        Returns:
                pymongo.MongoClient: Cliente para conectarse a una base de datos de MongoDB
    """

    if mongo_client is None:
        init_database(global_settings["mongoUser"], global_settings["mongoPassword"])

    return mongo_client


def close_client():
    """Desconecta el cliente de MongoDB
    """

    get_mongo_client().close()
    print('Mongo Client Closed')
