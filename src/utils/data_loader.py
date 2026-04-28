"""
Data loader utility for reading split JSON files from the new folder structure.

This module provides transparent loading of data that has been split across 
multiple files for maintainability, while preserving backward compatibility
with code that expects a single list of records.

Usage:
    from src.utils.data_loader import load_category_data
    
    tools = load_category_data('tools')
    services = load_category_data('services')
"""

import json
import os
from typing import List, Dict, Any
from pathlib import Path


# Get the project root directory (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Map category names to their folder paths (relative to project root)
CATEGORY_FOLDERS = {
    "tools": PROJECT_ROOT / "data" / "tools",
    "services": PROJECT_ROOT / "data" / "service_providers",
    "courses": PROJECT_ROOT / "data" / "courses",
    "case_studies": PROJECT_ROOT / "data" / "case_studies",
    "insights": PROJECT_ROOT / "data" / "insights"
}


def load_category_data(category: str) -> List[Dict[str, Any]]:
    """
    Load all data for a given category from split JSON files.
    
    This function reads all JSON files in the category's folder and combines
    them into a single list, maintaining the order determined by filename sorting.
    
    Args:
        category: Category name ('tools', 'services', 'courses', 'case_studies', 'insights')
        
    Returns:
        List of dictionaries containing all records for the category
        
    Raises:
        ValueError: If category is not recognized
        FileNotFoundError: If category folder doesn't exist
    """
    if category not in CATEGORY_FOLDERS:
        raise ValueError(
            f"Unknown category '{category}'. "
            f"Valid categories: {list(CATEGORY_FOLDERS.keys())}"
        )
    
    folder_path = CATEGORY_FOLDERS[category]
    
    # Check if folder exists
    if not os.path.exists(folder_path):
        raise FileNotFoundError(
            f"Category folder not found: {folder_path}\n"
            f"Please run 'python src/utils/fetch_data_from_apis.py' first."
        )
    
    # Find all JSON files in the folder
    json_files = sorted(Path(folder_path).glob("*.json"))
    
    if not json_files:
        raise FileNotFoundError(
            f"No JSON files found in {folder_path}"
        )
    
    # Load and combine all data
    all_data = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle both list and dict responses
                if isinstance(data, list):
                    all_data.extend(data)
                elif isinstance(data, dict):
                    # If it's a dict with a 'data' key, use that
                    all_data.extend(data.get('data', []))
                    
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {json_file}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading {json_file}: {e}")
    
    return all_data


def get_category_file_count(category: str) -> int:
    """
    Get the number of split files for a category.
    
    Args:
        category: Category name
        
    Returns:
        Number of JSON files in the category folder
    """
    if category not in CATEGORY_FOLDERS:
        return 0
    
    folder_path = CATEGORY_FOLDERS[category]
    if not os.path.exists(folder_path):
        return 0
    
    return len(list(Path(folder_path).glob("*.json")))


def get_all_categories_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    Load data for all categories at once.
    
    Returns:
        Dictionary mapping category names to their data lists
    """
    result = {}
    for category in CATEGORY_FOLDERS.keys():
        try:
            result[category] = load_category_data(category)
        except (FileNotFoundError, ValueError) as e:
            print(f"Warning: Could not load {category}: {e}")
            result[category] = []
    
    return result
