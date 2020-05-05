"""
init file for pppf_db
"""

from .db_paths import phagedb, clustersdb
from .database_handles import connect_to_db, disconnect
from .protein import lookup_word
from .dump_protein_fasta import print_all_proteins


__all__ = [
    'phagedb', 'clustersdb', 'connect_to_db', 'disconnect',
    'print_all_proteins'
]