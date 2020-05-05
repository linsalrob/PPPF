"""
Download a list of accessions to a directory in GenBank format

This is a replacement for the snakemake download which doesn't work properly!

"""

import os
import sys
from pppf_accessories import color
from pppf_lib import GenBank

__author__ = 'Rob Edwards'

class GenBankDownload(GenBank):
    """
    A genbank download object. This has a directory to store the results
    and a list of accessions to retrieve.
    """


    def __init__(self, email, api_key, outputfile = "sequences.gb", directory = ".", accessions = [], **kwargs):
        """
        Initialize the object.
        """

        GenBank.__init__(self, email, api_key, **kwargs)

        self.accessions = accessions
        self.directory = directory
        self.outputfile = outputfile


    def chunk_accessions(self):
        """
        Split the list into the number of elements to request
        """
        for i in range(0, len(self.accessions), self.number_of_requests):
            if self.verbose:
                sys.stderr.write(f"{color.PINK}Chunk {i}-{i+self.number_of_requests}{color.ENDC}\n")

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
            
            try:
                handle = self.entrez.efetch(id=",".join(acc), 
                                       db=self.db, 
                                       rettype=self.rettype, 
                                       retmode=self.retmode)
                out.write(handle.read())
            except http.client.IncompleteRead as e:
                sys.stderr.write(f"{color.RED}Incomplete read{color.ENDC}\n")
                out.write(handle.read())
        out.close()




