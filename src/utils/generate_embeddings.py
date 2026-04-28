print("Script started...")

import json
import faiss
import os
import sys
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle

# Ensure emoji/log output works on Windows terminals using legacy encodings.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Import the data loader utility
from data_loader import load_category_data

# Setup output directory
os.makedirs("vectorstore", exist_ok=True)

# Clear previous vectorstore
if os.path.exists("vectorstore/faiss_index.index"):
    os.remove("vectorstore/faiss_index.index")
if os.path.exists("vectorstore/metadata.json"):
    os.remove("vectorstore/metadata.json")
if os.path.exists("vectorstore/tfidf.pkl"):
    os.remove("vectorstore/tfidf.pkl")

# Initialize data containers
all_texts = []
all_metadata = []
raw_texts = []  # For TF-IDF

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

print("\n" + "="*80)
print("📚 LOADING DATA FROM SPLIT FILES")
print("="*80)

# ============================================================================
# 1. PROCESS TOOLS
# ============================================================================
try:
    tools_data = load_category_data("tools")
    print(f"\n✅ Loaded {len(tools_data)} tools from data/tools/")
    
    for tool in tools_data:
        # Extract fields for embedding
        # API fields: category (array), sub_category (array), title, long_description
        category = ' '.join(tool.get('category', [])) if isinstance(tool.get('category'), list) else tool.get('category', '')
        sub_category = ' '.join(tool.get('sub_category', [])) if isinstance(tool.get('sub_category'), list) else tool.get('sub_category', '')
        title = tool.get('title', '')
        long_desc = tool.get('long_description', '')
        
        # Create embedding text (same order as Excel: category, sub_category, title, description)
        embed_text = f"{category} {sub_category} {title} {long_desc}"
        
        # Create metadata entry
        metadata_entry = {
            "sheet": "Cleaned Sheet",  # Keep same sheet name for compatibility
            "column_headers": ["Category", "Sub-Category", "Name of Tool"],
            "values": [category, sub_category, title],
            "short_description": tool.get('short_description', ''),
            "image": tool.get('image', ''),
            "url": tool.get('url', ''),
            "slug": tool.get('slug', ''),
            "id": tool.get('id', ''),
            "category": "tool"
        }
        
        all_metadata.append(metadata_entry)
        all_texts.append(embed_text)
        raw_texts.append(embed_text)

except FileNotFoundError as e:
    print(f"⚠️  {e}")

# ============================================================================
# 2. PROCESS SERVICES
# ============================================================================
try:
    services_data = load_category_data("services")
    print(f"✅ Loaded {len(services_data)} services from data/service_providers/")
    
    for service in services_data:
        # Extract fields for embedding
        # API fields: title, long_description
        title = service.get('title', '')
        long_desc = service.get('long_description', '')
        
        # Create embedding text
        embed_text = f"{title} {long_desc}"
        
        # Create metadata entry
        metadata_entry = {
            "sheet": "Service Provider Profiles",  # Keep same sheet name
            "column_headers": ["Name of Service Provider"],
            "values": [title],
            "short_description": service.get('short_description', ''),
            "image": service.get('image', ''),
            "url": service.get('url', ''),
            "slug": service.get('slug', '')
        }
        
        all_metadata.append(metadata_entry)
        all_texts.append(embed_text)
        raw_texts.append(embed_text)

except FileNotFoundError as e:
    print(f"⚠️  {e}")

# ============================================================================
# 3. PROCESS COURSES
# ============================================================================
try:
    courses_data = load_category_data("courses")
    print(f"✅ Loaded {len(courses_data)} courses from data/courses/")
    
    for course in courses_data:
        # Extract fields for embedding
        # API fields: explore_by_skill, topic, title, long_description, tools_techniques_covered
        skill = course.get('explore_by_skill', '')
        topic = course.get('topic', '')
        title = course.get('title', '')
        long_desc = course.get('long_description', '')
        tools_covered = course.get('tools_techniques_covered', '')
        
        # Create embedding text (same order as Excel: skill, topic, title, description, tools)
        embed_text = f"{tools_covered} {long_desc} {title} {topic} {skill}"
        
        # Create metadata entry
        metadata_entry = {
            "sheet": "Training Program",  # Keep same sheet name
            "column_headers": ["Skill", "Topic", "Course Title"],
            "values": [skill, topic, title],
            "short_description": course.get('short_description', ''),
            "image": course.get('image', ''),
            "url": course.get('url', ''),
            "slug": course.get('slug', '')
        }
        
        all_metadata.append(metadata_entry)
        all_texts.append(embed_text)
        raw_texts.append(embed_text)

