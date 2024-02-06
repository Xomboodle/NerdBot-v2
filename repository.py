"""repository.py"""
import os
import logging
from typing import Any

import mysql.connector
from mysql.connector import MySQLConnection, Error
from mysql.connector.pooling import PooledMySQLConnection

from types import UnionType


Connection: UnionType = MySQLConnection | PooledMySQLConnection


logging.basicConfig(format='%(levelname)s @ %(asctime): %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)


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
