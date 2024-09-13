"""repository.py"""
from datetime import datetime
import os
from typing import Any

import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.cursor import MySQLCursor

from enums import Claimable, ErrorType, WarningType, ModerationType
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


def get_current_exists(guild_id: int, claimable: Claimable) -> bool | Error:
    """
    Returns whether a particular claimable is currently unclaimed.
    :param guild_id: The ID of the guild.
    :param claimable: The type of claimable.
    :return:
    """
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        "guildId": guild_id
    }

    q_current_coin = ("SELECT Current "
                      "FROM GUILD_COINS "
                      "WHERE GuildId = %(guildId)s")

    q_current_clam = ("SELECT Current "
                      "FROM GUILD_CLAMS "
                      "WHERE GuildId = %(guildId)s")

    with cnx.cursor() as cursor:
        try:
            if claimable == Claimable.Coin:
                cursor.execute(q_current_coin, params)
            elif claimable == Claimable.Clam:
                cursor.execute(q_current_clam, params)
            response = cursor.fetchone()
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def update_current_exists(guild_id: int, claimable: Claimable, value: int) -> Error:
    """
    Returns whether a particular claimable is currently unclaimed.
    :param guild_id: The ID of the guild.
    :param claimable: The type of claimable.
    :param value: The value to set Current to.
    :return:
    """
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        "guildId": guild_id,
        "current": value
    }

    q_current_coin = ("UPDATE GUILD_COINS "
                      "SET Current = %(current)s"
                      "WHERE GuildId = %(guildId)s")

    q_current_clam = ("UPDATE GUILD_CLAMS "
                      "SET Current = %(current)s"
                      "WHERE GuildId = %(guildId)s")

    with cnx.cursor() as cursor:
        try:
            if claimable == Claimable.Coin:
                cursor.execute(q_current_coin, params)
            elif claimable == Claimable.Clam:
                cursor.execute(q_current_clam, params)
            cnx.commit()
            response = Error(ErrorType.NoError)
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


# Internal use only
def insert_user(user_id: int, cnx: PartialConnection, cursor: MySQLCursor) -> Error:
    params = {
        "userId": user_id
    }

    q_insert_user = ("INSERT "
                     "INTO USERS (UserId)"
                     "VALUES (%(userId)s)")

    try:
        cursor.execute(q_insert_user, params)
        cnx.commit()
        response = Error(ErrorType.NoError)
    except mysql.connector.Error as error:
        response = Error(ErrorType.MySqlException, error.msg)

    return response


