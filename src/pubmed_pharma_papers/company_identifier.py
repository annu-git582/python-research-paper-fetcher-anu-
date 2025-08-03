"""
Module for identifying pharmaceutical and biotech companies from author affiliations.
"""

import re
from typing import List, Set, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CompanyMatch:
    """Represents a matched company in an affiliation."""
    company_name: str
    confidence: float
    match_type: str  # 'exact', 'partial', 'keyword'

class CompanyIdentifier:
    """Identifies pharmaceutical and biotech companies from text."""
    
    def __init__(self):
        """Initialize with known company patterns and keywords."""
        self.pharma_companies = self._load_pharma_companies()
        self.biotech_keywords = self._load_biotech_keywords()
        self.academic_keywords = self._load_academic_keywords()
        
    def _load_pharma_companies(self) -> Set[str]:
        """Load known pharmaceutical company names."""
        companies = {
            # Major pharmaceutical companies
            'pfizer', 'johnson & johnson', 'j&j', 'roche', 'novartis', 'merck',
            'sanofi', 'glaxosmithkline', 'gsk', 'astrazeneca', 'bristol myers squibb',
            'bms', 'abbott', 'eli lilly', 'lilly', 'amgen', 'gilead', 'biogen',
            'celgene', 'regeneron', 'vertex', 'moderna', 'biontech', 'illumina',
            'thermo fisher', 'agilent', 'waters', 'perkinelmer', 'danaher',
            'becton dickinson', 'bd', 'medtronic', 'boston scientific',
            'edwards lifesciences', 'intuitive surgical', 'stryker',
            
            # Biotech companies
            'genentech', 'immunogen', 'seattle genetics', 'seagen', 'bluebird bio',
            'crispr therapeutics', 'editas medicine', 'intellia therapeutics',
            'sangamo therapeutics', 'alnylam', 'ionis pharmaceuticals',
            'antisense therapeutics', 'wave life sciences', 'sarepta therapeutics',
            'biomarin', 'alexion', 'ultragenyx', 'horizon therapeutics',
            'jazz pharmaceuticals', 'neurocrine biosciences', 'sage therapeutics',
            'karuna therapeutics', 'compass pathways', 'mindmed',
            
            # Generic and specialty pharma
            'teva', 'mylan', 'viatris', 'sandoz', 'hikma', 'sun pharma',
            'dr reddy', 'lupin', 'cipla', 'aurobindo', 'zydus cadila',
            'torrent pharmaceuticals', 'glenmark', 'alkem laboratories',
            
            # CROs and service providers
            'quintiles', 'iqvia', 'covance', 'parexel', 'pra health sciences',
            'syneos health', 'icon', 'ppd', 'charles river laboratories',
            'wuxi apptec', 'catalent', 'lonza', 'samsung biologics',
            'boehringer ingelheim', 'fujifilm diosynth', 'patheon'
        }
        
        return {company.lower() for company in companies}
    
    def _load_biotech_keywords(self) -> Set[str]:
        """Load keywords that indicate biotech/pharma companies."""
        return {
            'pharmaceuticals', 'pharma', 'therapeutics', 'biosciences',
            'biotechnology', 'biotech', 'biopharma', 'biopharmaceuticals',
            'medicines', 'drugs', 'inc.', 'corp.', 'corporation', 'ltd.',
            'limited', 'company', 'co.', 'laboratories', 'labs', 'research',
            'development', 'clinical', 'trials', 'cro', 'contract research'
        }
    
    def _load_academic_keywords(self) -> Set[str]:
        """Load keywords that indicate academic institutions."""
        return {
            'university', 'college', 'school', 'institute', 'institution',
            'hospital', 'medical center', 'health system', 'clinic',
            'department', 'faculty', 'division', 'center for', 'centre for',
            'national institutes', 'nih', 'nsf', 'government', 'public health',
            'ministry of health', 'veterans affairs', 'va medical'
        }
    
    def is_non_academic_affiliation(self, affiliation: str) -> bool:
        """
        Determine if an affiliation represents a non-academic institution.
        
        Args:
            affiliation: Author affiliation text
            
        Returns:
            True if affiliation appears to be non-academic
        """
        if not affiliation:
            return False
            
        affiliation_lower = affiliation.lower()
        
        # Check for academic keywords first
        for keyword in self.academic_keywords:
            if keyword in affiliation_lower:
                return False
        
        # Check for company keywords or known companies
        for keyword in self.biotech_keywords:
            if keyword in affiliation_lower:
                return True
                
        for company in self.pharma_companies:
            if company in affiliation_lower:
                return True
        
        # Additional heuristics
        # Check for corporate email domains
        if '@' in affiliation and not any(domain in affiliation.lower() 
                                        for domain in ['.edu', '.ac.', '.gov']):
            return True
            
        return False
    
    def identify_companies(self, affiliation: str) -> List[CompanyMatch]:
        """
        Identify pharmaceutical/biotech companies in affiliation text.
        
        Args:
            affiliation: Author affiliation text
            
        Returns:
            List of identified companies with confidence scores
        """
        if not affiliation:
            return []
            
        matches = []
        affiliation_lower = affiliation.lower()
        
        # Check for exact company matches
        for company in self.pharma_companies:
            if company in affiliation_lower:
                # Calculate confidence based on context
                confidence = self._calculate_confidence(affiliation_lower, company)
                matches.append(CompanyMatch(
                    company_name=company.title(),
                    confidence=confidence,
                    match_type='exact'
                ))
        
        # Check for keyword-based matches
        if not matches:
            keyword_matches = self._find_keyword_matches(affiliation)
            matches.extend(keyword_matches)
        
        # Remove duplicates and sort by confidence
        unique_matches = {}
        for match in matches:
            key = match.company_name.lower()
            if key not in unique_matches or match.confidence > unique_matches[key].confidence:
                unique_matches[key] = match
        
        return sorted(unique_matches.values(), key=lambda x: x.confidence, reverse=True)
    
    def _calculate_confidence(self, affiliation: str, company: str) -> float:
        """Calculate confidence score for a company match."""
        base_confidence = 0.8
        
        # Boost confidence for longer company names (more specific)
        if len(company) > 10:
            base_confidence += 0.1
            
        # Boost confidence if company appears at the beginning
        if affiliation.startswith(company):
            base_confidence += 0.1
            
        # Reduce confidence if academic keywords are present
        for keyword in self.academic_keywords:
            if keyword in affiliation:
                base_confidence -= 0.2
                break
        
        return min(1.0, max(0.1, base_confidence))
    
    def _find_keyword_matches(self, affiliation: str) -> List[CompanyMatch]:
        """Find companies based on keyword patterns."""
        matches = []
        affiliation_lower = affiliation.lower()
        
        # Look for patterns like "Company Name Pharmaceuticals"
        pharma_pattern = r'(\w+(?:\s+\w+)*)\s+(pharmaceuticals|pharma|therapeutics|biotech|biosciences)'
        
        for match in re.finditer(pharma_pattern, affiliation_lower):
            company_name = match.group(0).title()
            confidence = 0.6  # Lower confidence for keyword matches
            
            matches.append(CompanyMatch(
                company_name=company_name,
                confidence=confidence,
                match_type='keyword'
            ))
        
        return matches
    
    def extract_company_names(self, matches: List[CompanyMatch], 
                            min_confidence: float = 0.5) -> List[str]:
        """
        Extract company names from matches above confidence threshold.
        
        Args:
            matches: List of company matches
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of company names
        """
        return [match.company_name for match in matches 
                if match.confidence >= min_confidence]
