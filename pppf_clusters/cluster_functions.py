"""
Extract the functions associated with a cluster
"""

import os
import sys
import argparse
import json
from pppf_accessories import color
from pppf_databases import connect_to_db, disconnect

protein_functions = {}

def get_functions(proteinid, clusterdb_cursor, verbose=False):
    """
    Helper function that just returns a tple of [function, {json format all functions}]
    :param proteinid: the protein id to search
    :param clusterdb_cursor: the database cursor
    :param verbose: more output
    :return: tple of [function, all functions]
    """

    sql = "select function, functions from cluster left join md5cluster on md5cluster.cluster = cluster.cluster_rowid where md5cluster.protein_md5sum = ?;"
    ex = clusterdb_cursor.execute(sql, [proteinid])
    return ex.fetchone()

def proteinid_to_function(proteinid, clusterdb_cursor, verbose=False):
    """
    Convert a protein ID to a single function
    :param proteinid: The protein md5 sum
    :param clusterdb_cursor: the cursor to the cluster database
    :param verbose: more output
    :return: str: the function of the protein or None if it is not in a cluster
    """

    global protein_functions

    if proteinid not in protein_functions:
        protein_functions[proteinid] = get_functions(proteinid, clusterdb_cursor, verbose)

    return protein_functions[proteinid][0]


def proteinid_to_all_functions(proteinid, clusterdb_cursor, verbose=False):
    """
    Convert a protein ID to a dict object of all function
    :param proteinid: The protein md5 sum
    :param clusterdb_cursor: the cursor to the cluster database
    :param verbose: more output
    :return: dict: the functions of the protein and their frequency
    """

    global protein_functions

    if proteinid not in protein_functions:
        protein_functions[proteinid] = get_functions(proteinid, clusterdb_cursor, verbose)

    return json.loads(protein_functions[proteinid][1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=" ")
    parser.add_argument('-i', help='protein id', required=True)
    parser.add_argument('-c', help='cluster database', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    c= connect_to_db(args.c, args.v)
    fn = proteinid_to_function(args.i, c.cursor(), args.v)
    fns = proteinid_to_all_functions(args.i, c.cursor(), args.v)
    fnstr = "\n".join([f"{x} -> {str(y)}" for x,y in sorted(fns.items(), key=lambda item: item[1], reverse=True)])
    disconnect(c, args.v)

    print(f"The function of {args.i} is\n'{fn}'")
    print(f'All the functions are:\n{fnstr}')
