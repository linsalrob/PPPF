from .formatting import color, colour
from .functions import is_hypothetical
from .genbank import GenBank
from .genbank_download import GenBankDownload
from .genbank_search import GenBankSearch

__all__ = [
    'color', 'colour', 'is_hypothetical',
    'GenBank', 'GenBankDownload', 'GenBankSearch'
]
