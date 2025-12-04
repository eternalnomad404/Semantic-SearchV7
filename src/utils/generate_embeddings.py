print("Script started...")

import json
import faiss
import os
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle

# Setup output directory
os.makedirs("vectorstore", exist_ok=True)

# Clear previous vectorstore
if os.path.exists("vectorstore/faiss_index.index"):
    os.remove("vectorstore/faiss_index.index")
if os.path.exists("vectorstore/metadata.json"):
    os.remove("vectorstore/metadata.json")
if os.path.exists("vectorstore/tfidf.pkl"):
    os.remove("vectorstore/tfidf.pkl")

# API Data file paths
API_DATA_FILES = {
    "tools": "data/tools_data.json",
    "services": "data/services_data.json",
    "courses": "data/courses_data.json",
    "case_studies": "data/case_studies_data.json"
}

# Initialize data containers
all_texts = []
all_metadata = []
raw_texts = []  # For TF-IDF

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

print("\n" + "="*80)
print("📚 LOADING DATA FROM API CACHE FILES")
print("="*80)

# ============================================================================
# 1. PROCESS TOOLS
# ============================================================================
tools_file = API_DATA_FILES["tools"]
if os.path.exists(tools_file):
    with open(tools_file, 'r', encoding='utf-8') as f:
        tools_data = json.load(f)
    
    print(f"\n✅ Loaded {len(tools_data)} tools from {tools_file}")
    
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
            "slug": tool.get('slug', '')
        }
        
        all_metadata.append(metadata_entry)
        all_texts.append(embed_text)
        raw_texts.append(embed_text)

else:
    print(f"⚠️  Tools data file not found: {tools_file}")

# ============================================================================
# 2. PROCESS SERVICES
# ============================================================================
services_file = API_DATA_FILES["services"]
if os.path.exists(services_file):
    with open(services_file, 'r', encoding='utf-8') as f:
        services_data = json.load(f)
    
    print(f"✅ Loaded {len(services_data)} services from {services_file}")
    
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

else:
    print(f"⚠️  Services data file not found: {services_file}")

# ============================================================================
# 3. PROCESS COURSES
# ============================================================================
courses_file = API_DATA_FILES["courses"]
if os.path.exists(courses_file):
    with open(courses_file, 'r', encoding='utf-8') as f:
        courses_data = json.load(f)
    
    print(f"✅ Loaded {len(courses_data)} courses from {courses_file}")
    
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

else:
    print(f"⚠️  Courses data file not found: {courses_file}")

# ============================================================================
# 4. PROCESS CASE STUDIES
# ============================================================================
case_studies_file = API_DATA_FILES["case_studies"]
if os.path.exists(case_studies_file):
    with open(case_studies_file, 'r', encoding='utf-8') as f:
        case_studies_data = json.load(f)
    
    print(f"✅ Loaded {len(case_studies_data)} case studies from {case_studies_file}")
    
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
            "slug": cs.get('slug', '')
        }
        
        all_metadata.append(metadata_entry)
        all_texts.append(embed_text)
        raw_texts.append(embed_text)
        
        # Debug: Print first case study details
        if cs.get("id") == 1:
            print(f"DEBUG: Case study {cs.get('id')} embed text preview: {embed_text[:200]}...")

else:
    print(f"⚠️  Case studies data file not found: {case_studies_file}")

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
