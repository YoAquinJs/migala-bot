"""El módulo db_utils contiene metodos que acceden y modifican datos en la base de datos de MongoDB"""

import discord
from enum import Enum
from bson.objectid import ObjectId

from database.mongo_client import get_mongo_client

_mongo_client = get_mongo_client()


class Collection(Enum):
    bugs = "bugs"
    polls = "polls"
    general = "general"
    selectors = "selectors"
    role_black_list = "role_black_list"


def insert(file: dict, guild: discord.Guild, collection: str):
    """Inserta un archivo a la base de datos

        Args:
                file (dict): Diccionario con los datos
                guild (discord.Guild): Información de una Guild de discord
                collection (str): Nombre de la coleccion a ingresar el archivo

        Returns:
                pymongo.results.InsertOneResult: Contiene la información de la inserción en MongoDB
    """

    database_name = get_database_name(guild)

    return _mongo_client[database_name][collection].insert_one(file)


def modify(key: str, value, modify_key: str, modify_value, guild: discord.Guild, collection: str):
    """Modifica un archivo con la llave y valor especificados en la base de datos

        Args:
                key (str): Llave a buscar
                value (indeterminado): Valor a buscar
                modify_key (dict): Llave del valor a modificar
                modify_value (indeterminado): Nuevo valor
                guild (discord.Guild): Información de una Guild de discord
                collection (str): Nombre de la coleccion a ingresar el archivo

        Returns:
                pymongo.results.UpdateOneResult: Contiene la información de la modificacion en MongoDB
    """

    database_name = get_database_name(guild)

    return _mongo_client[database_name][collection].update_one({key: value}, {"$set": {modify_key: modify_value}})


def replace(key: str, value, file: dict, guild: discord.Guild, collection: str):
    """Inserta un archivo a la base de datos

        Args:
                key (str): Llave a buscar
                value (indeterminado): Valor a buscar
                file (dict): Diccionario con los datos
                guild (discord.Guild): Información de una Guild de discord
                collection (str): Nombre de la coleccion a ingresar el archivo

        Returns:
                pymongo.results.InsertOneResult: Contiene la información de la inserción en MongoDB
    """

    database_name = get_database_name(guild)

    return _mongo_client[database_name][collection].find_one_and_replace({key: value}, file)


def delete(key: str, value, guild: discord.Guild, collection: str):
    """Elimina un archivo en la base de datos

        Args:
                key (str): Llave a comparar
                value (indeterminado): Valor a comparar
                guild (discord.Guild): Información de una Guild de discord
                collection (str): Nombre de la coleccion a ingresar el archivo

        Returns:
                pymongo.results.DeleteResult: Contiene la información de la eliminacion en MongoDB
    """

    database_name = get_database_name(guild)

    return _mongo_client[database_name][collection].delete_one({key: value})


def query(key: str, value, guild: discord.Guild, collection: str):
    """Obtiene un archivo de la base de datos

        Args:
                key (str): Llave a buscar
                value (indeterminado): Valor a buscar
                guild (discord.Guild): Información de una Guild de discord
                collection (str): Nombre de la coleccion en la cual se buscara el archivo

        Returns:
                dict: Archivo encontrado o None si no existe
    """

    database_name = get_database_name(guild)

    return _mongo_client[database_name][collection].find_one({key: value})


def query_id(file_id: str, guild: discord.Guild, collection: str):
    """Obtiene un archivo por su id en la base de datos

        Args:
                file_id (str): Id del archivo
                guild (discord.Guild): Información de una Guild de discord
                collection (str): Nombre de la coleccion en la cual se buscara el archivo

        Returns:
                dict: Archivo encontrado o None si no existe
    """

    database_name = get_database_name(guild)

    try:
        return _mongo_client[database_name][collection].find_one({"_id": ObjectId(file_id)})
    except:
        return None


def query_all(guild: discord.Guild, collection: str):
    """Obtiene todos los archivos en la coleccion especificada en la base de datos

        Args:
                guild (discord.Guild): Información de una Guild de discord
                collection (str): Nombre de la coleccion en la cual se buscara el archivo

        Returns:
                pymongo.cursor.Cursor: Clase iterable sobre Mongo query results de todos los archivos en la coleccion
    """

    database_name = get_database_name(guild)

    return _mongo_client[database_name][collection].find({})


def exists(key: str, value, guild: discord.Guild, collection: str):
    """Revisa la existencia de un archivo en la base de datos

        Args:
                key (str): Llave a buscar
                value (indeterminado): Valor a buscar
                guild (discord.Guild): Información de una Guild de discord
                collection (str): Nombre de la coleccion en la cual se buscara el archivo

        Returns:
                bool: Existencia del archivo
    """

    database_name = get_database_name(guild)

    for file in _mongo_client[database_name][collection].find({}):
        if file[key] == value:
            return True

    return False


def query_rnd(guild: discord.Guild, collection: str):
    """Obtiene un archivo aleatorio en la base de datos

        Args:
                guild (discord.Guild): Información de una Guild de discord
                collection (str): Nombre de la coleccion en la cual se buscara el archivo

        Returns:
                dict: Archivo encontrado o None si no hay ningun archivo en la coleccion
    """

    database_name = get_database_name(guild)

    cursor = _mongo_client[database_name][collection].aggregate([
        {"$match": {"start_time": {"$exists": False}}},
        {"$sample": {"size": 1}}
    ])

    rnd = None
    for i in cursor:
        rnd = i

    return rnd


def get_database_name(guild: discord.Guild) -> str:
    """Genera el nombre de la base de datos de una guild de discord

        Args:
                guild (discord.Guild): Información de una Guild de discord

        Returns:
                str: Nombre único de la base de datos para el servidor de discord
    """

    name = guild.name
    if len(name) > 20:
        # limitacion del nombre del nombre a menos de 64 caracteres
        name = name.replace("a", "")
        name = name.replace("e", "")
        name = name.replace("i", "")
        name = name.replace("o", "")
        name = name.replace("u", "")

        if len(name) > 20:
            name = name[:20]

    return f'{name.replace(" ", "_")}_{guild.id}'
