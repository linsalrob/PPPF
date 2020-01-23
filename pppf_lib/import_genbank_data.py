"""
Import data from genbank into sqlite3


"""

import os
import sys
import argparse
from database_handles import connect_to_db, disconnect

def load_functions(tabf, dbfile, overwrite=False, verbose=False):
    """
    Load the protein data into the database from a tab separated file. This is made by genbank2flatfile.pl sequences.gbk > sequences.tbl
    :param tabf: protein tabular output
    :param db: database file to write
    :param overwrite: overwrite the existing database (will not overwrite by default)
    :param verbose: more output
    :return:
    """

    if os.path.exists(dbfile) and not overwrite:
        sys.stderr.write("Sorry, {} already exists. Please set the overwrite flag\n".format(dbfile))
        sys.exit(-1)

    conn = connect_to_db(dbfile, verbose=verbose)

    conn.execute("""
        CREATE TABLE genome (
            identifier TEXT,
            source_file TEXT, 
            accession TEXT, 
            length INTEGER, 
            name TEXT
            )""")

    conn.execute("""
        CREATE TABLE gene (
        accession TEXT,
        contig TEXT,
        start INTEGER,
        end INTEGER,
        strand INTEGER,
        length INTEGER,
        dna_sequence TEXT,
        other_ids TEXT
        )""")

    conn.execute("""
        CREATE TABLE protein (
        accession TEXT,
        contig TEXT,
        protein_sequence TEXT,
        length INTEGER,
        product TEXT,
        other_ids TEXT
        )""")


    conn.commit()

    genome_insert = "INSERT INTO genome (identifier, source_file, accession, length, name) VALUES (?, ?, ?, ?, ?)"

    gene_insert = "INSERT INTO gene (accession, contig, start, end, strand, dna_sequence, length, other_ids) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

    protein_insert = "INSERT INTO protein (accession, contig, protein_sequence, length, product, other_ids) VALUES (?, ?, ?, ?, ?, ?)"

    with open(tabf, 'r') as f:
        for l in f:
            p = l.strip().split("\t")
            conn.execute(genome_insert, p[0:5])
            conn.execute(gene_insert, [p[5], p[2]] + p[6:9] + [p[10], len(p[10]), p[12]])
            conn.execute(protein_insert, [p[5], p[2], p[9], len(p[9]), p[11], p[12]])

    disconnect(conn, verbose=verbose)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load data from a protein table into an SQLlite database')
    parser.add_argument('-f', help='protein table (output from genbank2flatfile.pl sequences.gbk > sequences.tbl)', required=True)
    parser.add_argument('-d', help='SQLite3 database', required=True)
    parser.add_argument('-x', help='force overwriting of the database', action='store_true')
    parser.add_argument('-v', help='verbose output', action='store_true', default=False)
    args = parser.parse_args()

    load_functions(args.f, args.d, args.x, args.v)

