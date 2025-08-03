"""
PubMed API client for fetching research papers.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
import requests
import time
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class Author:
    """Represents a paper author with affiliation information."""
    name: str
    affiliation: str
    email: Optional[str] = None
    is_corresponding: bool = False

@dataclass
class Paper:
    """Represents a research paper with metadata."""
    pubmed_id: str
    title: str
    publication_date: str
    authors: List[Author]
    abstract: str = ""

class PubMedClient:
    """Client for interacting with PubMed API."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize PubMed client.
        
        Args:
            email: Email for API identification (recommended by NCBI)
            api_key: API key for higher rate limits
        """
        self.email = email
        self.api_key = api_key
        self.session = requests.Session()
        
    def search_papers(self, query: str, max_results: int = 100) -> List[str]:
        """
        Search for papers using PubMed query syntax.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results to return
            
        Returns:
            List of PubMed IDs
            
        Raises:
            requests.RequestException: If API request fails
        """
        logger.info(f"Searching PubMed with query: {query}")
        
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml'
        }
        
        if self.email:
            params['email'] = self.email
        if self.api_key:
            params['api_key'] = self.api_key
            
        try:
            response = self.session.get(
                f"{self.BASE_URL}esearch.fcgi",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            id_list = root.find('.//IdList')
            
            if id_list is None:
                return []
                
            pubmed_ids = [id_elem.text for id_elem in id_list.findall('Id') if id_elem.text]
            logger.info(f"Found {len(pubmed_ids)} papers")
            return pubmed_ids
            
        except requests.RequestException as e:
            logger.error(f"Error searching PubMed: {e}")
            raise
        except ET.ParseError as e:
            logger.error(f"Error parsing XML response: {e}")
            raise
    
    def fetch_paper_details(self, pubmed_ids: List[str]) -> List[Paper]:
        """
        Fetch detailed information for papers by PubMed IDs.
        
        Args:
            pubmed_ids: List of PubMed IDs
            
        Returns:
            List of Paper objects with detailed information
        """
        if not pubmed_ids:
            return []
            
        logger.info(f"Fetching details for {len(pubmed_ids)} papers")
        
        # Process in batches to avoid overwhelming the API
        batch_size = 20
        all_papers = []
        
        for i in range(0, len(pubmed_ids), batch_size):
            batch = pubmed_ids[i:i + batch_size]
            papers = self._fetch_batch_details(batch)
            all_papers.extend(papers)
            
            # Rate limiting - be respectful to NCBI servers
            if i + batch_size < len(pubmed_ids):
                time.sleep(0.5)
                
        return all_papers
    
    def _fetch_batch_details(self, pubmed_ids: List[str]) -> List[Paper]:
        """Fetch details for a batch of PubMed IDs."""
        params = {
            'db': 'pubmed',
            'id': ','.join(pubmed_ids),
            'retmode': 'xml'
        }
        
        if self.email:
            params['email'] = self.email
        if self.api_key:
            params['api_key'] = self.api_key
            
        try:
            response = self.session.get(
                f"{self.BASE_URL}efetch.fcgi",
                params=params,
                timeout=60
            )
            response.raise_for_status()
            
            return self._parse_paper_details(response.content)
            
        except requests.RequestException as e:
            logger.error(f"Error fetching paper details: {e}")
            return []
    
    def _parse_paper_details(self, xml_content: bytes) -> List[Paper]:
        """Parse XML response to extract paper details."""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for article in root.findall('.//PubmedArticle'):
                paper = self._parse_single_paper(article)
                if paper:
                    papers.append(paper)
                    
        except ET.ParseError as e:
            logger.error(f"Error parsing paper details XML: {e}")
            
        return papers
    
    def _parse_single_paper(self, article_elem: ET.Element) -> Optional[Paper]:
        """Parse a single paper from XML element."""
        try:
            # Extract PubMed ID
            pmid_elem = article_elem.find('.//PMID')
            if pmid_elem is None or not pmid_elem.text:
                return None
            pubmed_id = pmid_elem.text
            
            # Extract title
            title_elem = article_elem.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None and title_elem.text else "No title"
            
            # Extract publication date
            pub_date = self._extract_publication_date(article_elem)
            
            # Extract authors
            authors = self._extract_authors(article_elem)
            
            # Extract abstract
            abstract_elem = article_elem.find('.//Abstract/AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None and abstract_elem.text else ""
            
            return Paper(
                pubmed_id=pubmed_id,
                title=title,
                publication_date=pub_date,
                authors=authors,
                abstract=abstract
            )
            
        except Exception as e:
            logger.error(f"Error parsing single paper: {e}")
            return None
    
    def _extract_publication_date(self, article_elem: ET.Element) -> str:
        """Extract publication date from article element."""
        # Try different date fields
        date_fields = [
            './/PubDate',
            './/ArticleDate',
            './/DateCompleted'
        ]
        
        for field in date_fields:
            date_elem = article_elem.find(field)
            if date_elem is not None:
                year_elem = date_elem.find('Year')
                month_elem = date_elem.find('Month')
                day_elem = date_elem.find('Day')
                
                year = year_elem.text if year_elem is not None else "1900"
                month = month_elem.text if month_elem is not None else "01"
                day = day_elem.text if day_elem is not None else "01"
                
                # Handle month names
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                }
                
                if month in month_map:
                    month = month_map[month]
                elif not month.isdigit():
                    month = "01"
                
                try:
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except:
                    return f"{year}-01-01"
        
        return "1900-01-01"
    
    def _extract_authors(self, article_elem: ET.Element) -> List[Author]:
        """Extract authors from article element."""
        authors = []
        
        author_list = article_elem.find('.//AuthorList')
        if author_list is None:
            return authors
        
        for author_elem in author_list.findall('Author'):
            # Extract name
            last_name_elem = author_elem.find('LastName')
            first_name_elem = author_elem.find('ForeName')
            
            if last_name_elem is None or not last_name_elem.text:
                continue
                
            last_name = last_name_elem.text
            first_name = first_name_elem.text if first_name_elem is not None else ""
            name = f"{first_name} {last_name}".strip()
            
            # Extract affiliation
            affiliation_elem = author_elem.find('.//Affiliation')
            affiliation = affiliation_elem.text if affiliation_elem is not None else ""
            
            # Check if corresponding author (simplified check)
            is_corresponding = 'corresponding' in affiliation.lower()
            
            # Extract email (basic pattern matching)
            email = self._extract_email_from_text(affiliation)
            
            authors.append(Author(
                name=name,
                affiliation=affiliation,
                email=email,
                is_corresponding=is_corresponding
            ))
        
        return authors
    
    def _extract_email_from_text(self, text: str) -> Optional[str]:
        """Extract email address from text using basic pattern matching."""
        import re
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        
        return matches[0] if matches else None
