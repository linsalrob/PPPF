"""
Create and maintain the connections to the SQLite database
"""

import sys
import os
import sqlite3
from pppf_accessories import color


def connect_to_db(dbname, verbose=False):
    """
    Connect to the database
    :param dbname: the database file name
    :param verbose: print addtional output
    :return: the database connection
    """
    if not os.path.exists(dbname):
        sys.stderr.write(f"{color.RED}FATAL: {dbname} does not exist. Cannot connect{color.ENDC}\n")
        sys.exit(-1)

    try:
        conn = sqlite3.connect(dbname)
    except sqlite3.Error as e:
        print(e)
        sys.exit(-1)

    if verbose:
        sys.stderr.write(f"{color.GREEN}Connected to database: {sqlite3.version}{color.ENDC}\n")

    conn.execute("PRAGMA foreign_keys = ON;")

    return conn

def disconnect(conn, verbose=False):
    """
    Disconnect the database and ensure we've saved all changes
    :param conn: the database connection
    :param verbose: print addtional output
    :return:
    """

    if conn:
        conn.commit()
        conn.close()
    elif verbose:
        sys.stderr.write(f"{color.RED}There was no database connection!{color.ENDC}\n")



