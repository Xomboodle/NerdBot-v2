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
    """
    Establishes connection to database. Must be called at the start of every other function in this file.
    Requires valid environment variables or the connection will fail.
    :return: A connection object.
    """
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


def get_all_guild_ids() -> list[int] | Error:
    """
    Retrieves all current guild IDs.
    :return: A list of guild IDs.
    """
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    q_select_all_guild_ids = ("SELECT GuildId "
                              "FROM GUILDS")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_select_all_guild_ids)

            response: Any = cursor.fetchall()
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def set_active_guild(guild_id: int) -> Error:
    """
    Sets a guild to active.
    :param guild_id: The ID of the guild.
    """
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        'guildId': guild_id
    }

    q_update_guild_active = ("UPDATE GUILDS "
                             "SET Active = 1 "
                             "WHERE GuildId = %(guildId)s")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_update_guild_active, params)
            cnx.commit()
            response = Error(ErrorType.NoError)
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def set_inactive_guild(guild_id: int) -> Error:
    """
    Sets a guild to inactive.
    :param guild_id: The ID of the guild.
    """
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        'guildId': guild_id
    }

    q_update_guild_active = ("UPDATE GUILDS "
                             "SET Active = 0 "
                             "WHERE GuildId = %(guildId)s")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_update_guild_active, params)
            cnx.commit()
            response = Error(ErrorType.NoError)
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def add_guild(guild_id: int) -> Error:
    """
    Add a new guild to the database.
    :param guild_id: The ID of the guild to add
    """
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        'guildId': guild_id
    }

    q_insert_new_guild = ("INSERT "
                          "INTO GUILDS (GuildId, Active) "
                          "VALUES (%(guildId)s, 1)")

    q_add_guild_id_to_coins = ("INSERT "
                               "INTO GUILD_COINS (GuildID, LastCaught, Total) "
                               "SELECT %(guildId)s AS GuildId, CURRENT_DATE() AS LastCaught, 0 AS Total "
                               "FROM GUILD_COINS "
                               "WHERE (GuildId=%(guildId)s "
                               "HAVING COUNT(*)=0")
    q_add_guild_id_to_clams = ("INSERT "
                               "INTO GUILD_CLAMS (GuildID, LastCaught, Total) "
                               "SELECT %(guildId)s AS GuildId, CURRENT_DATE() AS LastCaught, 0 AS Total "
                               "FROM GUILD_CLAMS "
                               "WHERE (GuildId=%(guildId)s "
                               "HAVING COUNT(*)=0")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_insert_new_guild, params)
            cnx.commit()
            cursor.execute(q_add_guild_id_to_coins, params)
            cnx.commit()
            cursor.execute(q_add_guild_id_to_clams, params)
            cnx.commit()
            response = Error(ErrorType.NoError)
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def get_guild_changelog_version(guild_id: int) -> int | Error:
    """
    Gets the latest changelog version released to a guild.
    :param guild_id: The guild ID.
    :return: The changelog index.
    """
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
    """
    Sets the changelog version for a guild.
    :param guild_id: The guild ID.
    :param version: The changelog index.
    """
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


def get_last_caught(guild_id: int, claimable: Claimable) -> datetime | Error:
    """
    Retrieves the time at which a crate/clam was last caught.
    :param guild_id: The guild ID.
    :param claimable: The type of claimable.
    :return: The datetime of the last caught item.
    """
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
    """
    Sets the time at which a crate/clam was last caught.
    :param guild_id: The guild ID.
    :param claimable: The type of claimable.
    :param time: The time at which the item was caught.
    """
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
