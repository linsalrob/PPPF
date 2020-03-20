# Database schema

We use `SQLite` for the databases, and these are the current schema that we have for each table.

These are deliberately designed to be lightweight at this development stage, and we do not try to represent all features in a genome.

We are more interested in getting the protein sequences organized into clusters!

**Notes:** 
- All tables names are singular (cluster, proteincluster, etc) and lower case.
- The md5sum is calculated using the Python `hashlib` library. The sequence is converted to `utf-8` typically like so:
    `seqmd5 = hashlib.md5(str(seq.seq).encode('utf-8')).hexdigest()`

## Genome table

The `genome` table describes the genome sequence.
This information generally comes from the GenBank or other source file.

Attribute | Value | Meaning
--- | --- | ---
genome_rowid | INTEGER PRIMARY KEY | The autoincremented ID. When inserting, set this to null (see note below)
identifier | TEXT | 
source_file | TEXT | the name (and path) of the file that we got this from.
accession | TEXT |
name | TEXT | the sample name (often same as identifier)
source | TEXT | is generally the common name
organism | TEXT | is generally the scientific name 
taxonomy | TEXT | the taxonomy string
collection_date | TEXT | when collected
country | TEXT | where collected
db_xref | TEXT | pipe-separated list of ids
host | TEXT | the bacterial host
isolation_source | TEXT | where it was isolated from
strain | TEXT | the specific strain
lab_host | TEXT | the lab host of this phage
sequence | TEXT | the genome sequence
sequence_md5 | TEXT | the md5 sum of the uppercase DNA genome sequence
length | INTEGER | length of the genome sequence

## Gene table

A `gene` is the DNA sequence that encodes a feature. It may or may not encode a protein (it could also encode some other feature).
This information generally comes from the GenBank or other source file.

Attribute | Value | Meaning
--- | --- | ---
gene_rowid | INTEGER PRIMARY KEY | The autoincremented ID.
accession | TEXT | The gene's accession number
contig | TEXT | The contig where the gene is found
start | INTEGER | The start position 
end | INTEGER | The end position
strand | INTEGER | The strand
dna_sequence | TEXT | The DNA sequence
dna_sequence_md | TEXT | the md5 sum of the uppercase DNA sequence
protein | INTEGER | The primary ID of the associated protein sequence
length | INTEGER | The length of the gene in `bp`
db_xref | TEXT | Any other IDs. A pipe-separated list of <code>db&#124;identifier`</code>

## Protein table

A `protein` is the protein sequence that is encoded by a protein encoding gene. 
This information generally comes from the GenBank or other source file.

Attribute | Value | Meaning
--- | --- | ---
protein_rowid | INTEGER PRIMARY KEY | The autoincremented ID.
protein_id | TEXT | this is the `protein_id` field from GenBank records
contig | TEXT
gene | INTEGER | The foreign key for the protein sequence
protein_sequence | TEXT | the protein sequence
length | INTEGER | the length of the translated sequence not including the stop codon
product | TEXT | the product encoded by the protein
db_xref | TEXT |
protein_sequence_md5  | TEXT | the md5sum of the uppercase protein sequence
EC_number | TEXT |
genename | TEXT |
locus_tag | TEXT |
note | TEXT |
ribosomal_slippage | TEXT |
transl_table | TEXT |



Product is often referred to as function.

## ClusterDefinition

The `clusterdefinition` table contains information about a specific class of clusters, how they were created and what the parameters were for the clustering.
Note that each cluster definition will describe hundreds of clusters

Attribute | Value | Meaning
--- | --- | ---
clusterdefinition_rowid | INTEGER PRIMARY KEY | The autoincremented ID.
name | TEXT | A short name (no spaces or special characters) for this cluster, suitable for use in a file name
description | TEXT | A human readable description of this cluster
command | TEXT | The command line invocation of the cluster


## Cluster

A `cluster` refers to a specific group of proteins that are somehow related to each other.

Attribute | Value | Meaning
--- | --- | ---
cluster_rowid | INTEGER PRIMARY KEY | The autoincremented ID.
uuid | TEXT | Universal unique ID for this cluster
clusterdefinition | INTEGER | Foreign key to ClusterDefinitions
members | TEXT | Comma-separated list of protein accessions for members in this cluster
exemplar | TEXT | The protein that exemplifies this cluster
longest_id | TEXT | The id of the longest protein sequence in this cluster
longest_len | INTEGER | The length of the longest protein sequence in this cluster
shortest_id | TEXT | The id of the shortest protein sequence in this cluster
shortest_len | INTEGER | The length of the shortest protein sequence in this cluster
average_size | REAL | The average size of the proteins in this cluster
number_of_members | INTEGER | The number of members in this cluster
functions | TEXT | A JSON format string of the functions and their counts (a dict object)
function | TEXT | The most likely (abundant) function of the proteins in this cluster.
number_of_functions | INTEGER | The number of (unique) functions in this cluster
only_hypothetical | INTEGER | Are all the functions in this cluster hypothetical


**Note:** Currently, `functions` is a `JSON` object that captures the name of the functions (products in a genbank file) and the count of those. The sum of function counts does not equal the number of members in the cluster, because there is a one protein sequence (md5sum) : many proteins relationship, and we count each protein individually. 

## ProteinCluster

The `proteincluster` table holds the connections between *proteins* and *clusters*. Neither protein nor cluster in this table needs to be unique (i.e. many:many)

Attribute | Value | Meaning
--- | --- | ---
proteincluster_rowid | INTEGER PRIMARY KEY | The autoincremented ID.
protein | INTEGER NOT NULL  | A protein accession. Foreign key to the protein table
cluster | INTEGER NOT NULL | A cluster UUID. Foreign key to the cluster table


### Notes:
- For the `primary key` we use the `id INTEGER PRIMARY KEY` format. This is automatically inserted if the field is left 
as null during the insert (which you should do). See the [SQLite documentation](https://www.sqlite.org/autoinc.html) for 
more information. These `PRIMARY KEYS` become the foreign keys e.g. in the `proteincluster` table.
