"""
Download some genbank files from a file with a list of accessions, 
one per line
"""

import os
import sys
import argparse
from pppf_accessories import color
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
    parser.add_argument('-d', help='optional directory to write to. Can also be specified as part of the outputname')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()


    fname = args.o
    dirname = None
    if os.path.sep in args.o:
        fname = args.o.split(os.path.sep)[-1]
        dirname = os.path.sep.join(args.o.split(os.path.sep)[0:-1])

    if dirname and args.d and (dirname != args.d):
        sys.stderr.write(f"""
{color.RED}CONFUSED!: Sorry, I'm confused! {color.ENDC} 
Output file name has {dirname} as a path yet you also requested {args.d}
as an output path. Can you help me by choosing one or the other?\n""")
        sys.exit(-1)
    elif args.d:
        dirname = args.d


    accs = read_accessions(args.f, args.v)
    download_files(accs, fname, dirname, args.v)




