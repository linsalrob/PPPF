"""
A class representing a cluster of proteins
"""

from uuid import uuid4

class Cluster:
    """
    A cluster of sequences has an ID that should be unique, an exemplar sequence, and a set of members.
    For convenience, the exemplar is also guaranteed to be one of the members so that you don't need to search through both
    the members and the examplar.

    The ID can also be the exemplar name too!

    :ivar id: A unique ID. If not provided we will calculate one
    :ivar exmmplar: The exemplar sequence
    :ivar members: a list or set (or settable object) of the members of the cluster
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
        self.average_size = 0
        self.number_of_members = len(self.members)
        self.functions = set()
        self.number_of_functions = 0