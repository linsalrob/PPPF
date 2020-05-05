"""
A generic genbank class that holds the connection inforamtion
"""

import os
import sys
from pppf_accessories import color
from Bio import Entrez

__author__ = 'Rob Edwards'

class GenBank():
    """
    A generic genbank class
    """

    def __init__(self, email, api_key, **kwargs):
        """
        Initialize the object.
        """
        
        self.entrez = Entrez
        
        if email:
            self.entrez.email = email
        else:
            raise Exception("Please provide an email to the Entrez application")

        if api_key:
            self.entrez.api_key = api_key
        else:
            raise Exception("Please provide an api_key to the Entrez application")

        
        self.db = kwargs.get('db', 'nuccore')
        self.rettype = kwargs.get('rettype', 'gb')
        self.retmode = kwargs.get('retmode', 'text')
        self.number_of_requests = kwargs.get('self.number_of_requests', 250)
        self.verbose = kwargs.get('verbose', False)


