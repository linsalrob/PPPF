"""
We have multiple instances of the same protein based on md5sum. How often do they have different functions
"""

import os
import sys
import argparse
from pppf_databases import connect_to_db, disconnect


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Plot a heatmap")
    parser.add_argument('-p', help='phages database', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    dbc = connect_to_db(args.p, args.v)
    cur = dbc.cursor()

    ex = cur.execute("select product, protein_md5sum from protein")
    counts = {}
    for (p,m) in ex.fetchall():
        if m not in counts:
            counts[m] = {}
        counts[m][p] = counts[m].get(p, 0) + 1

    for m in counts:
        print(f"{len(counts[m])}\t{m}")