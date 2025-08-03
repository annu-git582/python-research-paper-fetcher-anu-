"""
Tests for core module.
"""

import pytest
from unittest.mock import Mock, patch
from pubmed_pharma_papers.core import PubMedPharmaFetcher
from pubmed_pharma_papers.pubmed_client import Paper, Author

class TestPubMedPharmaFetcher:
    """Test cases for PubMedPharmaFetcher class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fetcher = PubMedPharmaFetcher()
    
    @patch('pubmed_pharma_papers.core.PubMedClient')
    @patch('pubmed_pharma_papers.core.CSVWriter')
    def test_fetch_papers_success(self, mock_csv_writer, mock_pubmed_client):
        """Test successful paper fetching."""
        # Mock PubMed client
        mock_client_instance = Mock()
        mock_pubmed_client.return_value = mock_client_instance
        mock_client_instance.search_papers.return_value = ['12345', '67890']
        
        # Mock papers
        mock_papers = [
            Paper(
                pubmed_id='12345',
                title='Test Paper 1',
                publication_date='2023-01-01',
                authors=[
                    Author(name='John Doe', affiliation='Pfizer Inc.')
                ]
            )
        ]
        mock_client_instance.fetch_paper_details.return_value = mock_papers
        
        # Mock CSV writer
        mock_writer_instance = Mock()
        mock_csv_writer.return_value = mock_writer_instance
        mock_writer_instance.filter_and_convert_papers.return_value = []
        
        # Test
        result = self.fetcher.fetch_papers("test query")
        
        # Assertions
        mock_client_instance.search_papers.assert_called_once_with("test query", 100)
        mock_client_instance.fetch_paper_details.assert_called_once_with(['12345', '67890'])
        assert isinstance(result, list)
    
    def test_fetch_papers_no_results(self):
        """Test handling of no search results."""
        with patch.object(self.fetcher.pubmed_client, 'search_papers', return_value=[]):
            result = self.fetcher.fetch_papers("nonexistent query")
            assert result == []
