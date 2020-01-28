# Database schema

We use `SQLite` for the databases, and these are the current schema that we have for each table.

These are deliberately designed to be lightweight at this development stage, and we do not try to represent all features in a genome.

We are more interested in getting the protein sequences organized into clusters!

## Genome table

This table describes a genome sequence
This information generally comes from the GenBank or other source file.

--- | ---
Attribute | Value
--- | ---
identifier | TEXT
source_file | TEXT
accession | TEXT
length | INTEGER
name | TEXT
sequence | TEXT

## Gene table

A gene is the DNA sequence that encodes a feature. It may or may not encode a protein (it could also encode some other feature).
This information generally comes from the GenBank or other source file.

--- | ---
Attribute | Value
--- | ---
accession | TEXT
contig | TEXT
start | INTEGER
end | INTEGER
strand | INTEGER
length | INTEGER
dna_sequence | TEXT
other_ids | TEXT

## Protein table

A protein is the protein sequence that is encoded by a protein encoding gene. 
This information generally comes from the GenBank or other source file.

--- | ---
Attribute | Value
--- | ---
accession | TEXT
contig | TEXT
protein_sequence | TEXT
length | INTEGER
product | TEXT
other_ids | TEXT

Product is often referred to as function.

## ClusterDefinitions

The ClusterDefinitions table contains information about a specific class of clusters, how they were created and what the parameters were for the clustering.
Note that each cluster definition will describe hundreds of clusters

--- | --- | ---
Attribute | Value | Meaning
--- | --- | ---
uuid | TEXT | Universal unique ID for this cluster definition
name | TEXT | A short name (no spaces or special characters) for this cluster, suitable for use in a file name
description | TEXT | A human readable description of this cluster
command | TEXT | The command line invocation of the cluster


## Cluster

A cluster refers to a specific group of proteins that are somehow related to each other.

--- | --- | ---
Attribute | Value | Meaning
--- | --- | ---
uuid | TEXT | Universal unique ID for this cluster
definition | TEXT | Foreign key to ClusterDefinitions
members | TEXT | Comma-separated list of protein accessions (foreign key) for members in this cluster
function | TEXT | The most likely (abundant) function of the proteins in this cluster.
altfunctions | TEXT | json format text representing all the functions encoded in this cluster. The format is "function" : "proportion of proteins"

## ProteinClusters

The connection between *proteins* and *clusters*. Neither protein nor cluster in this table needs to be unique (i.e. many:many)

--- | --- | ---
Attribute | Value | Meaning
--- | --- | ---
protein | TEXT | A protein accession. Foreign key to the protein table
cluster | TEXT | A cluster UUID. Foreign key to the cluster table
