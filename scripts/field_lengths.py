"""
For each field in the database get the longest entry in that database.

We use this to define the field lengths, eg, in PPPF_Website.

I realize this is cicular, because you need the database loaded to get the longest
field lengths to define the database!
"""

import os
import sys
import argparse
import pppf_db
from pppf_databases import connect_to_db, disconnect

__author__ = 'Rob Edwards'
__copyright__ = 'Copyright 2020, Rob Edwards'
__credits__ = ['Rob Edwards']
__license__ = 'MIT'
__maintainer__ = 'Rob Edwards'
__email__ = 'raedwards@gmail.com'


for db in pppf_db.phagedb, pppf_db.clustersdb:
    print(f"Fields in {db}")
    con = connect_to_db(db)
    cursor = con.cursor()
    exc = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for tbltpl in exc.fetchall():
        tbl = tbltpl[0]
        print(f"\tTable: {tbl}")
        cd = con.execute(f"select * from {tbl} limit 1")
        names = list(map(lambda x: x[0], cd.description))
        for fld in names:
            lfsql = f"select length({fld}) from {tbl} order by length({fld}) DESC limit 1;"
            lfexc = cursor.execute(lfsql)
            print(f"{tbl} :: {fld} :: {lfexc.fetchone()[0]}")


