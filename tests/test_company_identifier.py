"""
Tests for company identifier module.
"""

import pytest
from pubmed_pharma_papers.company_identifier import CompanyIdentifier

class TestCompanyIdentifier:
    """Test cases for CompanyIdentifier class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.identifier = CompanyIdentifier()
    
    def test_is_non_academic_affiliation_pharma_company(self):
        """Test identification of pharmaceutical company affiliations."""
        affiliation = "Pfizer Inc., New York, NY, USA"
        assert self.identifier.is_non_academic_affiliation(affiliation) is True
    
    def test_is_non_academic_affiliation_university(self):
        """Test identification of university affiliations."""
        affiliation = "Department of Biology, Harvard University, Cambridge, MA"
        assert self.identifier.is_non_academic_affiliation(affiliation) is False
    
    def test_is_non_academic_affiliation_hospital(self):
        """Test identification of hospital affiliations."""
        affiliation = "Massachusetts General Hospital, Boston, MA"
        assert self.identifier.is_non_academic_affiliation(affiliation) is False
    
    def test_identify_companies_known_company(self):
        """Test identification of known pharmaceutical companies."""
        affiliation = "Novartis Pharmaceuticals Corporation, Basel, Switzerland"
        matches = self.identifier.identify_companies(affiliation)
        
        assert len(matches) > 0
        assert any('novartis' in match.company_name.lower() for match in matches)
    
    def test_identify_companies_keyword_match(self):
        """Test identification based on keywords."""
        affiliation = "BioTech Solutions Therapeutics, San Francisco, CA"
        matches = self.identifier.identify_companies(affiliation)
        
        assert len(matches) > 0
    
    def test_identify_companies_empty_affiliation(self):
        """Test handling of empty affiliation."""
        matches = self.identifier.identify_companies("")
        assert len(matches) == 0
    
    def test_extract_company_names(self):
        """Test extraction of company names from matches."""
        affiliation = "Pfizer Inc., New York, NY"
        matches = self.identifier.identify_companies(affiliation)
        company_names = self.identifier.extract_company_names(matches)
        
        assert len(company_names) > 0
        assert isinstance(company_names[0], str)
