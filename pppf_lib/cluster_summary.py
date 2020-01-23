"""
Summarize the cluster information. We want to get the exemplar, the number of proteins,
the range length of the proteins, and the number of unique functions.
etc.
"""

import os
import sys
import argparse

from roblib import bcolors
from cluster import Cluster
from formatting import color

def read_mmseqs_clusters(clf, verbose=False):
    """
    Read all the clusters at once and return an array of clusters.
    :param clf: cluster file
    :param verbose: more output
    :return: the list of clusters
    """

    cls = []
    cc = 0
    if verbose:
        sys.stderr.write(f"{color.GREEN}Reading {clf}{color.ENDC}\n")

    lastclid = None
    thiscls = set()
    with open(clf, 'r') as f:
        for l in f:
            p = l.strip().split("\t")
            if lastclid != p[0]:
                # this is a new cluster
                if lastclid:
                    cls.append(Cluster(lastclid, lastclid, thiscls))
                    cc += 1
                lastclid = p[0]
                thiscls = set()
            thiscls.add(p[1])

    if verbose:
        sys.stderr.write(f"{color.BLUE}There were {cc} clusters{color.ENDC}\n")
    return cls

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Summarize a set of clusters from mmseqs (or elsewhere)')
    parser.add_argument('-t', help='mmseqs format tsv file of clusters')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    if args.t:
        read_mmseqs_clusters(args.t, args.v)
    else:
        sys.stderr.write(f"{color.RED}Please provide a cluster file{color.ENDC}\n")
