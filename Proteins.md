# Feature Tables

Here we describe the structure of the feature tables that we use in PPPF

An annotation file is converted into a table for downstream analysis.


| Column | Contents |
| --- | --- |
| 0 | Genome identifier |
| 1 | Genome source file name |
| 2 | Genome accession (identifier.version) |
| 3 |  Genome length |
| 4 | Genome name |
| 5 | Protein accession (identifier.version) |
| 6 | Start location of the feature (bp) |
| 7 | End location of the feature (bp)
| 8 | Strand of the feature (-1 \| 0 \| 1) |
| 9 | Amino acid sequence of the feature if appropriate | 
| 10 | DNA sequence of the feature |
| 11 | feature product name |
| 12 | other feature identifiers (joined with `;`)|

Some of this data is repetitive (e.g. columns 0-4).

# Annotations

We use a simple JSON data structure or SQLite database to store the functional annotations as a hash.

# Cluster data

We store the cluster data in simple sparse matrices.

