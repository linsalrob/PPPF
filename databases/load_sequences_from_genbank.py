"""
Load the sequences from GenBank.

This is the correct way to do this!
"""

import sys
import argparse

from formatting import color
import database_handles

import hashlib
from Bio import SeqIO


def load_genbank_file(gbkf, conn, verbose=True):
    """
    Load the sequences from a genbank file
    :param gbkf: genbank file
    :param conn: database connection
    :param verbose: more output
    :return:
    """

    c = conn.cursor()

    for seq in SeqIO.parse(open(gbkf, 'r'), "genbank"):

        # source metadata
        srcmtd = {
            'collection_date': "",
            'country': "",
            'db_xref': "",
            'isolation_source': "",
            'host': "",
            'strain': "",
            'lab_host': ""
        }
        # protein (CDS) metadata
        prtmtd = {
            'EC_number': "",
            'db_xref': "",
            'gene': "",
            'locus_tag': "",
            'note': "",
            'product': "",
            'protein_id': "",
            'ribosomal_slippage': "",
            'transl_table': "",
            'translation': ""
        }
        # tRNA metadata
        trnmtd = {
            'codon_recognized': "",
            'db_xref': "",
            'gene': "",
            'locus_tag': "",
            'note': "",
            'product': "",
            'is_tmRNA': False,
        }

        # the information for the genes
        for feat in seq.features:
            if verbose:
                sys.stderr.write(f"{color.BLUE}Parsing a {feat.type}{color.ENDC}\n")
            if feat.type == 'source':
                for s in srcmtd.keys():
                    if s in feat.qualifiers:
                        srcmtd[s] = feat.qualifiers[s][0]
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
                    (?,?,?,?,?,?,?,?,?,?,?,?,?)                  
                """
                c.execute(sql, [
                    prtmtd['protein_id'], seq.name, prtmtd['product'], prtmtd['db_xref'], prtmtd['translation'],
                    prtmd5, len(prtmtd['translation']), prtmtd['EC_number'], prtmtd['gene'], prtmtd['locus_tag'],
                    prtmtd['note'], prtmtd['ribosomal_slippage'], prtmtd['transl_table']
                ])

                proteinrow = c.lastrowid
                dnaseq = str(feat.extract(seq).seq)
                dnamd5 = hashlib.md5(dnaseq.encode('utf-8')).hexdigest()
                sql = """
                    INSERT INTO gene(accession, contig, start, end, strand, dna_sequence, dna_sequence_md, protein, length, db_xref)
                    values (?,?,?,?,?,?,?,?,?,?)
                """

                c.execute(sql, [
                    prtmtd['locus_tag'], seq.name, start, stop, strand, dnaseq, dnamd5, proteinrow, len(dnaseq), prtmtd['db_xref']
                ])

                dnarow = c.lastrowid

                c.execute("UPDATE protein set gene=? where rowid = ?", (dnarow, proteinrow))

                conn.commit()

            if feat.type == 'tRNA' or feat.type == 'tmRNA':
                (start, stop, strand) = (feat.location.start.position, feat.location.end.position, feat.strand)
                for t in trnmtd:
                    if t in feat.qualifiers:
                        trnmtd[t] = "|".join(feat.qualifiers[t])
                if feat.type == 'tmRNA':
                    trnmtd['is_tmRNA'] = True
                dnaseq = str(feat.extract(seq).seq)
                dnamd5 = hashlib.md5(dnaseq.encode('utf-8')).hexdigest()
                sql = """
                    INSERT INTO trna(accession, contig, start, end, strand, dna_sequence, dna_sequence_md5, 
                    codon_recognized, db_xref, gene, note, product, is_tmRNA) values (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """

                c.execute(sql, [
                    trnmtd['locus_tag'], seq.name, start, stop, strand, dnaseq, dnamd5, trnmtd['codon_recognized'],
                    trnmtd['db_xref'], trnmtd['gene'], trnmtd['note'], trnmtd['product'], trnmtd['is_tmRNA']
                ])

                conn.commit()

        sql = """
                        INSERT INTO genome(identifier, source_file, accession,  name, source, organism, description, taxonomy, 
                            collection_date, country, db_xref, host, isolation_source, strain, lab_host, sequence, sequence_md5, length)
                        values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """

        seqmd5 = hashlib.md5(str(seq.seq).encode('utf-8')).hexdigest()
        tax = "; ".join(seq.annotations['taxonomy'])

        c.execute(sql, [seq.id, gbkf, seq.annotations['accessions'][0], seq.name, seq.annotations['source'],
                             seq.annotations['organism'], seq.description, tax, srcmtd['collection_date'],
                             srcmtd['country'], srcmtd['db_xref'], srcmtd['host'], srcmtd['isolation_source'], srcmtd['strain'], srcmtd['lab_host'],
                             str(seq.seq), seqmd5, len(seq)])
        conn.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load genbank data into an SQLite table')
    parser.add_argument('-f', help='GenBank file to parse', required=True)
    parser.add_argument('-d', help='SQLite database', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    conn = database_handles.connect_to_db(args.d, args.v)
    load_genbank_file(args.f, conn, args.v)