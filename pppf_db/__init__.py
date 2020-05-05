"""
init file for pppf_db
"""

from .db_paths import phagedb, clustersdb
from .database_handles import connect_to_db, disconnect
from .proteins import lookup_word, print_all_proteins
from .genomes import list_all_genomes

__all__ = [
    'phagedb', 'clustersdb',
    'connect_to_db', 'disconnect',
    'lookup_word', 'print_all_proteins',
    'list_all_genomes'
]