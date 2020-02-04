"""
The SQLite table definitions. See the [Schema](../Schema.md) documentation for more details.
"""

import sys
import argparse

from databases import database_handles
from formatting import color

def define_genome_table(conn, verbose=False):
    """
    Define the genome table
    :param conn: The database connection
    :param verbose: more output
    :return:
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating GENOME table{color.ENDC}\n")

    conn.execute("""
        CREATE TABLE genome (
                genome_id INTEGER PRIMARY KEY,
                identifier TEXT,
                source_file TEXT, 
                accession TEXT, 
                length INTEGER, 
                name TEXT,
                sequence TEXT, 
                sequence_md5 TEXT
            )""")
    conn.execute("CREATE UNIQUE INDEX genome_idx1 ON genome(genome_id);")
    conn.execute("CREATE INDEX genome_idx2 ON genome(genome_id, identifier);")
    conn.execute("CREATE INDEX genome_idx3 ON genome(genome_id, accession);")
    conn.commit()

def define_gene_table(conn, verbose=False):
    """
    Define the gene table
    :param conn: The database connection
    :param verbose: more output
    :return:
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating GENE table{color.ENDC}\n")

    conn.execute("""
        CREATE TABLE gene (
            gene_id INTEGER PRIMARY KEY,
            accession TEXT,
            contig TEXT,
            start INTEGER,
            end INTEGER,
            strand INTEGER,
            length INTEGER,
            dna_sequence TEXT,
            protein INTEGER,
            other_ids TEXT,
            dna_sequence_md TEXT
        )""")
    conn.execute("CREATE UNIQUE INDEX gene_idx1 ON gene(gene_id);")
    conn.execute("CREATE INDEX gene_idx2 ON gene(accession, gene_id);")
    conn.execute("CREATE INDEX gene_idx3 ON gene(protein, gene_id);")
    conn.execute("CREATE INDEX gene_idx4 ON gene(dna_sequence_md, gene_id);")
    conn.commit()


def define_protein_table(conn, verbose=False):
    """
    Define the protein table
    :param conn: The database connection
    :param verbose: more output
    :return:
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating PROTEIN table{color.ENDC}\n")

    conn.execute("""
        CREATE TABLE protein (
            protein_id INTEGER PRIMARY KEY,
            accession TEXT,
            contig TEXT,
            gene INTEGER,
            protein_sequence TEXT,
            length INTEGER,
            product TEXT,
            other_ids TEXT,
            protein_sequence_md5  TEXT
        )""")
    conn.execute("CREATE UNIQUE INDEX protein_idx1 ON protein(protein_id);")
    conn.execute("CREATE INDEX protein_idx2 ON protein(accession, protein_id);")
    conn.execute("CREATE INDEX protein_idx3 ON protein(gene, protein_id);")
    conn.execute("CREATE INDEX protein_idx4 ON protein(protein_sequence_md5, protein_id);")
    conn.execute("CREATE INDEX protein_idx5 ON protein(protein_sequence_md5, protein_sequence);")
    conn.commit()

def define_clusterdefinitions_table(conn, verbose=False):
    """
    Define the clusterdefinitions table
    :param conn: The database connection
    :param verbose: more output
    :return:
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating CLUSTERDEFINITION table{color.ENDC}\n")

    conn.execute("""
        CREATE TABLE clusterdefinition (
            clusterdefinition_id INTEGER PRIMARY KEY,
            uuid TEXT,
            name TEXT,
            description TEXT,
            command TEXT
        )""")
    conn.execute("CREATE UNIQUE INDEX clusterdefinition_idx1 ON clusterdefinition(clusterdefinition_id);")
    conn.execute("CREATE UNIQUE INDEX clusterdefinition_idx2 ON clusterdefinition(clusterdefinition_id, uuid);")
    conn.commit()

def define_cluster_table(conn, verbose=False):
    """
    Define the cluster table
    :param conn: The database connection
    :param verbose: more output
    :return:
    """
    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating CLUSTER table{color.ENDC}\n")

    conn.execute("""
        CREATE TABLE cluster (
            cluster_id INTEGER PRIMARY KEY,
            uuid TEXT,
            definition TEXT,
            members TEXT,
            function TEXT,
            altfunction TEXT
        )""")
    conn.execute("CREATE UNIQUE INDEX cluster_idx1 ON cluster(cluster_id);")
    conn.execute("CREATE UNIQUE INDEX cluster_idx2 ON cluster(cluster_id, uuid);")
    conn.commit()


def define_proteinclusters_table(conn, verbose=False):
    """
    Define the proteincluster table
    :param conn: The database connection
    :param verbose: more output
    :return:
    """
    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating PROTEINCLUSTER table{color.ENDC}\n")

    conn.execute("""
        CREATE TABLE proteincluster (
            proteincluster_id INTEGER PRIMARY KEY,
            protein INTEGER NOT NULL,
            cluster INTEGER NOT NULL,
            FOREIGN KEY(protein) REFERENCES protein(protein_id)
            FOREIGN KEY(protein) REFERENCES cluster(cluster_id)
        )""")
    conn.execute("CREATE UNIQUE INDEX proteincluster_idx1 ON proteincluster(proteincluster_id);")
    conn.execute("CREATE INDEX proteincluster_idx2 ON proteincluster(proteincluster_id, protein);")
    conn.execute("CREATE INDEX proteincluster_idx3 ON proteincluster(proteincluster_id, cluster);")
    conn.execute("CREATE INDEX proteincluster_idx4 ON proteincluster(protein, cluster);")
    conn.execute("CREATE INDEX proteincluster_idx5 ON proteincluster(cluster, protein);")
    conn.commit()


def define_all_tables(conn, verbose=False):
    """
    Just run all the above definitions
    :param conn: The database connection
    :param verbose: more output
    :return:
    """

    define_genome_table(conn, verbose)
    define_gene_table(conn, verbose)
    define_protein_table(conn, verbose)
    define_clusterdefinitions_table(conn, verbose)
    define_cluster_table(conn, verbose)
    define_proteinclusters_table(conn, verbose)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create tables for a database')
    parser.add_argument('-d', help='database file name', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    conn = database_handles.connect_to_db(args.d, args.v)
    define_all_tables(conn, args.v)
    conn.commit() # final commit to make sure everything saved!
    database_handles.disconnect(conn, args.v)