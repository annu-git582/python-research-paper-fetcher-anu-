"""
Command-line interface for PubMed Pharma Papers.
"""

import argparse
import logging
import sys
from typing import Optional

from .core import PubMedPharmaFetcher

def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[logging.StreamHandler(sys.stderr)]
    )

def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog='get-papers-list',
        description='Fetch research papers from PubMed with pharmaceutical/biotech company affiliations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  get-papers-list "cancer AND drug therapy"
  get-papers-list "COVID-19 AND vaccine" --file results.csv
  get-papers-list "diabetes AND treatment" --debug --file diabetes_papers.csv
  
Query Syntax:
  Supports full PubMed query syntax including:
  - Boolean operators: AND, OR, NOT
  - Field tags: [Title], [Author], [Journal], etc.
  - Date ranges: 2020:2023[PDAT]
  - MeSH terms: "Neoplasms"[Mesh]
        """
    )
    
    parser.add_argument(
        'query',
        help='PubMed search query (supports full PubMed syntax)'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Output filename for CSV results (prints to console if not specified)',
        metavar='FILENAME'
    )
    
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug output'
    )
    
    parser.add_argument(
        '--max-results',
        type=int,
        default=100,
        help='Maximum number of papers to fetch (default: 100)',
        metavar='N'
    )
    
    parser.add_argument(
        '--email',
        help='Email address for PubMed API identification (recommended)',
        metavar='EMAIL'
    )
    
    parser.add_argument(
        '--api-key',
        help='NCBI API key for higher rate limits',
        metavar='KEY'
    )
    
    return parser

def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize fetcher
        fetcher = PubMedPharmaFetcher(
            email=args.email,
            api_key=args.api_key
        )
        
        # Fetch papers
        logger.info("Starting paper fetch process")
        records = fetcher.fetch_papers(args.query, args.max_results)
        
        if not records:
            logger.warning("No papers found with pharmaceutical/biotech affiliations")
            return 0
        
        # Output results
        if args.file:
            fetcher.save_to_file(records, args.file)
        else:
            fetcher.print_to_console(records)
        
        logger.info(f"Process completed successfully. Found {len(records)} relevant papers.")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.debug:
            logger.exception("Full traceback:")
        return 1

if __name__ == '__main__':
    sys.exit(main())
