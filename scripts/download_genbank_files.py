"""
Download some genbank files from a file with a list of accessions, 
one per line
"""

import os
import sys
import argparse
from pppf_lib import color
from pppf_lib import GenBankDownload

__author__ = 'Rob Edwards'


def read_accessions(fname, verbose=False):
    """
    Read the file of accessions and return a list
    """
    if verbose:
        sys.stderr.write(f"{color.GREEN}Reading accessions{color.ENDC}\n")

    accs = []
    with open(fname, 'r') as f:
        for l in f:
            accs.append(l.strip())
    return accs

def download_files(accessions, outputfile, directory=None, verbose=False):
    """
    Do the download
    """
    if verbose:
        sys.stderr.write(f"{color.GREEN}Downloading data{color.ENDC}\n")

    ncbi_api_key = os.environ.get("NCBI_API_KEY", None)
    if not ncbi_api_key:
        sys.stderr.write(f"{color.RED}FATAL:{color.ENDC} Please define the NCBI_API_KEY environment variable with a valid NCBI API key\n")
        sys.exit(-1)


    email = os.environ.get("EMAIL", None)
    if not email:
        sys.stderr.write(f"""
            {color.RED}FATAL:{color.ENDC}
            To make use of NCBI's E-utilities, NCBI requires you to specify your email address with each request
            Please define an environment variable called EMAIL
            For example, export EMAIL=anemail@org.com\n""");
        sys.exit(-1)

    kwargs = {
        'api_key': ncbi_api_key,
        'email': email,
        'outputfile': outputfile,
        'directory': directory,
        'verbose': verbose,
        'accessions': accessions
    }

    gb = GenBankDownload(**kwargs)
    gb.download()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download some genbank accessions')
    parser.add_argument('-f', help='file of accessions to download, one per line', required=True)
    parser.add_argument('-o', help='output file (default: sequences,gb)', default='sequences.gb')
    parser.add_argument('-d', help='Directory to write to')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    accs = read_accessions(args.f, args.v)
    download_files(accs, args.o, args.d, args.v)




