"""
create the pppf_databases
"""

import os
import sys
import argparse

from pppf_lib import color
from pppf_databases import load_genbank_file, connect_to_db, disconnect, define_all_tables



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a database and load it with GenBank data")
    parser.add_argument('-f', help='genbank file to load', required=True)
    parser.add_argument('-d', help='SQL output database', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    conn = connect_to_db(args.d, args.v)
    sys.stderr.write(f"{color.BOLD}{color.BLUE}Defining Tables{color.ENDC}\n")
    define_all_tables(conn, args.v)
    sys.stderr.write(f"{color.BOLD}{color.BLUE}Loading data{color.ENDC}\n")
    load_genbank_file(args.f, conn, args.v)
    disconnect(conn, args.v)