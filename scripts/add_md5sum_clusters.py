"""
Do not use! This is just to update the database with a new table that I added
"""

import os
import sys
import argparse
from pppf_databases import connect_to_db, disconnect
from pppf_lib import color

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-c', help='clusters db', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()
    dbc = connect_to_db(args.c, args.v)
    cur = dbc.cursor()

    # define the table
    if args.v:
        sys.stderr.write(f"{color.GREEN}Creating MD5CLUSTERS table{color.ENDC}\n")

    cur.execute("""
        CREATE TABLE md5cluster (
            md5cluster_rowid INTEGER PRIMARY KEY,
            protein_md5sum TEXT NOT NULL,
            cluster INTEGER NOT NULL,
            FOREIGN KEY(cluster) REFERENCES cluster(cluster_rowid)
        )""")
    cur.execute("CREATE UNIQUE INDEX md5cluster_idx1 ON md5cluster(md5cluster_rowid);")
    cur.execute("CREATE INDEX md5cluster_idx2 ON md5cluster(md5cluster_rowid, protein_md5sum);")
    cur.execute("CREATE INDEX md5cluster_idx3 ON md5cluster(md5cluster_rowid, cluster);")
    cur.execute("CREATE INDEX md5cluster_idx4 ON md5cluster(protein_md5sum, cluster);")
    cur.execute("CREATE INDEX md5cluster_idx5 ON md5cluster(cluster, protein_md5sum);")
    dbc.commit()



    # get all the clusters
    ex = cur.execute("select cluster_rowid, members from cluster")
    for (i,m) in ex.fetchall():
        for o in m.split(","):
            cur.execute("INSERT INTO md5cluster (protein_md5sum, cluster) VALUES (?,?)", [o, i])
    dbc.commit()