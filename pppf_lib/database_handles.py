"""
Create and maintain the connections to the SQLite database
"""


import os
import sys
import argparse
import sqlite3
import gzip


def connect_to_db(dbname, verbose=False):
    """
    Connect to the database
    :param dbname: the database file name
    :param verbose: print addtional output
    :return: the database connection
    """

    try:
        conn = sqlite3.connect(dbname)
    except sqlite3.Error as e:
        print(e)
        sys.exit(-1)

    if verbose:
        sys.stderr.write("Connected to database: {}\n".format(sqlite3.version))

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
        sys.stderr.write("There was no database connection!\n")




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Index a fastq file")
    parser.add_argument('-f', help='fastq file to index', required=True)
    parser.add_argument('-c', help='index file to create', required=True)
    parser.add_argument('-w', help='overwrite the file if it exists', action="store_true")
    parser.add_argument('-v', help='verbose output', action="store_true")
    args = parser.parse_args()

    create_index(args.f, args.c, args.w, args.v)