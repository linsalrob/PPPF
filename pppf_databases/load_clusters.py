"""
Read the clusters from mmseqs and load them into the pppf_databases
"""

import os
import sys
import argparse

from pppf_lib import color
from Bio import SeqIO
from formatting import color
import database_handles



# TODO


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', help='genbank file to load', required=True)
    parser.add_argument('-d', help='cluster database file to put them in', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    conn = database_handles.connect_to_db(args.d, args.v)
    load_file(args.f, conn, args.v)