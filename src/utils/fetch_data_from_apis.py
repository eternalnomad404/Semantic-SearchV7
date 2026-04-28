"""
Fetch data from DT4SI APIs and save to JSON cache files
This script replaces Excel file reading with API-based data fetching

Usage: python src/utils/fetch_data_from_apis.py
"""

import requests
import json
import os
import sys
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Ensure emoji/log output works on Windows terminals using legacy encodings.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# API Configuration
API_BASE_URL = "https://dt4si.com/api/v1"
API_ENDPOINTS = {
    "tools": f"{API_BASE_URL}/tools",
    "services": f"{API_BASE_URL}/services",
    "courses": f"{API_BASE_URL}/courses",
    "case_studies": f"{API_BASE_URL}/case-studies",
    "insights": f"{API_BASE_URL}/insights"
}

# Output directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Output folder paths for split data
OUTPUT_FOLDERS = {
    "tools": os.path.join(DATA_DIR, "tools"),
    "services": os.path.join(DATA_DIR, "service_providers"),
    "courses": os.path.join(DATA_DIR, "courses"),
    "case_studies": os.path.join(DATA_DIR, "case_studies"),
    "insights": os.path.join(DATA_DIR, "insights")
}

# Create output folders
for folder in OUTPUT_FOLDERS.values():
    os.makedirs(folder, exist_ok=True)

# Records per file target (aiming for ~600 lines per file)
# Based on analysis: tools ~15 lines/rec, courses ~12, services ~9, case_studies ~10
# Being conservative to ensure no file exceeds 600 lines
RECORDS_PER_FILE = {
    "tools": 38,          # ~38 records = ~577 lines (safer)
    "courses": 49,        # ~49 records = ~588 lines
    "services": 66,       # ~66 records = ~600 lines
    "case_studies": 59,   # ~59 records = ~596 lines
    "insights": 40        # conservative default for longer keyword/description fields
}


def fetch_from_api(endpoint: str, category: str) -> List[Dict[str, Any]]:
    """
    Fetch data from API endpoint
    
    Args:
        endpoint: Full API URL
        category: Category name (for logging)
        
    Returns:
        List of items from API
    """
    try:
        print(f"\n📡 Fetching {category} from API...")
        print(f"   URL: {endpoint}")
        
        response = requests.get(endpoint, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response structures
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            # Try common keys
            items = data.get('data') or data.get('items') or data.get(category) or []
        else:
            items = []
        
        print(f"   ✅ Successfully fetched {len(items)} {category}")
        return items
        
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout: API took too long to respond")
        raise
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error: Could not reach API")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"   ❌ HTTP Error: {e}")
        raise
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        raise


def compare_data(old_data: List[Dict], new_data: List[Dict], category: str) -> Tuple[int, int, int]:
    """
    Compare old and new data to detect changes
    
    Returns:
        Tuple of (added_count, removed_count, modified_count)
    """
    # Create sets of IDs/slugs for comparison
    old_ids = set()
    old_items = {}
    
    for item in old_data:
        item_id = item.get('id') or item.get('slug') or item.get('title', '')
        old_ids.add(item_id)
        old_items[item_id] = item
    
    new_ids = set()
    new_items = {}
    
    for item in new_data:
        item_id = item.get('id') or item.get('slug') or item.get('title', '')
        new_ids.add(item_id)
        new_items[item_id] = item
    
    # Calculate differences
    added = new_ids - old_ids
    removed = old_ids - new_ids
    
    # Check for modifications in common items
    modified = 0
    common_ids = old_ids & new_ids
    for item_id in common_ids:
        if old_items[item_id] != new_items[item_id]:
            modified += 1
    
    return len(added), len(removed), modified


def save_to_split_files(data: List[Dict], category: str):
    """
    Save fetched data to multiple JSON files in category folder.
    
    Splits data into chunks to keep each file under ~600 lines while
    maintaining semantic units (complete records).
    
    Args:
        data: List of records to save
        category: Category name (tools, services, courses, case_studies)
    """
    folder_path = OUTPUT_FOLDERS[category]
    records_per_file = RECORDS_PER_FILE[category]
    
    # Load existing data from all files in the folder for comparison
    old_data = []
    existing_files = list(Path(folder_path).glob("*.json"))
    for existing_file in existing_files:
        try:
            with open(existing_file, 'r', encoding='utf-8') as f:
                old_data.extend(json.load(f))
        except:
            pass
    
    # Compare and show changes
    if old_data:
        added, removed, modified = compare_data(old_data, data, category)
        
        if added > 0 or removed > 0 or modified > 0:
            print(f"   📝 Changes detected:")
            if added > 0:
                print(f"      ➕ {added} new items added")
            if removed > 0:
                print(f"      ➖ {removed} items removed")
            if modified > 0:
                print(f"      ✏️  {modified} items modified")
        else:
            print(f"   ✔️  No changes detected")
    else:
        print(f"   📝 First time fetch - {len(data)} items")
    
    # Clear old files
    for old_file in existing_files:
        try:
            os.remove(old_file)
        except:
            pass
    
    # Split data into chunks and save
    total_files = (len(data) + records_per_file - 1) // records_per_file
    
    for i in range(0, len(data), records_per_file):
        chunk = data[i:i + records_per_file]
        file_num = (i // records_per_file) + 1
        
        # Generate filename with zero-padded number
        if category == "services":
            filename = f"providers_part_{file_num:02d}.json"
        else:
            filename = f"{category}_part_{file_num:02d}.json"
        
        filepath = os.path.join(folder_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"   ❌ Failed to save {filepath}: {e}")
            raise
    
    print(f"   💾 Saved {len(data)} records to {total_files} file(s) in {folder_path}/")


def save_to_file(data: List[Dict], filepath: str, category: str):
    """
    DEPRECATED: Legacy function for backward compatibility.
    Now redirects to save_to_split_files.
    """
    save_to_split_files(data, category)


def main():
    """Main execution function"""
    print("="*80)
    print("🚀 FETCHING DATA FROM DT4SI APIs")
    print("="*80)
    
    all_success = True
    summary = {}
    
    # Fetch data from each API
    for category, endpoint in API_ENDPOINTS.items():
        try:
            # Fetch from API
            data = fetch_from_api(endpoint, category)
            
            # Save to split files in category folder
            save_to_split_files(data, category)
            
            folder_path = OUTPUT_FOLDERS[category]
            file_count = len(list(Path(folder_path).glob("*.json")))
            
            summary[category] = {
                "status": "success",
                "count": len(data),
                "files": file_count,
                "folder": folder_path
            }
            
        except Exception as e:
            all_success = False
            summary[category] = {
                "status": "failed",
                "error": str(e)
            }
    
    # Print summary
    print("\n" + "="*80)
    print("📊 FETCH SUMMARY")
    print("="*80)
    
    for category, info in summary.items():
        if info["status"] == "success":
            print(f"✅ {category.upper()}: {info['count']} items → {info['files']} file(s) in {info['folder']}/")
        else:
            print(f"❌ {category.upper()}: FAILED - {info['error']}")
    
    print("="*80)
    
    if all_success:
        print("✨ All data fetched successfully!")
        print("\nNext step: Run 'python src/utils/generate_embeddings.py' to generate embeddings")
    else:
        print("⚠️  Some APIs failed. Please check errors above and try again.")
        exit(1)


if __name__ == "__main__":
    main()
