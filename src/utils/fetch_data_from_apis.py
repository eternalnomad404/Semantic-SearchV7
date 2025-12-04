"""
Fetch data from DT4SI APIs and save to JSON cache files
This script replaces Excel file reading with API-based data fetching

Usage: python src/utils/fetch_data_from_apis.py
"""

import requests
import json
import os
from typing import Dict, List, Any

# API Configuration
API_BASE_URL = "https://dt4si.com/api/v1"
API_ENDPOINTS = {
    "tools": f"{API_BASE_URL}/tools",
    "services": f"{API_BASE_URL}/services",
    "courses": f"{API_BASE_URL}/courses",
    "case_studies": f"{API_BASE_URL}/case-studies"
}

# Output directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Output file paths
OUTPUT_FILES = {
    "tools": os.path.join(DATA_DIR, "tools_data.json"),
    "services": os.path.join(DATA_DIR, "services_data.json"),
    "courses": os.path.join(DATA_DIR, "courses_data.json"),
    "case_studies": os.path.join(DATA_DIR, "case_studies_data.json")
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


def save_to_file(data: List[Dict], filepath: str, category: str):
    """Save fetched data to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"   💾 Saved to {filepath}")
    except Exception as e:
        print(f"   ❌ Failed to save {category}: {e}")
        raise


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
            
            # Save to file
            output_file = OUTPUT_FILES[category]
            save_to_file(data, output_file, category)
            
            summary[category] = {
                "status": "success",
                "count": len(data),
                "file": output_file
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
            print(f"✅ {category.upper()}: {info['count']} items → {info['file']}")
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
