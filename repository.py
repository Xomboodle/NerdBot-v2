"""repository.py"""
import os
import logging
from typing import Any

import mysql.connector
from mysql.connector import MySQLConnection, Error
from mysql.connector.pooling import PooledMySQLConnection

from types import UnionType

Connection: UnionType = MySQLConnection | PooledMySQLConnection
PartialConnection: UnionType = Connection | None

logging.basicConfig(format='%(levelname)s @ %(asctime)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)


def create_connection() -> PartialConnection:
    connection: Connection = mysql.connector.connect(
        host=os.environ.get('HOST'),
        user=os.environ.get('DBUSER'),
        password=os.environ.get('DBPASS'),
        database=os.environ.get('DATABASE')
    )
    if connection and connection.is_connected():
        return connection
    else:
        logging.warning("Failed to connect to database")
        return None


def add_guild(guild_id: int) -> bool:
    logging.info("Entered function add_guild")
    cnx: PartialConnection = create_connection()
    if cnx is None:
        return False

    params = {
        'guildId': guild_id
    }

    q_select_guild_exists = ("SELECT 1 "
                             "FROM GUILDS "
                             f"WHERE GuildID = %(guildId)s")

    q_insert_new_guild = ("INSERT "
                          "INTO GUILDS (GuildID, Active) "
                          "VALUES (%(guildId)s, 1)")

    q_update_guild_active = ("UPDATE GUILDS "
                             "SET Active = 1 "
                             "WHERE GuildID = %(guildId)s")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_select_guild_exists, params)

            check_guild_exists: Any = cursor.fetchone()
            if check_guild_exists == 1:
                cursor.execute(q_update_guild_active, params)
                cnx.commit()
            else:
                cursor.execute(q_insert_new_guild, params)
                cnx.commit()
        except Error as error:
            logging.error(error)
        finally:
            cursor.close()
            cnx.close()

    logging.info("Exiting function add_guild")
    return True


def get_guild_changelog_version(guild_id: int) -> int | None:
    logging.info("Entered function set_guild_changelog_version")
    cnx: PartialConnection = create_connection()
    if cnx is None:
        return None

    params = {
        'guildId': guild_id
    }

    q_get_guild_changelog_version = ("SELECT Changelog "
                                     "FROM GUILDS "
                                     "WHERE GuildID = %(guildId)s")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_get_guild_changelog_version, params)
            version: Any = cursor.fetchone()
        except Error as error:
            logging.error(error)
        finally:
            cursor.close()
            cnx.close()

    logging.info("Exiting function set_guild_changelog_version")
    return version


def set_guild_changelog_version(guild_id: int, version: int) -> bool:
    logging.info("Entered function set_guild_changelog_version")
    cnx: PartialConnection = create_connection()
    if cnx is None:
        return False

    params = {
        'version': version,
        'guildId': guild_id
    }

    q_set_guild_changelog_version = ("UPDATE GUILDS "
                                     "SET Changelog = %(version)s "
                                     "WHERE GuildID = %(guildId)s")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_set_guild_changelog_version, params)
            cnx.commit()
        except Error as error:
            logging.error(error)
        finally:
            cursor.close()
            cnx.close()

    logging.info("Exiting function set_guild_changelog_version")
    return True
