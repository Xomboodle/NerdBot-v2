"""repository.py"""
from datetime import datetime
import os
from typing import Any

import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.pooling import PooledMySQLConnection

from enums import Claimable, ErrorType, WarningType
from classes import Error

from types import UnionType

Connection: UnionType = MySQLConnection | PooledMySQLConnection
PartialConnection: UnionType = Connection | Error


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
        return Error(WarningType.BadConnection, "Failed to connect to database.")


def add_guild(guild_id: int) -> Error:
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        'guildId': guild_id
    }

    q_select_guild_exists = ("SELECT 1 "
                             "FROM GUILDS "
                             "WHERE GuildID = %(guildId)s")

    q_insert_new_guild = ("INSERT "
                          "INTO GUILDS (GuildID, Active) "
                          "VALUES (%(guildId)s, 1)")

    q_update_guild_active = ("UPDATE GUILDS "
                             "SET Active = 1 "
                             "WHERE GuildID = %(guildId)s")

    q_add_guild_id_to_coins = ("INSERT "
                               "INTO GUILD_COINS (GuildID) "
                               "VALUES (%(guildId)s)")
    q_add_guild_id_to_clams = ("INSERT "
                               "INTO GUILD_CLAMS (GuildID) "
                               "VALUES (%(guildId)s)")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_select_guild_exists, params)

            check_guild_exists: Any = cursor.fetchone()
            if check_guild_exists == 1:
                cursor.execute(q_update_guild_active, params)
                cnx.commit()
                cursor.execute(q_add_guild_id_to_coins, params)
                cnx.commit()
                cursor.execute(q_add_guild_id_to_clams, params)
                cnx.commit()
            else:
                cursor.execute(q_insert_new_guild, params)
                cnx.commit()
            response = Error(ErrorType.NoError)
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def get_guild_changelog_version(guild_id: int) -> int | Error:
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        'guildId': guild_id
    }

    q_get_guild_changelog_version = ("SELECT Changelog "
                                     "FROM GUILDS "
                                     "WHERE GuildID = %(guildId)s")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_get_guild_changelog_version, params)
            response: Any = cursor.fetchone()
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def set_guild_changelog_version(guild_id: int, version: int) -> Error:
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

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
            response = Error(ErrorType.NoError)
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def get_last_caught(guild_id: int, claimable: Claimable) -> datetime | None | Error:
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        'guildId': guild_id
    }

    if claimable == Claimable.Coin:
        q_get_last_caught = ("SELECT LastCaught "
                             "FROM GUILD_COINS "
                             "WHERE GuildID = %(guildId)s")
    elif claimable == Claimable.Clam:
        q_get_last_caught = ("SELECT LastCaught "
                             "FROM GUILD_CLAM "
                             "WHERE GuildID = %(guildId)s")
    else:
        return Error(ErrorType.InvalidArgument, "Invalid argument for claimable.")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_get_last_caught, params)
            response: Any = cursor.fetchone()
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def set_last_caught(guild_id: int, claimable: Claimable, time: datetime) -> Error:
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        'guildId': guild_id,
        'time': time
    }

    if claimable == Claimable.Coin:
        q_set_last_caught = ("UPDATE GUILD_COINS "
                             "SET LastCaught = %(time)s "
                             "WHERE GuildID = %(guildId)s")
    elif claimable == Claimable.Clam:
        q_set_last_caught = ("UPDATE GUILD_CLAM "
                             "SET LastCaught = %(time)s "
                             "WHERE GuildID = %(guildId)s")
    else:
        return Error(ErrorType.InvalidArgument, "Invalid argument for claimable.")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_set_last_caught, params)
            cnx.commit()
            response = Error(ErrorType.NoError)
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response
