"""
Read the clusters from mmseqs and load them into the databases
"""

import os
import sys
import argparse

from roblib import bcolors
from Bio import SeqIO
from formatting import color
import database_handles

def load_file(gbkf, conn, verbose=True):
    """
    Load the sequences from a genbank file
    :param gbkf: genbank file
    :param conn: database connection
    :param verbose: more output
    :return:
    """

    for seq_record in SeqIO.parse(open(gbkf, 'r'), "genbank"):
        print(seq_record.id)
        print(repr(seq_record.seq))
        print(len(seq_record))




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', help='genbank file to load', required=True)
    parser.add_argument('-d', help='database file to put them in', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    conn = database_handles.connect_to_db(args.d, args.v)
    load_file(args.f, conn, args.v)