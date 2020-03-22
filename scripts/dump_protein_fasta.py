"""

"""

import os
import sys
import argparse
from pppf_databases import protein_to_fasta, connect_to_db, disconnect

__author__ = 'Rob Edwards'





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=' ')
    parser.add_argument('-p', help="phage sqlite database", required=True)
    parser.add_argument('-f', help='output fasta file', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    conn = connect_to_db(args.d, args.v)
    protein_to_fasta(conn, args.f, args.v)
    disconnect(conn, args.v)


