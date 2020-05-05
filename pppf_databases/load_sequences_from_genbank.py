"""
Load the sequences from GenBank.

This is the correct way to do this!
"""

import sys
import argparse

from pppf_accessories import color
from pppf_databases import connect_to_db, disconnect

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

    if verbose:
        sys.stderr.write(f"{color.PINK}Parsing {gbkf}{color.ENDC}\n")

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
                prtmd5 = hashlib.md5(prtmtd['translation'].upper().encode('utf-8')).hexdigest()
                if 'product' in prtmtd:
                    if len(prtmtd['product']) > 1:
                        prtmtd['product'] = prtmtd['product'][0].upper() + prtmtd['product'][1:].lower()
                    elif len(prtmtd['prodcut']) == 0:
                        prtmtd['product'] = "Hypothetical protein"
                else:
                    prtmtd['product'] = "Hypothetical protein"

                # if there is no protein sequence (yes, there are some genbank records with no protein sequence)
                # we don't continue
                if len(prtmtd['translation']) == 0:
                    sys.stderr.write(f"SKIPPED: No translation for {prtmtd['protein_id']}\n")
                    continue

                # add the protein sequence and md5sum and sequence if we don't already have it
                ex = c.execute("select protein_md5sum from protein_sequence where protein_md5sum = ?", [prtmd5])
                tple = ex.fetchone()
                if not tple:
                    c.execute("INSERT INTO protein_sequence (protein_md5sum, protein_sequence) VALUES (?,?)",
                              [prtmd5, prtmtd['translation'].upper()])

                sql = """
                    INSERT INTO protein(protein_id, contig, product, db_xref, protein_md5sum, 
                    length, EC_number, genename, locus_tag, note, ribosomal_slippage, transl_table) values 
                    (?,?,?,?,?,?,?,?,?,?,?,?)                  
                """
                c.execute(sql, [
                    prtmtd['protein_id'], seq.name, prtmtd['product'], prtmtd['db_xref'], 
                    prtmd5, len(prtmtd['translation']), prtmtd['EC_number'], prtmtd['gene'], prtmtd['locus_tag'],
                    prtmtd['note'], prtmtd['ribosomal_slippage'], prtmtd['transl_table']
                ])

                proteinrow = c.lastrowid

                dnaseq = str(feat.extract(seq).seq)
                dnamd5 = hashlib.md5(dnaseq.upper().encode('utf-8')).hexdigest()
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
                dnamd5 = hashlib.md5(dnaseq.upper().encode('utf-8')).hexdigest()
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

        seqmd5 = hashlib.md5(str(seq.seq).upper().encode('utf-8')).hexdigest()
        tax = "; ".join(seq.annotations['taxonomy'])

        c.execute(sql, [seq.id, gbkf, seq.annotations['accessions'][0], seq.name, seq.annotations['source'],
                             seq.annotations['organism'], seq.description, tax, srcmtd['collection_date'],
                             srcmtd['country'], srcmtd['db_xref'], srcmtd['host'], srcmtd['isolation_source'], srcmtd['strain'], srcmtd['lab_host'],
                             str(seq.seq), seqmd5, len(seq)])
        conn.commit()

def create_full_text_search(conn, verbose=True):
    """
    Create a full text search virtual table on the protein products
    :param conn: the database connection
    :param verbose: more output
    :return: 
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Adding full text search capabilities{color.ENDC}\n")
    
    c = conn.cursor()
    c.execute("CREATE VIRTUAL TABLE protein_fts using FTS5(protein_rowid, product);")
    c.execute("INSERT INTO protein_fts SELECT protein_rowid, product FROM protein;")
    conn.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load genbank data into an SQLite table')
    parser.add_argument('-f', help='GenBank file to parse', required=True)
    parser.add_argument('-p', help='Phage SQLite database', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    conn = connect_to_db(args.p, args.v)
    load_genbank_file(args.f, conn, args.v)
    create_full_text_search(conn, args.v)
    disconnect(conn, args.v)
