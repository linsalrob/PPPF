"""
What is the function of the first protein in the genome?
"""

import os
import sys
import argparse
from database_handles import connect_to_db, disconnect

__author__ = 'Rob Edwards'
__copyright__ = 'Copyright 2020, Rob Edwards'
__credits__ = ['Rob Edwards']
__license__ = 'MIT'
__maintainer__ = 'Rob Edwards'
__email__ = 'raedwards@gmail.com'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=" ")
    parser.add_argument('-d', help='phage database', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    dbcon = connect_to_db(args.d, args.v)
    cur = dbcon.cursor()

    gene_query = "select gene_rowid, contig, start, end, protein from gene"
    exc = cur.execute(gene_query)

    firstgene = {}
    for tple in exc.fetch_row():
        if contig not in firstgene:
            firstgene[contig] = tple
        l = min(tple[2], tple[3])
        if l < firstgene[contig][2] or l < firstgene[contig][2]:
            firstgene[contig] = tple

    protein_query = "select protein_id, product, locus_tag from protein where protein_rowid = ?"
    for contig in firstgene:
        exc = cur.execute(protein_query, firstgene[contig][4])
        tple = exc.fetch_one()
        print("\t".join(map(str, firstgene[contig] + tple)))
