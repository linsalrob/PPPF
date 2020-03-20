"""
Do not use! This is just to update the database with a new table that I added
"""

import os
import sys
import argparse
from pppf_databases import connect_to_db, disconnect

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-c', help='clusters db', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()
    dbc = connect_to_db(args.c, args.v)
    cur = dbc.cursor()

    # get all the clusters
    ex = cur.execute("select cluster_rowid, members from cluster")
    for (i,m) in ex.fetchall():
        for o in m.split(","):
            cur.execute("INSERT INTO md5cluster (protein_md5sum, cluster) VALUES (?,?)", [o, i])
    dbc.commit()