"""

"""

import os
import sys
import argparse

from pppf_databases import connect_to_db, disconnect
from pppf_clusters import read_mmseqs_clusters, add_functions_to_clusters, insert_cluster_metadata, insert_into_database

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load the cluster information into the databases')
    parser.add_argument('-p', help='Phage SQL database', required=True)
    parser.add_argument('-c', help='Clusters SQL database', rquired=True)
    parser.add_argument('-t', help='Cluster tsv file', required=True)
    parser.add_argument('-n', help='Cluster name (short text)', required=True)
    parser.add_argument('-s', help='Cluster description (human readable text)', required=True)
    parser.add_argument('-c', help='Cluster command line (bash)', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    phageconn = connect_to_db(args.p, args.v)
    clconn = connect_to_db(args.c, args.v)
    clusters = read_mmseqs_clusters(args.t, args.v)
    (clusters, protein_info) = add_functions_to_clusters(clusters, phageconn, args.v)
    metadata_id = insert_cluster_metadata(clconn, args.n, args.s, args.c, args.v)
    insert_into_database(clusters, clconn, phageconn, metadata_id, protein_info, args.v)
    disconnect(phageconn, args.v)
    disconnect(clconn, args.v)
