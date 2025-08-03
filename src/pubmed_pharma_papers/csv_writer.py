"""
Module for writing research paper data to CSV format.
"""

import csv
from typing import List, TextIO, Optional
from dataclasses import dataclass
import logging

from .pubmed_client import Paper, Author
from .company_identifier import CompanyIdentifier

logger = logging.getLogger(__name__)

@dataclass
class PaperRecord:
    """Represents a paper record for CSV output."""
    pubmed_id: str
    title: str
    publication_date: str
    non_academic_authors: str
    company_affiliations: str
    corresponding_author_email: str

class CSVWriter:
    """Handles writing paper data to CSV format."""
    
    def __init__(self):
        """Initialize CSV writer with company identifier."""
        self.company_identifier = CompanyIdentifier()
    
    def filter_and_convert_papers(self, papers: List[Paper]) -> List[PaperRecord]:
        """
        Filter papers with non-academic authors and convert to CSV records.
        
        Args:
            papers: List of Paper objects
            
        Returns:
            List of PaperRecord objects for papers with non-academic authors
        """
        records = []
        
        for paper in papers:
            record = self._process_paper(paper)
            if record and record.non_academic_authors:  # Only include papers with non-academic authors
                records.append(record)
        
        logger.info(f"Filtered {len(records)} papers with non-academic authors from {len(papers)} total papers")
        return records
    
    def _process_paper(self, paper: Paper) -> Optional[PaperRecord]:
        """Process a single paper into a CSV record."""
        try:
            non_academic_authors = []
            company_affiliations = set()
            corresponding_email = ""
            
            for author in paper.authors:
                # Check if author is from non-academic institution
                if self.company_identifier.is_non_academic_affiliation(author.affiliation):
                    non_academic_authors.append(author.name)
                    
                    # Identify companies in affiliation
                    company_matches = self.company_identifier.identify_companies(author.affiliation)
                    company_names = self.company_identifier.extract_company_names(company_matches)
                    company_affiliations.update(company_names)
                
                # Check for corresponding author email
                if author.is_corresponding and author.email:
                    corresponding_email = author.email
                elif author.email and not corresponding_email:
                    # Use any available email if no corresponding author email found
                    corresponding_email = author.email
            
            # If no non-academic authors found, skip this paper
            if not non_academic_authors:
                return None
            
            return PaperRecord(
                pubmed_id=paper.pubmed_id,
                title=paper.title,
                publication_date=paper.publication_date,
                non_academic_authors="; ".join(non_academic_authors),
                company_affiliations="; ".join(sorted(company_affiliations)),
                corresponding_author_email=corresponding_email
            )
            
        except Exception as e:
            logger.error(f"Error processing paper {paper.pubmed_id}: {e}")
            return None
    
    def write_to_csv(self, records: List[PaperRecord], output_file: TextIO) -> None:
        """
        Write paper records to CSV file.
        
        Args:
            records: List of PaperRecord objects
            output_file: File object to write to
        """
        if not records:
            logger.warning("No records to write to CSV")
            return
        
        fieldnames = [
            'PubmedID',
            'Title', 
            'Publication Date',
            'Non-academic Author(s)',
            'Company Affiliation(s)',
            'Corresponding Author Email'
        ]
        
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in records:
            writer.writerow({
                'PubmedID': record.pubmed_id,
                'Title': record.title,
                'Publication Date': record.publication_date,
                'Non-academic Author(s)': record.non_academic_authors,
                'Company Affiliation(s)': record.company_affiliations,
                'Corresponding Author Email': record.corresponding_author_email
            })
        
        logger.info(f"Successfully wrote {len(records)} records to CSV")
    
    def write_to_console(self, records: List[PaperRecord]) -> None:
        """
        Write paper records to console in CSV format.
        
        Args:
            records: List of PaperRecord objects
        """
        import sys
        self.write_to_csv(records, sys.stdout)
