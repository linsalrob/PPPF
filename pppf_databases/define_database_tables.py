"""
The SQLite table definitions. See the [Schema](../Schema.md) documentation for more details.
"""

import sys
import argparse

from pppf_databases import database_handles
from pppf_accessories import color

def define_genome_table(conn, verbose=False):
    """
    Define the genome table
    :param conn: The database connection
    :param verbose: more output
    :return:
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating GENOME table{color.ENDC}\n")

    conn.cursor().execute("""
        CREATE TABLE genome (
                genome_rowid INTEGER PRIMARY KEY,
                identifier TEXT,
                source_file TEXT, 
                accession TEXT, 
                name TEXT,
                description TEXT,
                source TEXT, 
                organism TEXT,
                taxonomy TEXT,
                collection_date TEXT,
                country TEXT,
                db_xref TEXT,
                host TEXT,
                isolation_source TEXT,
                strain TEXT,
                lab_host TEXT,
                sequence TEXT, 
                sequence_md5 TEXT,
                length INTEGER
            )""")
    conn.cursor().execute("CREATE UNIQUE INDEX genome_idx1 ON genome(genome_rowid);")
    conn.cursor().execute("CREATE INDEX genome_idx2 ON genome(genome_rowid, identifier);")
    conn.cursor().execute("CREATE INDEX genome_idx3 ON genome(genome_rowid, accession);")
    conn.cursor().execute("CREATE INDEX genome_idx4 ON genome(accession, identifier);")
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

    conn.cursor().execute("""
        CREATE TABLE gene (
            gene_rowid INTEGER PRIMARY KEY,
            accession TEXT,
            contig TEXT,
            start INTEGER,
            end INTEGER,
            strand INTEGER,
            length INTEGER,
            dna_sequence TEXT,
            protein INTEGER,
            db_xref TEXT,
            dna_sequence_md TEXT
        )""")
    conn.cursor().execute("CREATE UNIQUE INDEX gene_idx1 ON gene(gene_rowid);")
    conn.cursor().execute("CREATE INDEX gene_idx2 ON gene(accession, gene_rowid);")
    conn.cursor().execute("CREATE INDEX gene_idx3 ON gene(protein, gene_rowid);")
    conn.cursor().execute("CREATE INDEX gene_idx4 ON gene(dna_sequence_md, gene_rowid);")
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

    conn.cursor().execute("""
        CREATE TABLE protein (
            protein_rowid INTEGER PRIMARY KEY,
            protein_id TEXT,
            contig TEXT,
            gene INTEGER,
            product TEXT,
            db_xref TEXT,
            protein_md5sum TEXT,
            length INTEGER,
            EC_number TEXT, 
            genename TEXT, 
            locus_tag TEXT, 
            note TEXT, 
            ribosomal_slippage TEXT, 
            transl_table TEXT,
            FOREIGN KEY (protein_md5sum) REFERENCES protein_sequence(protein_md5sum)
        )""")
    conn.cursor().execute("CREATE UNIQUE INDEX protein_idx1 ON protein(protein_rowid);")
    conn.cursor().execute("CREATE INDEX protein_idx2 ON protein(protein_id, protein_rowid);")
    conn.cursor().execute("CREATE INDEX protein_idx3 ON protein(gene, protein_rowid);")
    conn.cursor().execute("CREATE INDEX protein_idx4 ON protein(protein_md5sum, protein_rowid);")
    conn.commit()

def define_protein_sequence_table(conn, verbose=False):
    """
    The protein sequence only holds the md5sum and the sequence of the protein.

    Note: the protein -> proteinsequence is a many:one relationship so we
    can't foreign key back to proteins, but we have a foreign key that points
    to this table from proteins.

    :param conn: the connection
    :param verbose: more output
    :return:
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating protein sequence table{color.ENDC}\n")

    conn.cursor().execute("""
        CREATE TABLE protein_sequence (
            protein_sequence_rowid INTEGER PRIMARY KEY,
            protein_md5sum TEXT,
            protein_sequence TEXT
        )
    """)
    conn.cursor().execute("CREATE UNIQUE INDEX ps_idx0 ON protein_sequence(protein_md5sum);")
    conn.cursor().execute("CREATE UNIQUE INDEX ps_idx1 ON protein_sequence(protein_sequence_rowid);")
    conn.cursor().execute("CREATE INDEX ps_idx2 ON protein_sequence(protein_md5sum, protein_sequence);")
    conn.cursor().execute("CREATE INDEX ps_idx3 ON protein_sequence(protein_sequence, protein_md5sum);")
    conn.commit()
    

