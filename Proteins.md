# Phage Protein Features

We load all of the phage data into SQLite databases. Those databases are defined using `define_databases.py`. 

Data an be loaded directly from a GenBank file. There are a few conversions that we use:

1. Proteins are stored using the md5sum of the uppercase protein sequence as the ID. When a new protein is added, we don't add it if we already have it in the database. We add a record pointing to that sequence.
2. Product names (i.e. gene functions) are converted to sentence case: the first letter is capitalized, but all others are not.
