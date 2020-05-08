[![Edwards Lab](https://img.shields.io/badge/Bioinformatics-EdwardsLab-03A9F4)](https://edwards.sdsu.edu/research)

# PPPF
# Probabilistic Phage Protein Families

## Author

[Rob Edwards](https://twitter.com/linsalrob)


## Synopsis

We are exploring different ways of annotating phage proteins (because it never gets old), and this is a  database of complete phage genomes and their annotations.

It also includes some phage protein clustering and tools associated with those clusters.

At the moment this is very much a _pre-alpha_ project. We are defining the tables and relations, building the code base to access those tables, and trying to explore what we should do next.

However, we have made all our data, and the code to recreate it, available for everyone in case it is of use to anyone. 

## Installation

### PIP installation

```pythonstub
pip install pppf
```

### Getting started
 
The [download_databases](python scripts/download_databases.py) script will download the two databases `phages.sql` [2.6 GB] and `clusters.sql` [1.8 GB] to the default location (currently `PPPF/data/databases/`) or to a location of your choosing. 

Most of the code in [scripts](scripts/) requires that you provide a `phage` or `clusters` database as a command line option, but we are implementing code in `pppfdb` that will use the default location. If you use a different location, you may need to change the location in that code.
 
 
### Building from scratch
 
If you want to build the databases from scratch, you can do so using `snakemake` and the [snakefiles](snakefiles/) that we provide.
 
 Then, you can use snakemake to start making it better. Probably.
 
 You will need a [process_phages.json](snakefiles/process_phages.json) file, and then you can update the databases 
 with the latest phage genomes like this:
 
 
```bash
snakemake -s PPPF/snakefiles/download_phages.snakefile --configfile process_phages.json
```


if you are running on Edwards' local compute resources, you can use this command to run the download on the cluster. 

```bash
snakemake -s ~/GitHubs/PPPF/snakefiles/download_phages.snakefile --cluster 'qsub -cwd -o sge_download.out -e sge_download.err -V' -j 200 --latency-wait 60
```
 
 It will download a new set of accessions, and then check the database to see what needs to be added. 
 Note that currently we do not delete anything from the database.
 
## Using PPPF

The basic structure is that each of the directories is a library, and the [scripts](scripts/) directory contains scripts that use those libraries. 

Take a look at the [database schema](Schema.md) for a more detailed discussion of the schema we designed.


## Information

### License

PPPF is released under the [MIT License](LICENSE)

### Issues

Please use the [issue tracker](https://github.com/linsalrob/PPPF/issues) for any bugs, enhancements, suggestions, or comments
