"""

"""

import os
import sys
import argparse

from roblib import bcolors
from pppf_databases import connect_to_db, disconnect
from pppf_clusters import read_mmseqs_clusters, add_functions_to_clusters, insert_cluster_metadata, insert_into_database

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load the cluster information into the databases')
    parser.add_argument('-d', help='SQL database', required=True)
    parser.add_argument('-t', help='Cluster tsv file', required=True)
    parser.add_argument('-n', help='Cluster name (short text)', required=True)
    parser.add_argument('-d', help='Cluster description (human readable text)', required=True)
    parser.add_argument('-c', help='Cluster command line (bash)', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    conn = connect_to_db(args.d, args.v)
    clusters = read_mmseqs_clusters(args.t, args.v)
    clusters = add_functions_to_clusters(clusters, conn, args.v)
    metadata_id = insert_cluster_metadata(conn, args.n, args.d, args.c, args.v)
    insert_into_database(clusters, conn, metadata_id, args.v)
    disconnect(conn, args.v)
