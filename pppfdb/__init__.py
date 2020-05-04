"""
init file for pppfdb
"""

from .db_paths import phagedb, clustersdb
from .database_handles import connect_to_db, disconnect
from .protein import lookup_word


__all__ = [
    'phagedb', 'clustersdb', 'connect_to_db', 'disconnect',
]