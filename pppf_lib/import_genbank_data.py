"""
Import data from genbank into sqlite3


"""

import os
import sys
from .database_handles import connect_to_db, disconnect

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
            id INTEGER AUTOINCREMENT, 
            identifier TEXT,
            source_file TEXT, 
            accession TEXT, 
            length INTEGER, 
            name TEXT
            )""")

    conn.execute("""
        CREATE TABLE protein (
        id INTEGER AUTOINCREMENT, 
        accession TEXT,
        start INTEGER,
        end INTEGER,
        strand INTEGER,
        protein_sequence TEXT,
        dna_sequence TEXT,
        product TEXT,
        other_ids TEXT
        )""")

    conn.commit()

    genome_insert = "INSERT INTO genome (identifier, source_file, accession, length, name) VALUES (?, ?, ?, ?, ?)"
    protein_insert = "INSERT INTO protein (accession, start, end, strand, protein_sequence, dna_sequence, product, other_ids)" \
                     " VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

    with open(tabf, 'r') as f:
        for l in f:
            p = l.strip().split("\t")
            conn.execute(genome_insert, p[0:5])
            conn.execute(protein_insert, p[5:])

    disconnect(conn, verbose=verbose)

