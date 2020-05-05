
from pppf_accessories import color
import sys
__author__ = 'Rob Edwards'


def protein_to_fasta(conn, outputfile=None, verbose=False):
    """
    Extract the protein sequences from the SQLite database and
    print them out in fasta format.

    Note that at the moment this uses the md5sum as the ID, although
    an option to extend this would be to use the original IDs from the
    protein table. If you want that, please create a GitHub issue.

    :param conn: the database connection
    :param outputfile: the name of the output file. Otherwise stdout
    :param verbose: more output
    """

    if verbose:
        sys.stderr.write(f"{color.GREEN}Creating fasta file{color.ENDC}\n")

    ex = conn.cursor().execute("SELECT protein_md5sum, protein_sequence from protein_sequence")
    out = open(outputfile, 'w') if outputfile else sys.stdout
    for row in ex.fetchall():
        out.write(f">{row[0]}\n{row[1]}\n")
    
    if out is not sys.stdout:
        out.close() 
        
