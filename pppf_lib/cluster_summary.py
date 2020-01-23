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
from database_handles import connect_to_db

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

    # don't forget the last cluster!
    if lastclid:
        cls.append(Cluster(lastclid, lastclid, thiscls))
        cc += 1

    if verbose:
        sys.stderr.write(f"{color.BLUE}There were {cc} clusters{color.ENDC}\n")
    return cls

def summarize_a_cluster(cl, cur, verbose=False):
    """
    Extract some information about each cluster and add it to the Cluster object
    :param cl: the cluster object
    :param cur: the database connection cursor
    :param verbose: more output
    :return: the modified cluster object
    """

    mems = list(cl.members)
    if cl.number_of_members > 999:
        sys.stderr.write(f"{color.PINK}The cluster id {cl.id} has {cl.number_of_members} members. Only processing 999{color.ENDC}\n")
        mems = mems[0:999]

    protein_query = f"select accession, length, product from protein where accession in ({','.join(['?']*len(mems))})"
    cur.execute(protein_query, mems)

    lens = []
    shortest = [None, 10000]
    longest  = [None, 0]
    functions = set()

    for row in cur.fetchall():
        lens.append(row[1])
        if row[1] > longest[1]:
            longest = [row[0], row[1]]
        if row[1] < shortest[1]:
            shortest = [row[0], row[1]]
        functions.add(row[2])

    cl.longest_id = longest[0]
    cl.longest_len = longest[1]
    cl.shortest_id = shortest[0]
    cl.shortest_len = shortest[1]
    cl.number_of_functions = len(functions)
    cl.all_functions = functions
    return cl

def summarize_clusters(cls, dbf, summf, verbose=False):
    """
    Extract some information about each cluster and add it to the Cluster object
    :param cls: the cluster object
    :param dbf: the database file
    :param summf: the summary file to write
    :param verbose: more output
    :return: the modified cluster object
    """

    updatedcls = []

    conn = connect_to_db(dbf, verbose)
    if not conn:
        sys.stderr.write(f"{color.RED}Could not connect to database {dbf}{color.ENDC}\n")
        sys.exit(-1)

    if verbose:
        sys.stderr.write(f"{color.GREEN}Adding summary data{color.ENDC}\n")

    cur = conn.cursor()

    out = open(summf, 'w')
    out.write("Count\tExemplar\tNumber of proteins\tNumber of functions\tShortest protein\tLongest protein\n")
    for cl in cls:
        nc = summarize_a_cluster(cl, cur, verbose)
        out.write(f"{nc.exemplar}\t{nc.number_of_members}\t{nc.number_of_functions}\t{nc.shortest_len}\t{nc.longest_len}\n")
        updatedcls.append(nc)

    out.close()

    return updatedcls

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Summarize a set of clusters from mmseqs (or elsewhere)')
    parser.add_argument('-t', help='mmseqs format tsv file of clusters')
    parser.add_argument('-d', help='sqlite database file', required=True)
    parser.add_argument('-s', help='summary file to write', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    clusters = None
    if args.t:
        clusters = read_mmseqs_clusters(args.t, args.v)
    else:
        sys.stderr.write(f"{color.RED}Please provide a cluster file{color.ENDC}\n")

    newclusters = summarize_clusters(clusters, args.d, args.s, args.v)