def define_trna_table(conn, verbose=False):
    """
    Define the tRNA table
    :param conn: the connection
    :param verbose: more output
    :return:
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating tRNA table{color.ENDC}\n")

    conn.cursor().execute("""
        CREATE TABLE trna (
            trna_rowid INTEGER PRIMARY KEY,
            accession TEXT,
            contig TEXT,
            start INTEGER,
            end INTEGER,
            strand INTEGER,
            dna_sequence TEXT,
            dna_sequence_md5 TEXT,
            codon_recognized TEXT,
            db_xref TEXT,
            gene TEXT,
            note TEXT,
            product TEXT,
            is_tmRNA INTEGER
        )
    """)
    conn.cursor().execute("CREATE UNIQUE INDEX trna_idx1 ON trna(trna_rowid);")
    conn.cursor().execute("CREATE INDEX trna_idx2 ON trna(dna_sequence_md5, dna_sequence);")
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

    conn.cursor().execute("""
        CREATE TABLE clusterdefinition (
            clusterdefinition_rowid INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            command TEXT
        )""")
    conn.cursor().execute("CREATE UNIQUE INDEX clusterdefinition_idx1 ON clusterdefinition(clusterdefinition_rowid);")
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

    conn.cursor().execute("""
        CREATE TABLE cluster (
            cluster_rowid INTEGER PRIMARY KEY,
            uuid TEXT,
            clusterdefinition INTEGER,
            members TEXT,
            exemplar TEXT, 
            longest_id TEXT, 
            longest_len INTEGER, 
            shortest_id TEXT, 
            shortest_len INTEGER, 
            average_size REAL, 
            number_of_members INTEGER, 
            functions TEXT, 
            function TEXT, 
            number_of_functions INTEGER, 
            only_hypothetical INTEGER, 
            FOREIGN KEY (clusterdefinition) REFERENCES clusterdefinition(clusterdefinition_rowid)
        )""")
    conn.cursor().execute("CREATE UNIQUE INDEX cluster_idx1 ON cluster(cluster_rowid);")
    conn.cursor().execute("CREATE UNIQUE INDEX cluster_idx2 ON cluster(cluster_rowid, uuid);")
    conn.cursor().execute("CREATE INDEX cluster_id3 ON cluster(function, functions, cluster_rowid);")
    conn.cursor().execute("CREATE INDEX cluster_id4 ON cluster(functions, function, cluster_rowid);")
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

    conn.cursor().execute("""
        CREATE TABLE proteincluster (
            proteincluster_rowid INTEGER PRIMARY KEY,
            protein INTEGER NOT NULL,
            cluster INTEGER NOT NULL,
            FOREIGN KEY(cluster) REFERENCES cluster(cluster_rowid)
        )""")
    conn.cursor().execute("CREATE UNIQUE INDEX proteincluster_idx1 ON proteincluster(proteincluster_rowid);")
    conn.cursor().execute("CREATE INDEX proteincluster_idx2 ON proteincluster(proteincluster_rowid, protein);")
    conn.cursor().execute("CREATE INDEX proteincluster_idx3 ON proteincluster(proteincluster_rowid, cluster);")
    conn.cursor().execute("CREATE INDEX proteincluster_idx4 ON proteincluster(protein, cluster);")
    conn.cursor().execute("CREATE INDEX proteincluster_idx5 ON proteincluster(cluster, protein);")
    conn.commit()

def define_md5clusters_table(conn, verbose=False):
    """
    The connection between md5 clusters and cluster Ids
    :param conn: The database connection
    :param verbose: more output
    :return:
    """
    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating MD5CLUSTERS table{color.ENDC}\n")

    conn.cursor().execute("""
        CREATE TABLE md5cluster (
            md5cluster_rowid INTEGER PRIMARY KEY,
            protein_md5sum TEXT NOT NULL,
            cluster INTEGER NOT NULL,
            FOREIGN KEY(cluster) REFERENCES cluster(cluster_rowid)
        )""")
    conn.cursor().execute("CREATE UNIQUE INDEX md5cluster_idx1 ON md5cluster(md5cluster_rowid);")
    conn.cursor().execute("CREATE INDEX md5cluster_idx2 ON md5cluster(md5cluster_rowid, protein_md5sum);")
    conn.cursor().execute("CREATE INDEX md5cluster_idx3 ON md5cluster(md5cluster_rowid, cluster);")
    conn.cursor().execute("CREATE INDEX md5cluster_idx4 ON md5cluster(protein_md5sum, cluster);")
    conn.cursor().execute("CREATE INDEX md5cluster_idx5 ON md5cluster(cluster, protein_md5sum);")
    conn.commit()



def define_phage_tables(conn, verbose=False):
    """
    Run the above definitions for phages
    :param conn: The database connection
    :param verbose: more output
    :return:
    """

    define_genome_table(conn, verbose)
    define_gene_table(conn, verbose)
    define_protein_table(conn, verbose)
    define_trna_table(conn, verbose)
    define_protein_sequence_table(conn, verbose)

def define_cluster_tables(conn, verbose=False):
    """
    Run the above definitions for clusters
    :param conn: The database connection
    :param verbose: more output
    :return:
    """

    define_clusterdefinitions_table(conn, verbose)
    define_cluster_table(conn, verbose)
    define_proteinclusters_table(conn, verbose)
    define_md5clusters_table(conn, verbose)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create tables for a database')
    parser.add_argument('-p', help='phage genome database file name')
    parser.add_argument('-c', help='cluster genome database file name')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    if args.p:
        phageconn = database_handles.connect_to_db(args.p, args.v)
        define_phage_tables(phageconn, args.v)
        phageconn.commit()  # final commit to make sure everything saved!
        database_handles.disconnect(phageconn, args.v)
    if args.c:
        clconn    = database_handles.connect_to_db(args.c, args.v)
        define_cluster_tables(clconn, args.v)
        clconn.commit()
        database_handles.disconnect(clconn, args.v)
