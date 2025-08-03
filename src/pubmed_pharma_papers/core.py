"""
Core module for fetching and processing PubMed papers with pharma/biotech affiliations.
"""

from typing import List, Optional
import logging
from pathlib import Path

from .pubmed_client import PubMedClient, Paper
from .company_identifier import CompanyIdentifier
from .csv_writer import CSVWriter, PaperRecord

logger = logging.getLogger(__name__)

class PubMedPharmaFetcher:
    """Main class for fetching and processing PubMed papers."""
    
    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the fetcher.
        
        Args:
            email: Email for PubMed API identification
            api_key: API key for higher rate limits
        """
        self.pubmed_client = PubMedClient(email=email, api_key=api_key)
        self.csv_writer = CSVWriter()
    
    def fetch_papers(self, query: str, max_results: int = 100) -> List[PaperRecord]:
        """
        Fetch papers matching query with pharma/biotech affiliations.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results to fetch
            
        Returns:
            List of filtered paper records
            
        Raises:
            Exception: If fetching or processing fails
        """
        try:
            # Search for papers
            logger.info(f"Starting search for query: {query}")
            pubmed_ids = self.pubmed_client.search_papers(query, max_results)
            
            if not pubmed_ids:
                logger.warning("No papers found for the given query")
                return []
            
            # Fetch detailed paper information
            papers = self.pubmed_client.fetch_paper_details(pubmed_ids)
            
            if not papers:
                logger.warning("No paper details could be fetched")
                return []
            
            # Filter and convert to CSV records
            records = self.csv_writer.filter_and_convert_papers(papers)
            
            logger.info(f"Successfully processed {len(records)} papers with pharma/biotech affiliations")
            return records
            
        except Exception as e:
            logger.error(f"Error fetching papers: {e}")
            raise
    
    def save_to_file(self, records: List[PaperRecord], filename: str) -> None:
        """
        Save paper records to CSV file.
        
        Args:
            records: List of paper records
            filename: Output filename
        """
        try:
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                self.csv_writer.write_to_csv(records, f)
                
            logger.info(f"Results saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving to file {filename}: {e}")
            raise
    
    def print_to_console(self, records: List[PaperRecord]) -> None:
        """
        Print paper records to console.
        
        Args:
            records: List of paper records
        """
        try:
            self.csv_writer.write_to_console(records)
        except Exception as e:
            logger.error(f"Error printing to console: {e}")
            raise
