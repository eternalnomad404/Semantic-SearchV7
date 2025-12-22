# Search Evaluation Golden Datasets

This repository maintains offline golden datasets used to evaluate search relevance and ranking quality.

## Purpose

- **Single source of truth** for search evaluation datasets
- **Decoupled from production** systems for independent evaluation
- **Versioned golden data** to track evaluation dataset evolution
- **Auditable evaluation process** with transparent data lineage

## Repository Structure

```
search-evaluation-goldens/
├── goldens/                    # Golden datasets by version
│   ├── v1/                    # Version 1.0 golden data
│   │   ├── queries.json       # Test queries for evaluation
│   │   ├── expected_results.json  # Expected search results
│   │   ├── relevance_judgments.json  # Human relevance ratings
│   │   └── metadata.json      # Dataset metadata and info
│   └── v2/                    # Version 2.0 (placeholder)
│       └── placeholder.json   # Reserved for future iterations
├── scripts/                   # Evaluation scripts (to be added)
│   └── README.md             # Scripts documentation
└── README.md                 # This file
```

## Usage

1. **Golden Data**: JSON files in `goldens/v*/` contain evaluation datasets
2. **Versioning**: Each version (v1, v2, etc.) represents a complete evaluation dataset
3. **Evaluation Scripts**: The `scripts/` directory is reserved for future evaluation tools
4. **Metadata**: Each version includes metadata about the dataset composition and metrics

## Data Format

All golden data uses JSON format for:
- **queries.json**: Test queries with metadata (intent, difficulty)  
- **expected_results.json**: Expected ranked results for each query
- **relevance_judgments.json**: Human relevance assessments
- **metadata.json**: Version info, metrics, and dataset statistics

## Constraints

- **No application code** - This is a data-only repository
- **No invented data** - All datasets must be real evaluation data
- **Minimal structure** - Keep files and folders to essential evaluation needs only
- **Auditable** - All changes and versions must be transparent and trackable