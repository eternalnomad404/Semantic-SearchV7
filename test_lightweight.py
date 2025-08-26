#!/usr/bin/env python3
"""
Test script to verify the lightweight search engine works correctly
"""

from search_engine import SemanticSearcher

def test_search():
    print("🔄 Loading search engine...")
    searcher = SemanticSearcher()
    print("✅ Search engine loaded successfully!")
    
    # Test search queries
    test_queries = [
        "AI tools for education",
        "python programming courses", 
        "data science training",
        "machine learning case studies"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        results, category = searcher.search(query, k=3)
        print(f"Found {len(results)} results in category: {category}")
        
        for i, result in enumerate(results, 1):
            values = result['metadata'].get('values', [])
            title = values[0] if values else "N/A"
            score = result['score']
            print(f"  {i}. {title} (Score: {score:.3f})")
    
    print("\n✅ All tests completed successfully!")
    print(f"📊 Total documents: {searcher.get_stats()['total_documents']}")

if __name__ == "__main__":
    test_search()
