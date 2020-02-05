"""
Load the sequences from GenBank.

This is the correct way to do this!
"""

import os
import sys
import argparse

from roblib import bcolors
import hashlib
from Bio import SeqIO

def load_file(gbkf, conn, verbose=True):
    """
    Load the sequences from a genbank file
    :param gbkf: genbank file
    :param conn: database connection
    :param verbose: more output
    :return:
    """

    for seq in SeqIO.parse(open(gbkf, 'r'), "genbank"):
        # the information for the genome record
        seqmd5 = hashlib.md5(seq.seq.encode('utf-8')).hexdigest()


        # source metadata
        srcmtd = {
            'collection_date':"",
            'country':"",
            'db_xref':"",
            'isolation_source': "",
            'host':"",
            'strain': "",
            'lab_host': ""
        }
        # protein (CDS) metadata
        prtmtd = {
            'EC_number': "",
            'db_xref' : "",
            'gene' : "",
            'locus_tag' : "",
            'note' :"",
            'product':"",
            'protein_id':"",
            'ribosomal_slippage':"",
            'transl_table':"",
            'translation':""
        }
        # tRNA metadata
        trnmtd: {
            'codon_recognized' : "",
            'db_xref' : "",
            'gene' : "",
            'locus_tag' : "",
            'note' : "",
            'product': "",
            'is_tmRNA' : "",
        }





        # the information for the genes
        for feat in seq.features:
            if feat.type == 'source':
                for c in srcmtd.keys():
                    if c in feat.qualifiers:
                        srcmtd[c] = feat.qualifiers[c][0]
                    if 'db_xref' in feat.qualifiers:
                        # we handle this separately as we want them all
                        srcmtd['db_xref'] = "|".join(feat.qualifiers['db_xref'])
            if feat.type == 'CDS':
                (start, stop, strand) = (feat.location.start.position, feat.location.end.position, feat.strand)
                for p in prtmtd:
                    if p in feat.qualifiers:
                        prtmtd[p] = "|".join(feat.qualifiers[p])
                prtmd5 = hashlib.md5(prtmtd['translation'].encode('utf-8')).hexdigest()
                sql = """
                    INSERT INTO protein(protein_id, contig, product, db_xref, protein_sequence, protein_sequence_md5, 
                    length, EC_number, genename, locus_tag, note, ribosomal_slippage, transl_table) values 
                    (?,?,?,??,?,?,?,?,?,?,?,?,?,?)                  
                """
                conn.execute(sql, [
                    prtmtd['protein_id'], seq.name, prtmtd['product'], prtmtd['db_xref'], prtmtd['translation'], prtmd5,
                    len(prtmtd['translation']), prtmtd['EC_number'], prtmtd['gene'], prtmtd['locus_tag'], prtmtd['note'],
                    prtmtd['ribosomal_slippage'], prtmtd['transl_table']
                ])

                


                conn.commit()




        sql = """
                        INSERT INTO genome(identifier, source_file, accession,  name, source, organism, description, taxonomy, 
                            collection_date, country, db_xref, host, isolation_source, strain, lab_host, sequence, sequence_md5, length)
                        values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """

        conn.execute(sql, [seq.id, gbkf, seq.annotations['accessions'][0], seq.name, seq.annotations['source'],
                     seq.annotations['organism'], seq.description, seq.annotations['taxonomy'], srcmtd['collection_date'],
                     srcmtd['country'], srcmtd['db_xref'], srcmtd['host'], srcmtd['isolation_source'], srcmtd['strain'], srcmtd['lab_host'],
                     seq.seq, seqmd5, len(seq)])
        conn.commit()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', help='', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()
