"""
Load the cluster information into the databases. This could also be in the databases folder :)

Our cluster tables have these structures:

        CREATE TABLE clusterdefinition (
            clusterdefinition_rowid INTEGER PRIMARY KEY,
            uuid TEXT,
            name TEXT,
            description TEXT,
            command TEXT


        CREATE TABLE cluster (
            cluster_rowid INTEGER PRIMARY KEY,
            uuid TEXT,
            definition TEXT,
            members TEXT,
            function TEXT,
            altfunction TEXT


        CREATE TABLE proteincluster (
            proteincluster_rowid INTEGER PRIMARY KEY,
            protein INTEGER NOT NULL,
            cluster INTEGER NOT NULL,
            FOREIGN KEY(protein) REFERENCES protein(protein_id)
            FOREIGN KEY(protein) REFERENCES cluster(cluster_id)

"""

import sys
import argparse
import json

from pppf_databases import connect_to_db, disconnect
from pppf_lib import color
from .cluster import Cluster


def read_mmseqs_clusters(clf, verbose=False):
    """
    Read all the clusters at once and return an array of clusters.
    :param clf: mmseqs cluster file that has [id1, id2] where id1 is the representative of the cluster
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
        cls.append(Cluster(None, lastclid, thiscls))
        cc += 1

    if verbose:
        sys.stderr.write(f"{color.BLUE}There were {cc} clusters{color.ENDC}\n")
    return cls


def add_functions_to_clusters(cls, conn, verbose=False):
    """
    Add the protein functions to the clusters.
    :param cls: The list of clusters
    :param conn: The database connection
    :param verbose: More output
    :return: A modified list of cluster objects that includes the functions
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Adding functions to clusters{color.ENDC}\n")

    cur = conn.cursor()

    for clu in cls:
        if verbose:
            sys.stderr.write(f"{color.PINK}\tCluster {clu.id}{color.ENDC}\n")

        plens = []
        fncount = {}

        # note we retrieve the information for the exemplar first and
        # then if it is the longest/shortest it remains that way
        ex = cur.execute("select product, protein_sequence from protein where protein_id=?", [clu.exemplar])
        tple = ex.fetchone()
        if not tple:
            sys.stderr.write(f"{color.RED}ERROR retrieving information about cluster exemplar {clu.exemplar} from the database.\nCan't continue{color.ENDC}\n")
            sys.exit(-1)
        (prdct, seq) = tple
        shortestid = longestid = clu.exemplar
        shortestlen = longestlen = len(seq)

        for c in clu.members:
            ex = cur.execute("select product, protein_sequence from protein where protein_id=?", [c])
            tple = ex.fetchone()
            if not tple:
                sys.stderr.write(f"{color.RED}ERROR retrieving information about {c} from the database{color.ENDC}\n")
                continue
            (prdct, seq) = tple
            if len(seq) > longestlen:
                longestid = c
                longestlen = len(seq)
            if len(seq) < shortestlen:
                shortestid = c
                shortestlen = len(seq)
            plens.append(len(seq))
            fncount[prdct] = fncount.get(prdct, 0) + 1
        clu.longest_id = longestid
        clu.longest_len = longestlen
        clu.shortest_id = shortestid
        clu.shortest_len = shortestlen
        clu.average_size = sum(plens)/len(plens)
        clu.functions = fncount
        clu.number_of_functions = len(clu.functions)
        allfn = sorted(fncount.items(), key=lambda item: item[1], reverse=True)
        assert isinstance(clu, Cluster)
        clu.function = allfn[0][0]
        clu.is_hypothetical()

    return cls


def insert_cluster_metadata(conn, name, desc, cli, verbose=False):
    """
    Insert the cluster metadata information in the SQL table and return its rowid.
    This is the information that describes how the clusters were made.
    :param conn: the database connection
    :param name: the name of the clustering approach
    :param desc: a human readable description of the clustering
    :param cli: the command line command used for the clustering
    :param verbose: more output
    :return: the clusterdefinition_rowid for this metadata
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Adding the metadata{color.ENDC}\n")

    cur = conn.cursor()
    cur.execute("INSERT INTO clusterdefinition(name, description, command) values (?,?,?)",
                [name, desc, cli])
    cd_rowid = cur.lastrowid
    conn.commit()
    return cd_rowid


def insert_into_database(clusters, conn, metadata_id, verbose=False):
    """
    Insert information into the database
    :param clusters: The array of clusters with their functions
    :param conn: the Database connection
    :param metadata_id: the rowid of the cluster definition table
    :param verbose: more output
    :return:
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Inserting into the database{color.ENDC}\n")

    # check the functions have been added
    c: Cluster = clusters[0]
    if not c.shortest_id:
        sys.stderr.write(f"{color.RED}FATAL: There is no shortest id for the first cluster. Was the seq info added?{color.ENDC}\n")
        sys.exit(-1)

    cur = conn.cursor()

    for c in clusters:
        sql = """
            INSERT INTO cluster (uuid, clusterdefinition, members, exemplar, longest_id, longest_len, shortest_id, 
            shortest_len, average_size, number_of_members, functions, function, 
            number_of_functions, only_hypothetical)
            VALUES  (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """
        data = [
            c.id, metadata_id, ",".join(c.members), c.exemplar, c.longest_id, c.longest_len, c.shortest_id,
            c.shortest_len, c.average_size, c.number_of_members, json.dumps(c.functions), c.function,
            c.number_of_functions, c.only_hypothetical
        ]
        cur.execute(sql, data)
        cluster_id = cur.lastrowid
        for m in c.members:
            ex = cur.execute("select protein_rowid from protein where protein_id = ?", [m])
            tple = ex.fetchone()
            if not tple:
                sys.stderr.write(f"{color.PINK}Found a protein {m} that does not appear in the protein table{color.ENDC}\n")
                continue
            cur.execute("INSERT INTO proteincluster (protein, cluster) VALUES (?,?)", [tple[0], cluster_id])
    conn.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load the cluster information into the databases')
    parser.add_argument('-d', help='SQL database', required=True)
    parser.add_argument('-t', help='Cluster tsv file', required=True)
    parser.add_argument('-n', help='Cluster name (short text)', required=True)
    parser.add_argument('-s', help='Cluster description (human readable text)', required=True)
    parser.add_argument('-c', help='Cluster command line (bash)', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    conn = connect_to_db(args.d, args.v)
    clusters = read_mmseqs_clusters(args.t, args.v)
    clusters = add_functions_to_clusters(clusters, conn, args.v)
    metadata_id = insert_cluster_metadata(conn, args.n, args.s, args.c, args.v)
    insert_into_database(clusters, conn, metadata_id, args.v)
    disconnect(conn, args.v)