def get_user_score(user_id: int, claimable: Claimable) -> int | Error:
    """
    Gets the individual user's score for a particular claimable.
    :param user_id: The ID of the user.
    :param claimable: The type of claimable.
    :return: The score for the user.
    """
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        "userId": user_id
    }

    q_select_user = ("SELECT 1 "
                     "FROM USERS "
                     "WHERE UserId = %(userId)s")

    q_get_user_coin_score = ("SELECT CoinsCaught "
                             "FROM USERS "
                             "WHERE UserId = %(userId)s")

    q_get_user_clam_score = ("SELECT ClamsCaught "
                             "FROM USERS "
                             "WHERE UserId = %(userId)s")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_select_user, params)
            user_exists = cursor.fetchone()
            if user_exists != 1:
                new_user_response = insert_user(user_id, cnx, cursor)
                response = 0 if new_user_response.Status == ErrorType.NoError else new_user_response
            else:
                if claimable == Claimable.Clam:
                    cursor.execute(q_get_user_clam_score, params)
                elif claimable == Claimable.Coin:
                    cursor.execute(q_get_user_coin_score, params)

                response = cursor.fetchone()
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def set_user_score(user_id: int, score: int, claimable: Claimable) -> Error:
    """
    Sets the user's score for a particular claimable.
    :param user_id: The user's ID.
    :param score: The score to set.
    :param claimable: The type of claimable.
    """
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        "userId": user_id,
        "score": score
    }

    q_update_coin_score = ("UPDATE USERS "
                           "SET CoinsCaught = %(score)s "
                           "WHERE UserId = %(userId)s")

    q_update_clam_score = ("UPDATE USERS "
                           "SET ClamsCaught = %(score)s "
                           "WHERE UserId = %(userId)s")

    with cnx.cursor() as cursor:
        try:
            if claimable == Claimable.Clam:
                cursor.execute(q_update_clam_score, params)
            elif claimable == Claimable.Coin:
                cursor.execute(q_update_coin_score, params)
            cnx.commit()
            response = Error(ErrorType.NoError)
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def get_top_group_scores(user_ids: list[int], claimable: Claimable) -> list[tuple[int, int]] | Error:
    """
    Gets top 10 scores for a particular claimable for a subset of users.
    :param user_ids: A list of user IDs.
    :param claimable: The type of claimable.
    :return: A list of scores attached to user IDs.
    """
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        "userIds": user_ids
    }

    q_get_group_coin_score = ("SELECT TOP (10) UserId, CoinsCaught "
                              "FROM USERS "
                              "WHERE UserId IN %(userIds)s "
                              "ORDER BY CoinsCaught DESC")

    q_get_group_clam_score = ("SELECT TOP (10) UserId, ClamsCaught "
                              "FROM USERS "
                              "WHERE UserId IN %(userIds)s "
                              "ORDER BY ClamsCaught DESC")

    with cnx.cursor() as cursor:
        try:
            if claimable == Claimable.Coin:
                cursor.execute(q_get_group_coin_score, params)
            elif claimable == Claimable.Clam:
                cursor.execute(q_get_group_clam_score, params)
            response = cursor.fetchall()
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def get_user_moderation_info(user_id: int, guild_id: int, moderation_type: ModerationType) -> list[int] | None | Error:
    """
    Retrieves data from the MODERATION table about a user's particular restriction within a guild
    :param user_id: The ID of the user.
    :param guild_id: The ID of the guild.
    :param moderation_type: The type of restriction.
    :return: An object with the restriction's data, or None if it doesn't exist.
    """
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        "userId": user_id,
        "guildId": guild_id,
        "moderationType": moderation_type
    }

    q_get_user_moderation_info = ("SELECT AdditionalData "
                                  "FROM MODERATION "
                                  "WHERE UserId = %(userId)s "
                                  "AND GuildId = %(userId)s "
                                  "AND ModerationType = %(moderationType)s")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_get_user_moderation_info, params)
            response = [int(x) for x in str(cursor.fetchone()).split(",")]
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def set_user_moderation_info(
        user_id: int,
        guild_id: int,
        moderation_type: ModerationType,
        additional_data: str) -> Error:
    """
    Adds moderation data to the MODERATION table for a user in a guild for a particular restriction.
    :param user_id: The ID of the user.
    :param guild_id: The ID of the guild.
    :param moderation_type: The type of restriction.
    :param additional_data: Any additional data needed.
    """
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        "userId": user_id,
        "guildId": guild_id,
        "moderationType": moderation_type,
        "additionalData": additional_data
    }

    q_set_user_moderation_info = ("INSERT INTO "
                                  "MODERATION (UserId, GuildId, ModerationType, AdditionalData) "
                                  "VALUES (%(userId)s, %(guildId)s, %(moderationType)s, %(additionalData)s")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_set_user_moderation_info, params)
            cnx.commit()
            response = Error(ErrorType.NoError)
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response


def remove_user_moderation_info(user_id: int, guild_id: int, moderation_type: ModerationType) -> Error:
    """
    Removes a particular restriction for a user in a guild.
    :param user_id: The ID of the user.
    :param guild_id: The ID of the guild.
    :param moderation_type: The type of restriction.
    """
    cnx: PartialConnection = create_connection()
    if isinstance(cnx, Error):
        return cnx

    params = {
        "userId": user_id,
        "guildId": guild_id,
        "moderationType": moderation_type
    }

    q_remove_user_moderation_info = ("DELETE FROM MODERATION "
                                     "WHERE UserId = %(userId)s "
                                     "AND GuildId = %(guildId)s "
                                     "AND ModerationType = %(moderationType)s")

    with cnx.cursor() as cursor:
        try:
            cursor.execute(q_remove_user_moderation_info, params)
            cnx.commit()
            response = Error(ErrorType.NoError)
        except mysql.connector.Error as error:
            response = Error(ErrorType.MySqlException, error.msg)
        finally:
            cursor.close()
            cnx.close()

    return response
