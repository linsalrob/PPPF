"""
Make a fasta file of all the proteins
"""

import os
import sys
import argparse

from pppf_accessories import color
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

    if args.v:
        sys.stderr.write(f"{color.GREEN}Loaded {len(cl)} proteins{color.ENDC}\n")

    ex = pcur.execute("select protein_md5sum, protein_sequence from protein_sequence")
    n = 0
    for (m, s) in ex.fetchall():
        n += 1
        if m not in cl:
            print(f">{m}\n{s}")
    if args.v:
        sys.stderr.write(f"{color.GREEN}Tested {n} proteins{color.ENDC}\n")

