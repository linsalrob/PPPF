"""
dump all the proteins to fasta format
"""

import os
import sys
from pppf_databases import protein_to_fasta, connect_to_db, disconnect
from . import phagedb

__author__ = 'Rob Edwards'
__copyright__ = 'Copyright 2020, Rob Edwards'
__credits__ = ['Rob Edwards']
__license__ = 'MIT'
__maintainer__ = 'Rob Edwards'
__email__ = 'raedwards@gmail.com'

def print_all_proteins():
    """
    Print all the proteins to stdout
    :return:  nothing
    """

    con = connect_to_db(phagedb)
    protein_to_fasta(con)
    disconnect(con)
