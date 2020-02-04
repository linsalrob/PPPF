# Database schema

We use `SQLite` for the databases, and these are the current schema that we have for each table.

These are deliberately designed to be lightweight at this development stage, and we do not try to represent all features in a genome.

We are more interested in getting the protein sequences organized into clusters!

**Note:** All tables names are singular (cluster, proteincluster, etc) and lower case.

## Genome table

The `genome` table describes the genome sequence.
This information generally comes from the GenBank or other source file.

Attribute | Value | Meaning
--- | --- | ---
genome_id | INTEGER PRIMARY KEY | The autoincremented ID. When inserting, set this to null (see note below)
identifier | TEXT
source_file | TEXT
accession | TEXT
length | INTEGER
name | TEXT
sequence | TEXT
sequence_md5 | TEXT | the md5 sum of the uppercase DNA genome sequence

## Gene table

A `gene` is the DNA sequence that encodes a feature. It may or may not encode a protein (it could also encode some other feature).
This information generally comes from the GenBank or other source file.

Attribute | Value | Meaning
--- | --- | ---
gene_id | INTEGER PRIMARY KEY | The autoincremented ID.
accession | TEXT | The gene's accession number
contig | TEXT | The contig where the gene is found
start | INTEGER | The start position 
end | INTEGER | The end position
strand | INTEGER | The strand
length | INTEGER | The length of the gene in `bp`
dna_sequence | TEXT | The DNA sequence
protein | INTEGER | The primary ID of the associated protein sequence
other_ids | TEXT | Any other IDs. A comma-separated list of <code>db&#124;identifier`</code>
dna_sequence_md | TEXT | the md5 sum of the uppercase DNA sequence
## Protein table

A `protein` is the protein sequence that is encoded by a protein encoding gene. 
This information generally comes from the GenBank or other source file.

Attribute | Value | Meaning
--- | --- | ---
protein_id | INTEGER PRIMARY KEY | The autoincremented ID.
accession | TEXT
contig | TEXT
gene | INTEGER | The foreign key for the protein sequence
protein_sequence | TEXT
length | INTEGER
product | TEXT
other_ids | TEXT
protein_sequence_md5  | TEXT | the md5sum of the uppercase protein sequence

Product is often referred to as function.

## ClusterDefinition

The `clusterdefinition` table contains information about a specific class of clusters, how they were created and what the parameters were for the clustering.
Note that each cluster definition will describe hundreds of clusters

Attribute | Value | Meaning
--- | --- | ---
clusterdefinition_id | INTEGER PRIMARY KEY | The autoincremented ID.
uuid | TEXT | Universal unique ID for this cluster definition
name | TEXT | A short name (no spaces or special characters) for this cluster, suitable for use in a file name
description | TEXT | A human readable description of this cluster
command | TEXT | The command line invocation of the cluster


## Cluster

A `cluster` refers to a specific group of proteins that are somehow related to each other.

Attribute | Value | Meaning
--- | --- | ---
cluster_id | INTEGER PRIMARY KEY | The autoincremented ID.
uuid | TEXT | Universal unique ID for this cluster
definition | TEXT | Foreign key to ClusterDefinitions
members | TEXT | Comma-separated list of protein accessions (foreign key) for members in this cluster
function | TEXT | The most likely (abundant) function of the proteins in this cluster.
altfunctions | TEXT | json format text representing all the functions encoded in this cluster. The format is "function" : "proportion of proteins"

## ProteinCluster

The `proteincluster` table holds the connections between *proteins* and *clusters*. Neither protein nor cluster in this table needs to be unique (i.e. many:many)

Attribute | Value | Meaning
--- | --- | ---
proteincluster_id | INTEGER PRIMARY KEY | The autoincremented ID.
protein | INTEGER NOT NULL  | A protein accession. Foreign key to the protein table
cluster | INTEGER NOT NULL | A cluster UUID. Foreign key to the cluster table


### Notes:
- For the `primary key` we use the `id INTEGER PRIMARY KEY` format. This is automatically inserted if the field is left 
as null during the insert (which you should do). See the [SQLite documentation](https://www.sqlite.org/autoinc.html) for 
more information. These `PRIMARY KEYS` become the foreign keys e.g. in the `proteincluster` table.