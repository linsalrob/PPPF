"""
Download the prebuilt databases from the Edwards lab website
"""

import os
import sys
import requests
import argparse

from pppf_accessories import color
from pppf_db import phagedb, clustersdb

__author__ = 'Rob Edwards'
__copyright__ = 'Copyright 2020, Rob Edwards'
__credits__ = ['Rob Edwards']
__license__ = 'MIT'
__maintainer__ = 'Rob Edwards'
__email__ = 'raedwards@gmail.com'

PHAGE_DB_URL = "https://edwards.sdsu.edu/phage/PPPF/phages.sql"
CLUSTER_DB_URL  = "https://edwards.sdsu.edu/phage/PPPF/clusters.sql"



def download_file(url, local_filename):
    """
    Use requests to stream the file from the server in chunks
    Please see this SO thread for more information and source
    https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests

    :param url: the url of the file to download
    :param local_filename: the name of the file to write
    :return: the local file name of the saved file
    """

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename




if __name__ == '__main__':

    phageout = phagedb
    clustout = clustersdb
    outdir = os.path.dirname(phageout)

    parser = argparse.ArgumentParser(description="Download the prebuilt SQL databases from the server")
    parser.add_argument('-d', help=f"Optional directory to output the files. Otherwise they will be in {outdir}")
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    if args.d:
        clustout = os.path.join(args.d, os.path.basename(clustout))
        phageout = os.path.join(args.d, os.path.basename(phageout))
        if args.v:
            sys.stderr.write(f"{color.BLUE}Saving the phages to {phageout} and the clusters to {clustout}{color.ENDC}\n")

    outdir = os.path.dirname(phageout)
    if not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

    sys.stderr.write(f"{color.GREEN}Downloading the phages to {phageout}{color.ENDC}\n")
    download_file(PHAGE_DB_URL, phageout)

    sys.stderr.write(f"{color.GREEN}Downloading the clusters to {clustout}{color.ENDC}\n")
    download_file(CLUSTER_DB_URL, clustout)
