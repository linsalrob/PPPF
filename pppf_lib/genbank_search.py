"""

Search genbank and return a list of ccessions
"""
import os
import sys
from pppf_accessories import color
from pppf_lib import GenBank

__author__ = 'Rob Edwards'

class GenBankSearch(GenBank):
    """
    A genbank search object. This is what we are going to search for
    """


    def __init__(self, email, api_key, **kwargs):
        """
        Initialize the object.
        """

        GenBank.__init__(self, email, api_key, **kwargs)

        self.retmax = kwargs.get('retmax', 5)
        self.term = kwargs.get('term', None)
        self.outputfile = kwargs.get('outputfile', None)
    
    def search(self):
        """
        Do  the searchn and return the parsed object
        """
        
        handle = self.entrez.esearch(db=self.db, term=self.term, retmax=self.retmax)
        return self.entrez.read(handle)



