"""
Just print some cluster member information
"""

import os
import sys
import argparse

from roblib import bcolors
from pppf_databases import connect_to_db, disconnect
from pppf_clusters import read_mmseqs_clusters, add_functions_to_clusters
from pppf_lib import color

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load the cluster information into the databases')
    parser.add_argument('-d', help='SQL database', required=True)
    parser.add_argument('-t', help='Cluster tsv file', required=True)
    parser.add_argument('-v', help='verbose output', default=True, action='store_true')
    args = parser.parse_args()

    conn = connect_to_db(args.d, args.v)
    clusters = read_mmseqs_clusters(args.t, args.v)
    for clu in clusters:
        print(f"{color.PINK}\tCluster {clu.id}{color.ENDC}")
        for m in clu.members:
            print(f"\t{color.BLUE}{m}{color.ENDC}")



#    clusters = add_functions_to_clusters(clusters, conn, args.v)

    disconnect(conn, args.v)
