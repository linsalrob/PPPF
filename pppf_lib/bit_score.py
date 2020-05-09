"""
Calculate a normalized bit score as a distance score.

The normalized bit score is generally defined as 1 - (bitscore / average(self-self bitscore of query and subject))
note that it is 1-b so that identical proteins have a score of 0 and can thus be used immediately as a distance
measure.

"""

import os
import sys
import argparse
from pppf_accessories import color, stream_blast_results

__author__ = 'Rob Edwards'

def self_bit_scores(blastf, verbose=False):
    """
    Generate a dict of self:self bitscores
    """


    if verbose:
        sys.stderr.write(f"{color.GREEN}Calculating self:self bitscores{color.ENDC}\n")

    ss = {}
    for b in stream_blast_results(blastf, verbose):
        if b.query == b.db:
            if b.query in ss and ss[b.query] > b.bitscore:
                continue
            ss[b.query] = b.bitscore
    return ss


def pairwise_bit_scores(blastf, ss, verbose=False):
    """
    Make a pairwise average bit score that is 
    the bitscore / average of two proteins self/self bit
    score
    ;param blastf: the blastfile
    :param ss: the self-self bitscores
    :param verbose: more output
    :return a dict of all vs. all normalized bit scores
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating scores{color.ENDC}\n")

    pb = {}

    for b in stream_blast_results(blastf, verbose):
        if b.query not in pb:
            pb[b.query] = {}
        if b.db not in pb:
            pb[b.db] = {}

        # we normalize by the bitscore of the two proteins if we can!
        if b.query in ss and b.db in ss:
            nb = 1 - (b.bitscore / ((ss[b.query] + ss[b.db])/2))
        else:
            # if we can't do that, we cheat and normalize 
            # the bit score by twice
            # the average length of the proteins
            # i.e. the sum of the lengths
            if verbose:
                sys.stderr.write(f"{color.PINK}Had to guess self:self score for {b.query} to {b.db}{color.ENDC}\n")
            nb = 1 - (b.bitscore / (b.query_length + b.subject_length + 3.3))

        if b.query in pb[b.db] and pb[b.db][b.query] > nb:
            continue
        pb[b.db][b.query] = pb[b.db][b.query] = nb

    return pb


def write_pb(outf, pb, verbose=False):
    """
    Write the pairwise bitscores to a tsv
    :param outf: output file
    :param pb: pairwise bit scores
    :param verbose: more output
    :return:
    """

    with open(outf + ".tsv", 'w') as out:
        out.write("Query\tSubject\tnBits\n")
        for p in pb:
            for q in pb[p]:
                out.write(f"{p}\t{q}\t{pb[p][q]}\n")

def write_matrix(outf, pb, verbose=False):
    """
    Print a matrix version of the pairwise bitscores
    :param outf: the matrix file to write
    :param pb: the pairwise bitscores
    :param verbose: more output
    :return:
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating scores{color.ENDC}\n")

    allkeys = list(pb.keys())

    with open(outf + ".mat", 'w') as out:
        out.write("\t".join([""] + allkeys))
        out.write("\n")
        for p in allkeys:
            out.write(p)
            for q in allkeys:
                if p == q:
                    out.write("\t0")
                elif q in pb[p]:
                    out.write(f"\t{pb[p][q]}")
                else:
                    out.write("\t1")
            out.write("\n")


def precluster(pb, cutoff, verbose=False):
    """
    Form some clusters based on the pairwise bitscores
    :param pb: pair wise bit score dictionary
    :param cutoff: maximum value to be included in a cluster (< this)
    :param verbose: more output
    :return: a set of clusters
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating clusters{color.ENDC}\n")

    clusters_by_id = {}
    id_by_clusters = {}
    clustercount = 0

    allkeys = list(pb.keys())

    # niaive clustering. Add the first protein to a cluster, and add all similar ones to it
    # repeat!


    for k in allkeys:
        currentcluster = None
        if k in clusters_by_id:
            currentcluster = clusters_by_id[k]
        else:
            currentcluster = clusters_by_id[k] = clustercount
            clustercount += 1

        # first, figure out who are friends are and what is the lowest cluster from them
        friends = {k}
        freindclusters = {clustercount}
        for j in pb[k]:
            if j == k:
                # ignore self clusters!
                continue
            if pb[k][j] > cutoff:
                continue
            friends.add(j)
            if j in clusters_by_id:
                freindclusters.add(clusters_by_id[j])
                if clusters_by_id[j] < currentcluster:
                    currentcluster = clusters_by_id[j]

        # now update friends with all members of the sets in friend clusters
        for c in freindclusters:
            if c in id_by_clusters:
                friends.update(id_by_clusters[c])

        # finally set friends to be in clustercount cluster and set id_by_clusters to include our friends

        clusters_by_id.update({x:currentcluster for x in friends})
        id_by_clusters[currentcluster] = friends
        if verbose:
            sys.stderr.write(f"{color.BLUE}Added cluster {currentcluster}{color.ENDC}\n")

    if verbose:
        sys.stderr.write(f"{color.GREEN}Maximum cluster is {clustercount} but we have {len(id_by_clusters.keys())} clusters{color.ENDC}\n")

    return id_by_clusters

def write_clusters(outf, cls, verbose=False):
    """
    Write the clusters
    :param outf: cluster output file
    :param cls: clusters
    :param verbose: more output
    :return:
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Writing clusters{color.ENDC}\n")

    out=open(outf + ".cls", 'w')
    out.write("cluster\tproteinID\n")
    ids = list(cls.keys())
    ids.sort()
    for i, j in enumerate(ids):
        for c in cls[j]:
            out.write(f"{i}\t{c}\n")

    out.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=' ')
    parser.add_argument('-b', help='blast input file', required=True)
    parser.add_argument('-o', help="output file base (we write .tsv, .cls, and .mat formats as appropriate)")
    parser.add_argument('-t', help='write tsv output', action='store_true')
    parser.add_argument('-m', help='write matrix output', action='store_true')
    parser.add_argument('-c', help='write clusters output', action='store_true')
    parser.add_argument('-x', help='maximum normalized bit score for clusters (default=1)', type=float, default=1)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    ss = self_bit_scores(args.b, args.v)
    pb = pairwise_bit_scores(args.b, ss, args.v)

    if args.t:
        write_pb(args.o, pb, args.v)
    if args.m:
        write_matrix(args.o, pb, args.v)
    if args.c:
        cl = precluster(pb, args.x, args.v)
        write_clusters(args.o, cl, args.v)
