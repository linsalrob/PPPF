"""
Find and download all the phage complete genomes from GenBank.

This is based in part on the snakemake genbank help:
    https://snakemake.readthedocs.io/en/stable/snakefiles/remote_files.html#genbank-ncbi-entrez

This doesn't include some other genomes identified by Andrew Millard, but
I add those separately later

I have tried a couple of versions of this (you can see them in the file
history on git), but settled on the eutils version. It adds a dependency
but is way cleaner and faster than either snakemakes NCBI handler
or BioPython

"""

import os
import sys
from datetime import date


configfile: 'process_phages.json'
GENOMEDIR = config['directories']['genomes']
USERID = config['userid']
PHAGE_DATABASE = config['phage_database']
CLUSTER_DATABASE = config['cluster_database']


# we don't include this as a rule because if the database
# does not exist, the initial load takes a long time
# and we want you to do it!

if not os.path.exists(PHAGE_DATABASE) or not os.path.exists(CLUSTER_DATABASE):
    sys.stderr.write(f"WARNING: {PHAGE_DATABASE} or {CLUSTER_DATABASE} does not exist\n")
    sys.stderr.write("""
If this is the first time you are running the code, please make the
database and populate it with genbank data. Alternatively, you
can download a preloaded version of the database from Rob's
website which will save you a day or two!

To create the database use:
        python3 ~/GitHubs/PPPF/scripts/create_databases.py -p phages.sql -c clusters.sql -v
You can continue from there and we'll add all the data
                     """)
    sys.exit(0)

# do we want verbose output? Set the verbose setting to true
VERBOSE = ""
if 'verbose' in config and config['verbose']:
    VERBOSE="-v"

phage_term = '"gbdiv_PHG"[prop] AND "complete"[Properties]'

todaysdate = date.today().strftime('%Y%m%d')



rule all:
    input:
        f"{todaysdate}.dbupdated",
        f"{todaysdate}.new_proteins.fasta"


rule eutils_phage_accessions:
    """
    Retrieve a tuple of [gi, accession] for all phages in GenBank
    """
    output:
        f"{todaysdate}.phage_accessions.txt"
    params:
        term = phage_term
    shell:
        "esearch -query '{params.term}' -db nuccore | efetch -format docsum | xtract -pattern DocumentSummary -element Id AccessionVersion > {output}"

rule new_genomes_only:
    """
    Find which genomes are new, and which are already in the database.
    Ignore those in the db
    """
    input:
        f"{todaysdate}.phage_accessions.txt"
    output:
        f"{todaysdate}.new_genomes.txt"
    shell:
        "python3 /home3/redwards/GitHubs/PPPF/scripts/phage_new_genomes.py -f {input} -p {PHAGE_DATABASE} -o {output} {VERBOSE}"


rule download_genomes:
    """
    Download the genome data
    """

    input:
        f"{todaysdate}.new_genomes.txt"
    output:
        os.path.join(GENOMEDIR, f"{todaysdate}.sequences.gb")
    shell:
        "python3 ~/GitHubs/PPPF/scripts/download_genbank_files.py -f {input} -o {output}"


rule load_database:
    """
    Load the genbank data into the database
    """
    input:
        os.path.join(GENOMEDIR, f"{todaysdate}.sequences.gb")
    output:
        f"{todaysdate}.dbupdated"
    shell:
        "python3 /home3/redwards/GitHubs/PPPF/scripts/load_databases.py -p {PHAGE_DATABASE} -f {input} -v > {output}"

rule find_new_proteins:
    """
    Find any proteins we have not yet added to clusters
    """
    input:
        semaphore_file = f"{todaysdate}.dbupdated"
    output:
        f"{todaysdate}.new_proteins.fasta"
    shell:
        """
        python3 ~/GitHubs/PPPF/scripts/proteins_not_in_clusters.py -p  {PHAGE_DATABASE} -c  {CLUSTER_DATABASE} -v > {output}
        """
