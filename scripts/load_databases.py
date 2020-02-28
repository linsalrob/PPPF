"""
create the pppf_databases
"""

import os
import sys
import argparse

from pppf_lib import color
from pppf_databases import load_genbank_file, connect_to_db, disconnect, define_all_tables



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Load the phage database with GenBank data")
    parser.add_argument('-f', help='genbank file to load', nargs="+", required=True)
    parser.add_argument('-p', help='Phage SQL database', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    conn = connect_to_db(args.p, args.v)
    sys.stderr.write(f"{color.BOLD}{color.BLUE}Loading data{color.ENDC}\n")
    count = 0
    tc = len(args.f)
    for f in args.f:
        count+=1
        if args.v:
            sys.stderr.write(f"{color.GREEN}File {count} of {tc}: {f}\n{color.ENDC}")
        load_genbank_file(f, conn, args.v)
    disconnect(conn, args.v)
