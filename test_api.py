"""
Test script for the FastAPI semantic search endpoints
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

# Test queries
test_queries = [
    {"query": "AI tools for education", "k": 5},
    {"query": "digital transformation consultants", "k": 5},
    {"query": "python training courses", "k": 5},
    {"query": "salesforce implementation case study", "k": 5},
    {"query": "data analytics", "k": 10, "min_score": 0.2},
]

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Total documents: {data['total_documents']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_stats_endpoint():
    """Test the stats endpoint"""
    print("\n📊 Testing stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats retrieved successfully")
            print(f"   Total documents: {data['total_documents']}")
            print(f"   Model: {data['model_name']}")
            print(f"   Categories: {data['categories']}")
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats error: {e}")

def test_categories_endpoint():
    """Test the categories endpoint"""
    print("\n📂 Testing categories endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/categories")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Categories retrieved successfully")
            print(f"   Available categories: {data['categories']}")
            print(f"   Category counts: {data['category_counts']}")
        else:
            print(f"❌ Categories failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories error: {e}")

def test_search_endpoint():
    """Test the search endpoint with multiple queries"""
    print("\n🔍 Testing search endpoint...")
    
    for i, query_data in enumerate(test_queries, 1):
        print(f"\n--- Test Query {i} ---")
        print(f"Query: {query_data['query']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/search",
                json=query_data,
                headers={"Content-Type": "application/json"}
            )
            request_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Search successful (request: {request_time:.2f}ms, engine: {data['execution_time_ms']:.2f}ms)")
                print(f"   Status: {data['status']}")
                print(f"   Total results: {data['total_results']}")
                print(f"   Category: {data['detected_category']}")
                
                # Show top 3 results
                for j, result in enumerate(data['results'][:3], 1):
                    print(f"   {j}. [{result['category_type']}] {result['title']}")
                    print(f"      Score: {result['score']:.3f} (S:{result['semantic_score']:.3f}, T:{result['tfidf_score']:.3f})")
                    print(f"      URL: {result['url']}")
                
            else:
                print(f"❌ Search failed: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Search error: {e}")

def test_search_debug_endpoint():
    """Test the debug search endpoint"""
    print("\n🐛 Testing debug search endpoint...")
    
    test_query = {"query": "AI tools", "k": 3}
    
    try:
        response = requests.post(
            f"{BASE_URL}/search/debug",
            json=test_query,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug search successful")
            print(f"   Execution time: {data['execution_time_ms']:.2f}ms")
            print(f"   Raw results count: {len(data.get('raw_results', []))}")
        else:
            print(f"❌ Debug search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Debug search error: {e}")

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n⚠️ Testing error handling...")
    
    # Test empty query
    try:
        response = requests.post(
            f"{BASE_URL}/search",
            json={"query": ""},
            headers={"Content-Type": "application/json"}
        )
        print(f"Empty query response: {response.status_code}")
    except Exception as e:
        print(f"Empty query error: {e}")
    
    # Test invalid JSON
    try:
        response = requests.post(
            f"{BASE_URL}/search",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        print(f"Invalid JSON response: {response.status_code}")
    except Exception as e:
        print(f"Invalid JSON error: {e}")

if __name__ == "__main__":
    print("🚀 Starting API Tests...")
    print("=" * 60)
    
    # Test all endpoints
    test_health_endpoint()
    test_stats_endpoint()
    test_categories_endpoint()
    test_search_endpoint()
    test_search_debug_endpoint()
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ API testing complete!")
    
    # Example curl commands
    print("\n📋 Example curl commands:")
    print("curl -X GET 'http://localhost:8000/health'")
    print("curl -X POST 'http://localhost:8000/search' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"query\": \"AI tools\", \"k\": 5}'")
