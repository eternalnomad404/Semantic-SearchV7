"""
Fetch image paths from external DT4SI APIs and create slug-to-image mapping.
Run this script whenever external API data changes to refresh image mappings.

Usage:
    python src/utils/fetch_external_images.py
"""

import json
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List
import os


# API Configuration
API_BASE_URL = "https://v3.dt4si.com/api/v1"
API_USERNAME = "devteam"
API_PASSWORD = "Mc9xNdZsJsg"

# API endpoints for each category
API_ENDPOINTS = {
    "tools": f"{API_BASE_URL}/tools",
    "services": f"{API_BASE_URL}/services",
    "courses": f"{API_BASE_URL}/courses",
    "case-studies": f"{API_BASE_URL}/case-studies"
}

# Output file path
OUTPUT_FILE = "data/slug_to_image_mapping.json"


def fetch_category_data(category: str, endpoint: str) -> List[Dict]:
    """
    Fetch data from a single API endpoint with authentication.
    
    Args:
        category: Category name (tools, services, courses, case-studies)
        endpoint: Full API endpoint URL
        
    Returns:
        List of items from the API
    """
    print(f"📡 Fetching {category} from {endpoint}...")
    
    try:
        response = requests.get(
            endpoint,
            auth=HTTPBasicAuth(API_USERNAME, API_PASSWORD),
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different possible response structures
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            # Try common keys for the data array
            items = data.get('data', data.get('items', data.get('results', [data])))
        else:
            print(f"⚠️  Unexpected response format for {category}")
            items = []
        
        print(f"✅ Fetched {len(items)} items from {category}")
        return items
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {category}: {e}")
        return []


def extract_slug_and_image(item: Dict) -> tuple:
    """
    Extract slug and image path from an API item.
    
    Args:
        item: Single item from API response
        
    Returns:
        Tuple of (slug, image_path) or (None, None) if not found
    """
    slug = item.get('slug')
    image = item.get('image')
    
    if slug and image:
        return (slug, image)
    else:
        return (None, None)


def build_slug_to_image_mapping() -> Dict[str, str]:
    """
    Fetch all external API data and build slug-to-image mapping.
    
    Returns:
        Dictionary mapping slugs to image paths
    """
    mapping = {}
    stats = {
        "total_items": 0,
        "items_with_images": 0,
        "categories": {}
    }
    
    print("🚀 Starting image fetch from external APIs...")
    print("=" * 80)
    
    for category, endpoint in API_ENDPOINTS.items():
        items = fetch_category_data(category, endpoint)
        
        category_count = 0
        category_with_images = 0
        
        for item in items:
            slug, image = extract_slug_and_image(item)
            
            if slug and image:
                # Check if slug already exists (shouldn't happen, but safety check)
                if slug in mapping:
                    print(f"⚠️  Duplicate slug found: {slug} (keeping first occurrence)")
                else:
                    mapping[slug] = image
                    category_with_images += 1
            elif slug and not image:
                # Slug exists but no image
                mapping[slug] = None
                
            category_count += 1
        
        stats["categories"][category] = {
            "total": category_count,
            "with_images": category_with_images
        }
        stats["total_items"] += category_count
        stats["items_with_images"] += category_with_images
        
        print(f"   ├─ {category_with_images}/{category_count} items have images")
    
    print("=" * 80)
    print(f"✅ Mapping complete: {stats['items_with_images']}/{stats['total_items']} items with images")
    
    return mapping, stats


def save_mapping_to_file(mapping: Dict[str, str], stats: Dict):
    """
    Save the slug-to-image mapping to a JSON file.
    
    Args:
        mapping: Dictionary of slug -> image_path
        stats: Statistics about the fetch operation
    """
    output_data = {
        "metadata": {
            "total_slugs": len(mapping),
            "total_items_fetched": stats["total_items"],
            "items_with_images": stats["items_with_images"],
            "categories": stats["categories"],
            "last_updated": None  # Will be set by json with timestamp
        },
        "mapping": mapping
    }
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Save to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Mapping saved to: {OUTPUT_FILE}")
    print(f"   ├─ Total slugs: {len(mapping)}")
    print(f"   ├─ With images: {stats['items_with_images']}")
    print(f"   └─ Without images: {len(mapping) - stats['items_with_images']}")


def main():
    """Main execution function"""
    print("\n" + "🎨 DT4SI Image Fetcher ".center(80, "="))
    print("\nThis script fetches image paths from external APIs")
    print("and creates a mapping file for your search results.\n")
    
    # Build the mapping
    mapping, stats = build_slug_to_image_mapping()
    
    if not mapping:
        print("\n❌ No data fetched. Please check:")
        print("   1. API endpoints are correct")
        print("   2. Credentials are valid")
        print("   3. Network connection is working")
        return
    
    # Save to file
    save_mapping_to_file(mapping, stats)
    
    print("\n" + "=" * 80)
    print("✅ Done! Image mapping ready to use.")
    print("\nNext steps:")
    print("   1. Regenerate embeddings: python src/utils/generate_embeddings.py")
    print("   2. Restart API server: python main.py")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
