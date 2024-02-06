"""repository.py"""
import os
import logging
from typing import Any

import mysql.connector
from mysql.connector import MySQLConnection, Error
from mysql.connector.pooling import PooledMySQLConnection

from types import UnionType

Connection: UnionType = MySQLConnection | PooledMySQLConnection

logging.basicConfig(format='%(levelname)s @ %(asctime)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)


def create_connection() -> Connection | None:
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
    cnx: Connection | None = create_connection()
    if cnx is None:
        return False

    q_select_guild_exists = ("SELECT 1 "
                             "FROM GUILDS "
                             f"WHERE GuildID = %s")

    q_insert_new_guild = ("INSERT "
                          "INTO GUILDS (GuildID, Active) "
                          "VALUES (%s, 1)")

    q_update_guild_active = ("UPDATE GUILDS "
                             "SET Active = 1 "
                             "WHERE GuildID = %s")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_select_guild_exists, (guild_id,))

            check_guild_exists: Any = cursor.fetchone()
            if check_guild_exists == 1:
                cursor.execute(q_update_guild_active, (guild_id,))
                cnx.commit()
            else:
                cursor.execute(q_insert_new_guild, (guild_id,))
                cnx.commit()
        except Error as error:
            logging.error(error)
        finally:
            cursor.close()
            cnx.close()

    logging.info("Exiting function add_guild")
    return True
