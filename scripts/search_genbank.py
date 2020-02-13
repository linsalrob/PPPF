"""
Search genbank for something
"""

import os
import sys
import argparse
from pppf_lib import GenBankSearch, color
__author__ = 'Rob Edwards'


def search_to_ids(term, outfile=None, verbose=False):
    """
    Search genbank and return a list of IDs.

    Note that we actually make two calls, first to get the number of 
    records and then to get all the records. A better solution would
    be to use the history mechanism of eutils
    """
    
    if verbose:
        sys.stderr.write(f"{color.GREEN}Searching!{color.ENDC}\n")

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
        'verbose': verbose,
        'term': term, 
    }

    if verbose:
        sys.stderr.write(f"{color.BLUE}Performing first search to see how many records to retrieve{color.ENDC}\n")

    gb = GenBankSearch(**kwargs)
    results = gb.search()
    # this is a dict and we need the number of records
    kwargs['retmax'] = results['Count']
    if verbose:
        sys.stderr.write(f"{color.BLUE}\tRetrieving {results['Count']} records{color.ENDC}\n")
    # now do the search again, this time getting all the records
    gb = GenBankSearch(**kwargs)
    results = gb.search()
    
    if outfile:
        with open(outfile, 'w') as out:
            out.write("\n".join(results['IdList']))
    else:
        print("\n".join(results['IdList']))




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=' ')
    parser.add_argument('-t', help='term to search for ', required=True)
    parser.add_argument('-o', help='output file')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    search_to_ids(args.t, args.o, args.v)



