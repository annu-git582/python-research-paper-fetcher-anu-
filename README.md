# PubMed Pharma Papers

A Python tool for fetching research papers from PubMed that have at least one author affiliated with pharmaceutical or biotechnology companies. The tool outputs results in CSV format with detailed author and company information.

## Features

- **PubMed Integration**: Fetches papers using the official PubMed API with full query syntax support
- **Company Identification**: Identifies pharmaceutical and biotech companies using comprehensive databases and heuristics
- **Flexible Output**: Save results to CSV file or print to console
- **Command-line Interface**: Easy-to-use CLI with helpful options
- **Robust Error Handling**: Comprehensive error handling and logging
- **Type Safety**: Fully typed Python code for better maintainability

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)

### Setup

1. Clone the repository:
\`\`\`bash
git clone https://github.com/username/pubmed-pharma-papers.git
cd pubmed-pharma-papers
\`\`\`

2. Install dependencies using Poetry:
\`\`\`bash
poetry install
\`\`\`

3. Activate the virtual environment:
\`\`\`bash
poetry shell
\`\`\`

## Usage

### Command Line Interface

The tool provides a command-line interface accessible via the `get-papers-list` command:

\`\`\`bash
# Basic usage - print results to console
get-papers-list "cancer AND drug therapy"

# Save results to CSV file
get-papers-list "COVID-19 AND vaccine" --file results.csv

# Enable debug output
get-papers-list "diabetes AND treatment" --debug --file diabetes_papers.csv

# Limit number of results
get-papers-list "Alzheimer AND drug" --max-results 50 --file alzheimer_drugs.csv

# Use email for API identification (recommended)
get-papers-list "heart disease AND medication" --email your.email@example.com
\`\`\`

### Command Line Options

- `query`: PubMed search query (required)
- `-f, --file FILENAME`: Output CSV filename (optional, prints to console if not specified)
- `-d, --debug`: Enable debug output
- `--max-results N`: Maximum number of papers to fetch (default: 100)
- `--email EMAIL`: Email address for PubMed API identification (recommended)
- `--api-key KEY`: NCBI API key for higher rate limits
- `-h, --help`: Show help message

### Query Syntax

The tool supports PubMed's full query syntax:

- **Boolean operators**: `AND`, `OR`, `NOT`
- **Field tags**: `[Title]`, `[Author]`, `[Journal]`, `[Affiliation]`
- **Date ranges**: `2020:2023[PDAT]`
- **MeSH terms**: `"Neoplasms"[Mesh]`

Examples:
\`\`\`bash
get-papers-list "cancer[Title] AND (chemotherapy OR immunotherapy)"
get-papers-list "Smith J[Author] AND diabetes"
get-papers-list "2022:2023[PDAT] AND COVID-19"
\`\`\`

### Python Module Usage

You can also use the tool as a Python module:

\`\`\`python
from pubmed_pharma_papers import PubMedPharmaFetcher

# Initialize fetcher
fetcher = PubMedPharmaFetcher(email="your.email@example.com")

# Fetch papers
records = fetcher.fetch_papers("cancer AND drug therapy", max_results=50)

# Save to file
fetcher.save_to_file(records, "results.csv")

# Or print to console
fetcher.print_to_console(records)
