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
            FOREIGN KEY(protein) REFERENCES protein(protein_rowid)
            FOREIGN KEY(protein) REFERENCES cluster(cluster_id)

"""

import sys
import json

from pppf_databases import connect_to_db, disconnect
from .cluster import Cluster
from pppf_accessories import color

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


def add_functions_to_clusters(cls, phageconn, verbose=False):
    """
    Add the protein functions to the clusters.
    :param cls: The list of clusters
    :param phageconn: The phage database connection
    :param verbose: More output
    :return: A modified list of cluster objects that includes the functions
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Adding functions to clusters{color.ENDC}\n")

    cur = phageconn.cursor()
    
    protein_info = {}

    cn = len(cls)
    for cc, clu in enumerate(cls):
        """
        if verbose:
            sys.stderr.write(f"{color.PINK}\tCluster {cc} of {cn}: {clu.id}{color.ENDC}\n")
        """

        plens = []

        # note we retrieve the information for the exemplar first and
        # then if it is the longest/shortest it remains that way
        ex = cur.execute("select product, length from protein where protein_md5sum=?", [clu.exemplar])
        tple = ex.fetchone()
        if not tple:
            sys.stderr.write(f"{color.RED}ERROR retrieving information about cluster exemplar {clu.exemplar} from the database.\nCan't continue{color.ENDC}\n")
            sys.exit(-1)
        (prdct, seqlen) = tple
        shortestid = longestid = clu.exemplar
        shortestlen = longestlen = seqlen

        for c in clu.members:
            ex = cur.execute("select product, length, protein_rowid from protein where protein_md5sum=?", [c])
            for tple in ex.fetchall():
                if not tple:
                    sys.stderr.write(f"{color.RED}ERROR retrieving information about {c} from the database{color.ENDC}\n")
                    continue
                (prdct, seqlen, prid) = tple
                # we only save one row id.
                # this should probably refer to the protein_sequence table
                # now we are using md5sums
                protein_info[c] = prid
                if seqlen > longestlen:
                    longestid = c
                    longestlen = seqlen
                if seqlen < shortestlen:
                    shortestid = c
                    shortestlen = seqlen
                plens.append(seqlen)
                clu.functions[prdct] = clu.functions.get(prdct, 0) + 1
        clu.longest_id = longestid
        clu.longest_len = longestlen
        clu.shortest_id = shortestid
        clu.shortest_len = shortestlen
        clu.average_size = sum(plens)/len(plens)
        clu.number_of_functions = len(clu.functions)
        allfn = sorted(clu.functions.items(), key=lambda item: item[1], reverse=True)
        assert isinstance(clu, Cluster)
        clu.function = allfn[0][0]
        clu.is_hypothetical()

    return (cls, protein_info)


def insert_cluster_metadata(clconn, name, desc, cli, verbose=False):
    """
    Insert the cluster metadata information in the SQL table and return its rowid.
    This is the information that describes how the clusters were made.
    :param clconn: the database connection
    :param name: the name of the clustering approach
    :param desc: a human readable description of the clustering
    :param cli: the command line command used for the clustering
    :param verbose: more output
    :return: the clusterdefinition_rowid for this metadata
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Adding the metadata{color.ENDC}\n")

    clcur = clconn.cursor()
    clcur.execute("INSERT INTO clusterdefinition(name, description, command) values (?,?,?)",
                [name, desc, cli])
    cd_rowid = clcur.lastrowid
    clconn.commit()
    return cd_rowid


def insert_into_database(clusters, clconn, phageconn, metadata_id, protein_info, verbose=False):
    """
    Insert information into the database
    :param clusters: The array of clusters with their functions
    :param clconn: the clusters database connection
    :param phageconn: the phage database connection
    :param metadata_id: the rowid of the cluster definition table
    :param protein_info: a dict of [protein id: protein_rowid]
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

    clcur = clconn.cursor()
    phcur = phageconn.cursor()

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
        clcur.execute(sql, data)
        cluster_id = clcur.lastrowid
        for m in c.members:
            if m not in protein_info:
                exc = phcur.execute("select protein_sequence_rowid from protein_sequence where protein_md5sum = ?", [m])
                tple = exc.fetchone()
                if not tple[0]:
                    sys.stderr.write(f"{color.RED}No protein info for {m}{color.ENDC}\n")
                    continue
                protein_info[m] = tple[0]
            clcur.execute("INSERT INTO proteincluster (protein, cluster) VALUES (?,?)", [protein_info[m], cluster_id])
            clcur.execute("INSERT INTO md5cluster (protein_md5sum, cluster) VALUES (?,?)", [m, cluster_id])
            clconn.commit()


if __name__ == '__main__':

    sys.stderr.write(f"{color.RED}FATAL: Please use scripts/load_clusters.py to load the clusters\n{color.ENDC}")
