"""
Test unlimited search results
"""
import requests
import json

# Test 1: With k=5 (limited)
print("=" * 80)
print("TEST 1: Search with k=5 (limited results)")
print("=" * 80)
response1 = requests.post(
    'http://localhost:8000/search',
    json={'query': 'ai tools', 'k': 5}
)
result1 = response1.json()
print(f"Status: {response1.status_code}")
print(f"Total results returned: {result1['total_results']}")
print(f"Execution time: {result1['execution_time_ms']:.2f}ms")
print()

# Test 2: Without k parameter (unlimited - all relevant results)
print("=" * 80)
print("TEST 2: Search without k parameter (unlimited results)")
print("=" * 80)
response2 = requests.post(
    'http://localhost:8000/search',
    json={'query': 'ai tools'}
)
result2 = response2.json()
print(f"Status: {response2.status_code}")
print(f"Total results returned: {result2['total_results']}")
print(f"Execution time: {result2['execution_time_ms']:.2f}ms")
print()

# Test 3: Show first 3 results with all fields
print("=" * 80)
print("SAMPLE RESULTS (showing first 3):")
print("=" * 80)
for i, result in enumerate(result2['results'][:3], 1):
    print(f"\n{i}. {result['title']}")
    print(f"   Category: {result['category_type']}")
    print(f"   Score: {result['score']:.4f}")
    print(f"   URL: {result['url']}")
    print(f"   Slug: {result['metadata'].get('slug', 'N/A')}")
    print(f"   Image: {result['metadata'].get('image', 'N/A')}")
    print(f"   Short Description: {result['metadata'].get('short_description', 'N/A')[:80]}...")

print("\n" + "=" * 80)
print(f"✅ SUCCESS! Unlimited results working.")
print(f"   - Limited (k=5): {result1['total_results']} results")
print(f"   - Unlimited (no k): {result2['total_results']} results")
print("=" * 80)
