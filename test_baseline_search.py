"""
Baseline search test - captures current system results before API migration
"""
import sys
sys.path.insert(0, 'src')
from core.search_engine import SemanticSearcher
import json

# Initialize searcher
print("Initializing search engine with current system...")
searcher = SemanticSearcher()

# Test queries
test_queries = [
    "Learning Link Foundation",
    "Salesforce CRM",
    "AI chatbot course",
    "data visualization"
]

results_baseline = {}

print("\n" + "="*80)
print("BASELINE SEARCH TEST - CURRENT SYSTEM")
print("="*80)

for query in test_queries:
    print(f"\n🔍 Query: '{query}'")
    results, detected_category = searcher.search(query, k=5)
    
    results_baseline[query] = {
        "detected_category": detected_category,
        "total_results": len(results),
        "top_5": []
    }
    
    for i, result in enumerate(results[:5], 1):
        metadata = result['metadata']
        sheet = metadata.get('sheet', 'unknown')
        
        result_info = {
            "rank": i,
            "score": round(result['score'], 4),
            "sheet": sheet,
            "semantic_score": round(result['semantic_score'], 4),
            "tfidf_score": round(result['tfidf_score'], 4)
        }
        
        # Add identifying info based on category
        if 'case-studies' in sheet.lower():
            result_info["title"] = metadata.get('values', ['N/A'])[0] if metadata.get('values') else 'N/A'
            result_info["industry"] = metadata.get('industry', 'N/A')
        else:
            values = metadata.get('values', [])
            # Tools: index 2 is Name of Tool
            # Services: index 0 is Provider Name
            # Courses: index 2 is Course Title
            if 'cleaned sheet' in sheet.lower() and len(values) >= 3:
                result_info["name"] = values[2]  # Name of Tool
            elif 'service provider' in sheet.lower() and len(values) >= 1:
                result_info["name"] = values[0]  # Provider Name
            elif 'training' in sheet.lower() and len(values) >= 3:
                result_info["name"] = values[2]  # Course Title
            else:
                result_info["name"] = values[0] if values else 'N/A'
        
        results_baseline[query]["top_5"].append(result_info)
        
        print(f"  {i}. Score: {result['score']:.4f} | {sheet}")
        if 'case-studies' in sheet.lower():
            print(f"     Title: {result_info['title']}")
        else:
            print(f"     Name: {result_info['name']}")

# Save baseline results
with open('baseline_results.json', 'w', encoding='utf-8') as f:
    json.dump(results_baseline, f, indent=2, ensure_ascii=False)

print("\n" + "="*80)
print("✅ Baseline results saved to baseline_results.json")
print("="*80)
