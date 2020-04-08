[![Edwards Lab](https://img.shields.io/badge/Bioinformatics-EdwardsLab-03A9F4)](https://edwards.sdsu.edu/research)

# PPPF

# Probabilistic Phage Protein Families

# What does it do?

We have a database of probabilistic phage protein families. You can use them to explore and annotate your data.

# Installation

You're relying on GitHub, so good luck. At the moment, if you are interested in working on this, you should contact
 Rob Edwards. He could sure use the help!
 
 # Getting started
 
 You can download a partially pre-populated database of phage genomes from [Robs website](https://edwards.sdsu.edu/phage/PPPF/phages.sql)
 
 Then, you can use snakemake to start making it better. Probably.
 
 You will need a [process_phages.json](snakefiles/process_phages.json) file, and then you can update the databases 
 with the latest phage genomes like this:
 
 ```bash
snakemake -s PPPF/snakefiles/download_phages.snakefile --configfile process_phages.json
```

if you are running on Edwards' local compute resources, you can use this command to run the download on the cluster. You may need to install some PERL dependencies for [eutils](https://www.ncbi.nlm.nih.gov/books/NBK25497/).

```bash
snakemake -s ~/GitHubs/PPPF/snakefiles/download_phages.snakefile --cluster 'qsub -cwd -o sge_download.out -e sge_download.err -V' -j 200 --latency-wait 60
```
 
 It will download a new set of accessions, and then check the database to see what needs to be added. 
 Note that currently we do not delete anything from the database.
 
 
