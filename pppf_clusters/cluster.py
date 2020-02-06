"""
A class representing a cluster of proteins
"""

from uuid import uuid4
from pppf_lib import is_hypothetical

class Cluster:
    """
    A cluster of sequences has an ID that should be unique, an exemplar sequence, and a set of members.
    For convenience, the exemplar is also guaranteed to be one of the members so that you don't need to search through both
    the members and the examplar.

    The ID can also be the exemplar name too!

    :ivar id: A unique ID. If not provided we will calculate one
    :ivar exmmplar: The exemplar sequence
    :ivar members: a list or set (or settable object) of the members of the cluster
    :ivar longest_id: the id of the longest protein or None if not set
    :ivar longest_len: the length of the longest protein or None if not set
    :ivar shortest_id: the id of the shortest protein or None if not set
    :ivar shortest_len: the length of the shortest protein or None if not set
    :ivar average_size: the average size of the members of the set or None if not set
    :ivar number_of_members: the number of members in the cluster
    :ivar number_of_functions: the number of unique functions in the cluster
    :ivar functions: a dict of functions and their frequency
    :ivar function: the most abundant function
    :ivar only_hypothetical: True is the set only has proteins whose functions are hypothetical.

    """

    def __init__(self, id, exemplar, members):
        """
        Initiate a cluster of sequences
        :param id: the unique ID. Can be None to autogenerate one
        :param exemplar: the exemplar sequence
        :param members: a list or set of the members of the sequence
        """
        if id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.exemplar = exemplar
        self.members = set(members)
        self.members.add(exemplar)
        self.longest_id = None
        self.longest_len = None
        self.shortest_id = None
        self.shortest_len = None
        self.average_size = None
        self.number_of_members = len(self.members)
        self.functions = {}
        self.function = None
        self.number_of_functions = 0
        self.only_hypothetical = None

    def is_hypothetical(self):
        """
        Is the function associated with this class hypothetical?
        :return: boolean: True if all the functions are hypothetical. False if not
        """

        if self.only_hypothetical:
            return self.only_hypothetical

        for f in self.functions:
            if not is_hypothetical(f):
                self.only_hypothetical = False
                return False

        self.only_hypothetical = True
        return True
