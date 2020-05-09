"""
Summarize the cluster information. We want to get the exemplar, the number of proteins,
the range length of the proteins, and the number of unique functions.
etc.
"""

import sys
import argparse
import pickle
import jsonpickle

from pppf_clusters.cluster import Cluster
from pppf_databases import connect_to_db
from pppf_lib import is_hypothetical
from pppf_accessories import color

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
                    cls.append(Cluster(None, lastclid, thiscls))
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

def cluster_is_hypothetical(cl, verbose=False):
    """
    Check the functions of the members of a cluster and determine whether they are
    all hypothetical
    :param cl: the cluster with enriched data
    :param verbose: more output
    :return: True if all hypothetical. False if not
    """

    for f in cl.functions:
        if not is_hypothetical(f):
            return False

    return True



def enrich_a_cluster(clid, mems, phagedb, exout=None, verbose=False):
    """
    Extract some information about each cluster and add it to the Cluster object
    :param clid: cluster id
    :param mems: the members of the cluster
    :param phagedb: the phage genome sqlite file
    :param exout: extended output file. If you want to add more data to the clusters (e.g. functions and lengths)
    :param verbose: more output
    :return: the modified cluster object
    """

    conn = connect_to_db(phagedb, verbose)
    cur = conn.cursor()

    lens = []
    shortest = [None, 10000]
    longest  = [None, 0]
    functions = {}

    maxn = 500
    c = 0
    e = maxn
    eout = None
    if exout:
        eout = open(exout, 'a')
    while c <= len(mems):
        if c > 0:
            sys.stderr.write(f"{color.PINK}Retrieving clusters {c}:{e} for {clid}{color.ENDC}\n")
        tm = mems[c:e]
        protein_query = f"select accession, length, product from protein where accession in ({','.join(['?']*len(tm))})"
        cur.execute(protein_query, tm)
        c = e
        e += maxn

        for row in cur.fetchall():
            if eout:
                r = "\t".join(map(str, row))
                eout.write(f'{clid}\t{r}\n')
            lens.append(row[1])
            if row[1] > longest[1]:
                longest = [row[0], row[1]]
            if row[1] < shortest[1]:
                shortest = [row[0], row[1]]
            functions[row[2]] = functions.get(row[2], 0) + 1

    if eout:
        eout.close()

    return shortest[0], shortest[1], longest[0], longest[1], functions, sum(lens)/len(lens)


def enrich_cluster_data(cls, summf, exout=None, verbose=False):
    """
    Extract some information about each cluster and add it to the Cluster object
    :param cls: the cluster object
    :param summf: the summary file to write
    :param verbose: more output
    :return: the modified cluster object
    """

    updatedcls = []


    if verbose:
        sys.stderr.write(f"{color.GREEN}Adding summary data{color.ENDC}\n")

    cur = conn.cursor()

    out = open(summf, 'w')
    out.write("Exemplar\tNumber of proteins\tNumber of functions\tShortest protein\tLongest protein\n")
    for cl in cls:
        cl.shortest_id, cl.shortest_len, cl.longest_id, cl.longest_len, cl.functions, cl.average_size =\
            enrich_a_cluster(cl.id, list(cl.members), cur, exout, verbose)
        cl.number_of_functions = len(cl.functions)
        cl.only_hypothetical = cluster_is_hypothetical(cl, verbose)
        # find the most frequent function
        allfn = sorted(cl.functions.items(), key=lambda item: item[1], reverse=True)
        cl.function = allfn[0][0]

        out.write(f"{cl.exemplar}\t{cl.number_of_members}\t{cl.number_of_functions}\t{cl.shortest_len}\t{cl.longest_len}\n")
        updatedcls.append(cl)

    out.close()

    return updatedcls

def pickle_cluster_data(cl, pf, verbose=False):
    """
    Write the revised cluster data to a pickle file to use later
    :param cl: the cluster information
    :param pf: the pickle file to write
    :param verbose: more output
    :return:
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Writing pickle data{color.ENDC}\n")

    with open(pf, 'wb') as po:
        pickle.dump(cl, po)


def json_cluster_data(cl, jf, verbose=False):
    """
    Write the cluster data in json format (not recommended for large data sets!)
    :param cl: The clusters
    :param jf: The json file to write
    :param verbose: more output
    :return:
    """


    if verbose:
        sys.stderr.write(f"{color.GREEN}Writing json data{color.ENDC}\n")

    with open(jf, 'w') as jo:
        jo.write(jsonpickle.encode(cl))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Summarize a set of clusters from mmseqs (or elsewhere)')
    parser.add_argument('-t', help='mmseqs format tsv file of clusters')
    parser.add_argument('-d', help='phage SQLite database file', required=True)
    parser.add_argument('-s', help='summary file to write', required=True)
    parser.add_argument('-p', help='pickle file to write with enriched cluster information')
    parser.add_argument('-e', help='enriched cluster output file')
    parser.add_argument('-j', help='write a json file with the enriched cluster information')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    clusters = None
    if args.t:
        clusters = read_mmseqs_clusters(args.t, args.v)
    else:
        sys.stderr.write(f"{color.RED}Please provide a cluster file{color.ENDC}\n")

    newclusters = enrich_cluster_data(clusters, args.s, args.e, args.v)

    if args.p:
        pickle_cluster_data(newclusters, args.p, args.v)

    if args.j:
        json_cluster_data(newclusters, args.j, args.v)



