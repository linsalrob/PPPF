"""
Find and download all the phage complete genomes from GenBank.

This is based in part on the snakemake genbank help:
    https://snakemake.readthedocs.io/en/stable/snakefiles/remote_files.html#genbank-ncbi-entrez

This doesn't include some other genomes identified by Andrew Millard, but
I add those separately later

Note that I originally wrote this using the snakemake remote handler,
but that is very buggy and slow, and so I wrapped my own
using BioPython.

"""

from os.path import join
from datetime import date


configfile: 'process_phages.json'
GENOMEDIR = config['directories']['genomes']
USERID = config['userid']
DATABASE = config['database']

phage_term = '"gbdiv_PHG"[prop] AND "complete"[Properties]'

todaysdate = date.today().strftime('%Y%m%d')


def find_genbank_files(wildcards):
    GBKS, = glob_wildcards(join(GENOMEDIR, f'{todaysdate}.files', '{gbk}.gbk')),
    g = expand(join(GENOMEDIR, f"{todaysdate}.files", "{gbk}.gbk"), gbk=GBKS)
    return g


rule all:
    input:
        f"{todaysdate}.phage_accessions.txt"


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

rule biopython_search_accessions:
    """
    Create a list of all the accessions to download.

    This rule is deprecated in favor of the eutils approach.
    Two reasons:
        i.  This rule only downloads the Gi which is (a) deprecated and (b) not a part of the genbank record
        ii. This was breaking somehow
    """
    output:
        f"{todaysdate}.biopython.phage_accessions.txt"
    shell:
        "python ~/GitHubs/PPPF/scripts/search_genbank.py -t '{phage_term}' -o {output}"

rule download_genomes:
    """
    Download the genome data
    """

    input:
        f"{todaysdate}.phage_accessions.txt"
    output:
        join(GENOMEDIR, f"{todaysdate}.sequences.gb")
    shell:
        "python3 ~/GitHubs/PPPF/scripts/download_genbank_files.py -f {input} -o {output}"

rule split_genomes:
    """
    Separate the genbank files into multiple files
    """
    input:
        join(GENOMEDIR, f"{todaysdate}.sequences.gb")
    output:
        directory(join(GENOMEDIR, f"{todaysdate}.files"))
    shell:
        "python3 ~/bin/separate_multigenbank.py -f {input} -d {output}"


rule create_databases:
    """
    Create the SQL database and load the sequence data
    """
    
    input:
        join(GENOMEDIR, f"{todaysdate}.files")
    params:
        find_genbank_files
    output:
        f"{todaysdate}.sql"
    shell:
        "python3 ~/GitHubs/PPPF/scripts/create_databases.py -f {params} -d {output} -v"
