"""
Download a list of accessions to a directory in GenBank format

This is a replacement for the snakemake download which doesn't work properly!

"""

import os
import sys
from pppf_lib import color
from Bio import Entrez

__author__ = 'Rob Edwards'

class GenBankDownload:
    """
    A genbank download object. This has a directory to store the results
    and a list of accessions to retrieve.
    """


    def __init__(self, email, api_key, outputfile = "sequences.gb", directory = ".", accessions = [], **kwargs):
        """
        Initialize the object.
        """

        if email:
            Entrez.email = email
        else:
            raise Exception("Please provide an email to the Entrez application")


        if api_key:
            Entrez.api_key = api_key
        else:
            raise Exception("Please provide an api_key to the Entrez application")

        self.accessions = accessions
        self.directory = directory
        self.outputfile = outputfile

        self.verbose = kwargs.get('verbose', False)
        self.db = kwargs.get('db', 'nuccore')
        self.rettype = kwargs.get('rettype', 'gb')
        self.retmode = kwargs.get('retmode', 'text')
        self.number_of_requests = kwargs.get('self.number_of_requests', 500)

    def chunk_accessions(self):
        """
        Split the list into the number of elements to request
        """
        for i in range(0, len(self.accessions), self.number_of_requests):
            yield self.accessions[i:i+self.number_of_requests]

    def download(self):
        """
        Download the accessions in self.accessions to the directory
        """

        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        
        out = open(os.path.join(self.directory, self.outputfile), 'w')

        for acc in self.chunk_accessions():
            if self.verbose:
                sys.stderr.write(f"{color.GREEN}Getting {acc}{color.ENDC}\n")
            handle = Entrez.efetch(id=",".join(acc), 
                                   db=self.db, 
                                   rettype=self.rettype, 
                                   retmode=self.retmode)
            out.write(handle.read())
        out.close()




