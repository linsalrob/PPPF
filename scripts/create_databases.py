"""
create the pppf_databases
"""

import os
import sys
import argparse

from pppf_accessories import color
from pppf_databases import load_genbank_file, connect_to_db, disconnect, define_phage_tables, define_cluster_tables



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a database and load it with GenBank data")
    parser.add_argument('-p', help='Phage SQL output database')
    parser.add_argument('-c', help='clusters SQLite database')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()


    if args.p:
        sys.stderr.write(f"{color.BOLD}{color.BLUE}Defining Phage Tables{color.ENDC}\n")
        if not os.path.exists(args.p):
            with open(args.p, 'w') as out:
                True
        phageconn = connect_to_db(args.p, args.v)
        define_phage_tables(phageconn, args.v)
        phageconn.commit()  # final commit to make sure everything saved!
        disconnect(phageconn, args.v)

    if args.c:
        sys.stderr.write(f"{color.BOLD}{color.BLUE}Defining Cluster Tables{color.ENDC}\n")
        if not os.path.exists(args.c):
            with open(args.c, 'w') as out:
                True
        clconn    = connect_to_db(args.c, args.v)
        define_cluster_tables(clconn, args.v)
        clconn.commit()
        disconnect(clconn, args.v)

    if not args.p and not args.c:
        sys.stderr.write(f"{color.RED}Nothing to do!{color.ENDC}\n")