except FileNotFoundError as e:
    print(f"⚠️  {e}")

# ============================================================================
# 4. PROCESS CASE STUDIES
# ============================================================================
try:
    case_studies_data = load_category_data("case_studies")
    print(f"✅ Loaded {len(case_studies_data)} case studies from data/case_studies/")
    
    for cs in case_studies_data:
        # Extract and clean the organization name from title
        case_study_title = cs.get("title", "")
        # Extract org name (everything before the first colon)
        clean_org_name = case_study_title.split(':')[0].strip()
        
        # Extract fields for embedding
        # API fields: title, keyword (replaces industry+problem_type), long_description (replaces summary)
        title = cs.get('title', '')
        keyword = cs.get('keyword', '')  # NEW: replaces industry + problem_type
        long_desc = cs.get('long_description', '')  # Replaces summary
        
        # Prioritize organization name by placing it first, then add case study keywords
        # This ensures direct name searches match strongly while maintaining thematic discoverability
        embed_text = f"{clean_org_name} {clean_org_name} {clean_org_name} case study {title} {keyword} {long_desc}"
        
        # Create display data
        display_data = [title, keyword]  # NEW: displaying keyword instead of separate industry/problem_type
        
        # Store metadata
        metadata_entry = {
            "sheet": "case-studies",
            "column_headers": ["Title", "Keywords"],  # CHANGED: Now uses Keywords
            "values": display_data,
            "case_study_id": cs.get('id'),
            "summary": long_desc,  # Store long_description as summary
            "word_count": len(long_desc.split()) if long_desc else 0,
            "keyword": keyword,  # NEW: Store keyword field
            "short_description": cs.get('short_description', ''),
            "image": cs.get('image', ''),
            "url": cs.get('url', ''),
            "slug": cs.get('slug', ''),
            "id": cs.get('id', ''),
            "category": "case_study"
        }
        
        all_metadata.append(metadata_entry)
        all_texts.append(embed_text)
        raw_texts.append(embed_text)
        
        # Debug: Print first case study details
        if cs.get("id") == 1:
            print(f"DEBUG: Case study {cs.get('id')} embed text preview: {embed_text[:200]}...")

except FileNotFoundError as e:
    print(f"⚠️  {e}")

# ============================================================================
# 5. PROCESS INSIGHTS
# ============================================================================
try:
    insights_data = load_category_data("insights")
    print(f"✅ Loaded {len(insights_data)} insights from data/insights/")

    for insight in insights_data:
        # Extract fields for embedding as requested
        title = insight.get('title', '')
        short_desc = insight.get('short_description', '')
        keyword = insight.get('keyword', '')

        # Embedding input schema: title + short_description + keyword
        embed_text = f"{title} {short_desc} {keyword}"

        metadata_entry = {
            "sheet": "Insights",
            "column_headers": ["Title", "Short Description", "Keyword"],
            "values": [title, short_desc, keyword],
            # Preserve all API fields for downstream consumers
            "id": insight.get('id', ''),
            "title": title,
            "short_description": short_desc,
            "image": insight.get('image', ''),
            "url": insight.get('url', ''),
            "slug": insight.get('slug', ''),
            "keyword": keyword,
            "category": "insight"
        }

        all_metadata.append(metadata_entry)
        all_texts.append(embed_text)
        raw_texts.append(embed_text)

except FileNotFoundError as e:
    print(f"⚠️  {e}")

# ============================================================================
# GENERATE AND SAVE EMBEDDINGS
# ============================================================================
print(f"\n{'='*80}")
print(f"🔄 Generating embeddings for {len(all_texts)} items...")
embeddings = model.encode(all_texts)

# Generate TF-IDF vectors
print("🔄 Generating TF-IDF vectors...")
tfidf = TfidfVectorizer(
    max_features=1000,
    stop_words='english',
    ngram_range=(1, 2)
)
tfidf_vectors = tfidf.fit_transform(raw_texts)

# Save TF-IDF vectorizer and vectors
with open("vectorstore/tfidf.pkl", "wb") as f:
    pickle.dump({
        'vectorizer': tfidf,
        'vectors': tfidf_vectors
    }, f)

# Save metadata
with open("vectorstore/metadata.json", "w", encoding="utf-8") as f:
    json.dump(all_metadata, f, ensure_ascii=False, indent=2)

# Save FAISS index
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)
faiss.write_index(index, "vectorstore/faiss_index.index")

print(f"✅ FAISS index built with {len(all_texts)} entries.")
print(f"✅ TF-IDF vectors generated with {tfidf_vectors.shape[1]} features.")
print("="*80)
print("✨ Embeddings generation complete!")
print("="*80)
