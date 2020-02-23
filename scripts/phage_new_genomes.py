"""
Read a list of [gi, accession number] and find those that are not in our
database
"""

import os
import sys
import argparse
import re

from pppf_lib import color
from pppf_databases import connect_to_db, disconnect
__author__ = 'Rob Edwards'






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find new accesssions')
    parser.add_argument('-f', help='input file of [gi, accession number]', required=True)
    parser.add_argument('-d', help='phage database', required=True)
    parser.add_argument('-o', help='file to write needed IDs to', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    # note that identifier has the version.
    # Thus identifier = AF068845.1 and accession = AF068845
    # We probably want identifier!

    con = connect_to_db(args.d, args.v)
    exc = con.cursor().execute("select identifier, accession from genome")
    ids = {}
    accs = {}
    for r in exc.fetchall():
        ids[r[0]] = r[1]
        accs[r[1]] = r[0]
    
    try:
        assert len(ids) == len(accs)
    except AssertionError as e:
        sys.stderr.write(f"{color.RED}FATAL: We found {len(ids)} identifiers and {len(accs)} accessions{color.ENDC}\n")
        sys.exit(1)

    if args.v:
        sys.stderr.write(f"{color.GREEN}{len(accs)} accessions and {len(ids)} identifiers found{color.ENDC}\n")

    count = 0
    need = set()
    seen = set()
    with open(args.f, 'r') as f:
        for l in f:
            count += 1
            p = l.strip().split("\t")
            seen.add(p[1])
            if p[1] in ids or p[1] in accs:
                continue
            need.add(p[1])

    if args.v:
        sys.stderr.write(f"{color.BLUE}There are {count} lines in {args.f}. We found {len(ids)} accessions in our database and {len(need)} new ones to get. Total: {len(ids) + len(need)}{color.ENDC}\n")


    # ids in our database not in your file
    notin = set()
    for n in ids:
        if n not in seen:
            notin.add(n)
    if notin:
        sys.stderr.write(f"{color.YELLOW}{len(notin)} IDs in the database not in your file:\n")
        sys.stderr.write("\n".join(notin))
        sys.stderr.write(f"{color.ENDC}\n")

    stripver = re.compile('\.\d+$')
    for n in need:
        an = stripver.sub('', n)
        if an in accs or an in ids:
            sys.stderr.write(f"{color.PINK}NEW VERSION: {an} ({n})\n{color.ENDC}")

    with open(args.o, 'w') as out:
        out.write("\n".join(need))

