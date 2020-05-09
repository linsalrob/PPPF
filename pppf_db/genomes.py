"""
Access the genome information in pppf
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

def list_all_genomes():
    """
    Print all the proteins to stdout
    :return:  nothing
    """

    con = connect_to_db(phagedb)
    exc = con.cursor().execute("select description from genome")
    for d in exc.fetchall():
        print(f"{d[0]}")
    disconnect(con)
