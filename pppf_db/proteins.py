"""
Functions to access the proteins database
"""

from . import phagedb, clustersdb
from pppf_databases import protein_to_fasta, connect_to_db, disconnect

def lookup_word(word):
    """
    Return the number of proteins with the word `word` in their
    product field
    :param word: the word to search for
    :param phagedb: the phage database connection
    :return : int the number of occurrences of word
    """
    con = connect_to_db(phagedb)
    c = con.cursor()
    sql = "select count(1) from protein_fts where product match ?"
    ex = c.execute(sql, [word])
    return ex.fetchone()[0]


def print_all_proteins():
    """
    Print all the proteins to stdout
    :return:  nothing
    """

    con = connect_to_db(phagedb)
    protein_to_fasta(con)
    disconnect(con)
