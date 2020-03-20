"""
Make a fasta file of all the proteins
"""

import os
import sys
import argparse

from pppf_lib import color
from pppf_databases import connect_to_db, disconnect


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Sequences in the phage database not in a cluster")
    parser.add_argument('-p', help='phage database', required=True)
    parser.add_argument('-c', help='cluster database', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()


    pbc = connect_to_db(args.p, args.v)
    pcur = pbc.cursor()

    dbc = connect_to_db(args.c, args.v)
    ccur = dbc.cursor()

    cl = set()
    ex = ccur.execute("select protein_md5sum, cluster from md5cluster")
    for (m, c) in ex.fetchall():
        cl.add(m)

    ex = pcur.execute("select protein_md5sum, protein_sequence from protein_sequence")
    for (m, s) in ex.fetchall():
        if m not in cl:
            print(f">{m}\n{s}")
