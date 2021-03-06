"""
Create protein families from our SQL database
"""



import os
import sys
import tempfile
from datetime import date


configfile: 'process_phages.json'
GENOMEDIR = config['directories']['genomes']
USERID = config['userid']
PHAGE_DATABASE = config['phage_database']
CLUSTER_DATABASE = config['cluster_database']
CLUSTERDIR = config['directories']['clusters']

# we define this as a variable as we do not want it cleaned up
TMPDIR = "tmp"
if not os.path.exists(TMPDIR):
    os.mkdir(TMPDIR)


if not os.path.exists(PHAGE_DATABASE):
    sys.stderr.write(f"FATAL: {PHAGE_DATABASE} not found.\n")
    sys.stderr.write(f"Please see snakefiles/download_phages.snakefile")
    sys.stderr.write("To make and install the databases\n")
    sys.exit(0)

if not os.path.exists(CLUSTER_DATABASE):
    sys.stderr.write(f"FATAL: {CLUSTER_DATABASE} not found.\n")
    sys.stderr.write(f"Please see snakefiles/download_phages.snakefile")
    sys.stderr.write("To make and install the databases\n")
    sys.exit(0)



# do we want verbose output? Set the verbose setting to true
VERBOSE = ""
if 'verbose' in config and config['verbose']:
    VERBOSE="-v"



todaysdate = date.today().strftime('%Y%m%d')



rule all:
    input:
        expand(
            "clusters.type{tps}.id{seqid}.dbload.sh",
            tps   = config['mmseqs']['types'], 
            seqid = config['mmseqs']['seqids']
        ),
        "load_databases.sh"



rule dump_all_protein_sequences:
    """
    Dump the protein sequences in fasta format
    """
    output:
        f"{todaysdate}.proteins.fasta"
    shell:
        """
        sqlite3 {PHAGE_DATABASE} "select protein_md5sum, protein_sequence from protein_sequence" \
                | sed 's/^/>/; s/|/\\n/' > {output}
        """

rule format_mmseqs_db:
    input:
        f"{todaysdate}.proteins.fasta"
    output:
        db = f"{todaysdate}.proteins.db",
        db_h = f"{todaysdate}.proteins.db_h",
        db_hi = f"{todaysdate}.proteins.db_h.index",
        db_lookup = f"{todaysdate}.proteins.db.lookup",
        db_dbtype = f"{todaysdate}.proteins.db.dbtype",
        db_hdbtype = f"{todaysdate}.proteins.db_h.dbtype",
        db_idx = f"{todaysdate}.proteins.db.index",
        db_source = f"{todaysdate}.proteins.db.source"
    shell:
        "mmseqs createdb {input} {output.db}"

rule cluster_proteins:
    """
    Build mmseqs clusters of those protein sequences.

    Two things of note: first, we specify one thread, which takes (obvs)
    longer, but we end up with a single output file per cluster.

    Second, we use $(mktemp -d -p {TMPDIR}) to create a temporary
    directory in the {TMPDIR} directory. Otherwise, mmseqs
    has a habit of stepping on itself.
    """
    input:
        db = f"{todaysdate}.proteins.db",
    params:
        seqid = "{seqid}",
        tp = "{tps}",
        cl = os.path.join(CLUSTERDIR, "clusters.type{tps}.id{seqid}")
    output:
        idx = os.path.join(CLUSTERDIR, "clusters.type{tps}.id{seqid}.index")
    shell:
        "mmseqs cluster --threads 1 --cov-mode {params.tp} --min-seq-id {params.seqid} {input.db} {params.cl} $(mktemp -d -p {TMPDIR})"

rule create_tsv:
    """
    Create tsv files from the clusters
    """
    input:
        db = f"{todaysdate}.proteins.db",
        idx = os.path.join(CLUSTERDIR, "clusters.type{tps}.id{seqid}.index")
    output:
        tsv = os.path.join(CLUSTERDIR, "clusters.type{tps}.id{seqid}.tsv")
    params:
        cl = os.path.join(CLUSTERDIR, "clusters.type{tps}.id{seqid}")
    shell:
        "mmseqs createtsv {input.db} {input.db} {params.cl} {output.tsv}"

rule load_database:
    """
    Put all the data in our database.
    Note that currently we make a shell script for each of these, because we need to run them serially since
    the database has a lock so concurrent threads are blocked
    """
    input:
        tsv = os.path.join(CLUSTERDIR, "clusters.type{tps}.id{seqid}.tsv")
    params:
        summ = 'mmseqs clustered type {tps} at {seqid} fraction homology',
        name = 'mmseqs {tps}--{seqid}',
        odir = os.path.join(CLUSTERDIR, "clusters.type{tps}.id{seqid}"),
        cli  = 'mmseqs cluster --threads 1 --cov-mode {tps} --min-seq-id {seqid} ' + f'{todaysdate}.proteins.db '
    output:
        out = "clusters.type{tps}.id{seqid}.dbload.sh"
    shell:
        """
        echo "python3 /home3/redwards/GitHubs/PPPF/scripts/load_clusters.py -p {PHAGE_DATABASE} -c {CLUSTER_DATABASE} -t {input.tsv} -n '{params.name}' -d '{params.summ}' -c '{params.cli} {params.odir} tempdir' {VERBOSE}" > {output.out}
        """
rule concat_loads:
    """
    Combine all the database loads into a file
    """
    input:
        "clusters.type{tps}.id{seqid}.dbload.sh"
    output:
        "load_databases.sh"
    shell:
        "cat {input} > {output}"