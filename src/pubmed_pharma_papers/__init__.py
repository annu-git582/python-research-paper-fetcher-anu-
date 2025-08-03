"""
PubMed Pharma Papers - A tool for fetching research papers with pharmaceutical/biotech affiliations.
"""

from .core import PubMedPharmaFetcher
from .pubmed_client import PubMedClient, Paper, Author
from .company_identifier import CompanyIdentifier, CompanyMatch
from .csv_writer import CSVWriter, PaperRecord

__version__ = "0.1.0"
__author__ = "Assistant"
__email__ = "assistant@example.com"

__all__ = [
    "PubMedPharmaFetcher",
    "PubMedClient", 
    "Paper",
    "Author",
    "CompanyIdentifier",
    "CompanyMatch", 
    "CSVWriter",
    "PaperRecord"
]
