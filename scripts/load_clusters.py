"""

"""

import os
import sys
import argparse

from pppf_databases import connect_to_db, disconnect
from pppf_clusters import read_mmseqs_clusters, add_functions_to_clusters, insert_cluster_metadata, insert_into_database

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load the cluster information into the databases')
    parser.add_argument('-p', '--phage', help='Phage SQL database', required=True)
    parser.add_argument('-c', '--clusters', help='Clusters SQL database', required=True)
    parser.add_argument('-t', '--tsv', help='Cluster tsv file', required=True)
    parser.add_argument('-n', '--name', help='Cluster name (short text)', required=True)
    parser.add_argument('-d', '--description', help='Cluster description (human readable text)', required=True)
    parser.add_argument('-c', '--cli', help='Cluster command line (bash)', required=True)
    parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')
    args = parser.parse_args()

    phageconn = connect_to_db(args.phage, args.verbose)
    clconn = connect_to_db(args.clusters, args.verbose)
    clusters = read_mmseqs_clusters(args.tsv, args.verbose)
    (clusters, protein_info) = add_functions_to_clusters(clusters, phageconn, args.verbose)
    metadata_id = insert_cluster_metadata(clconn, args.name, args.description, args.cli, args.verbose)
    insert_into_database(clusters, clconn, phageconn, metadata_id, protein_info, args.verbose)
    disconnect(phageconn, args.verbose)
    disconnect(clconn, args.verbose)
