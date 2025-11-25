print("Script started...")

import pandas as pd
import json
import faiss
import os
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from fuzzywuzzy import fuzz
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

# Sheet configurations with row boundaries
sheet_configs = [
    {
        "filename": "tools.xlsx",
        "sheet_name": "Cleaned Sheet",  # Changed from "tools" to actual sheet name
        "embed_cols": [0, 1, 2, 4],
        "display_cols": [0, 1, 2, 16],  # Added column Q (index 16) for short_description
        "column_headers": ["Category", "Sub-Category", "Name of Tool", "short_description"],
        "skip_rows": 0,  # No need to skip rows in cleaned sheet
        "max_rows": 231
    },
    {
        "filename": "service-providers.xlsx",
        "sheet_name": "Service Provider Profiles",
        "embed_cols": [0, 1],
        "display_cols": [0, 14],  # Added column O (index 14) for short_description
        "column_headers": ["Name of Service Provider", "short_description"],
        "skip_rows": 0,
        "max_rows": 25
    },
    {
        "filename": "training-courses.xlsx",
        "sheet_name": "Training Program",
        "embed_cols": [8, 10, 2, 1, 0],
        "display_cols": [0, 1, 2, 14],  # Added column O (index 14) for short_description
        "column_headers": ["Skill", "Topic", "Course Title", "short_description"],
        "skip_rows": 0,
        "max_rows": 110
    },
    {
        "type": "case_studies",
        "filename": "case_studies_metadata.json",
        "embed_fields": ["title", "industry", "problem_type", "summary"],  # Removed full_text, focused on GROQ summary, NOT including short_description
        "display_fields": ["title", "industry", "problem_type"],
        "column_headers": ["Title", "Industry", "Problem Type"]
    }
]

# Initialize data containers
all_texts = []
all_metadata = []
raw_texts = []  # For TF-IDF

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Process each sheet
for config in sheet_configs:
    # Handle case studies differently
    if config.get("type") == "case_studies":
        filepath = os.path.join("data", config["filename"])
        
        if not os.path.exists(filepath):
            print(f"Case studies file not found: {filepath}")
            continue
            
        try:
            # Load case studies metadata
            with open(filepath, 'r', encoding='utf-8') as f:
                case_studies = json.load(f)
            
            print(f"Loaded {len(case_studies)} case studies from {config['filename']}")
            
            for cs in case_studies:
                # Create embedding text from multiple fields
                embed_text_parts = []
                for field in config["embed_fields"]:
                    if field in cs and cs[field]:
                        text = str(cs[field])
                        embed_text_parts.append(text)
                
                embed_text = " ".join(embed_text_parts)
                
                # Enhance embedding text with explicit case study keywords for better semantic matching
                embed_text = f"case study case studies success story impact story {embed_text}"
                
                # Create display data
                display_data = []
                for field in config["display_fields"]:
                    display_data.append(cs.get(field, ""))
                
                # Store metadata
                metadata_entry = {
                    "sheet": "case-studies",
                    "column_headers": config["column_headers"],
                    "values": display_data,
                    "case_study_id": cs.get("id"),
                    "summary": cs.get("summary", ""),
                    "full_text": cs.get("full_text", "")[:500] + "..." if len(cs.get("full_text", "")) > 500 else cs.get("full_text", ""),
                    "word_count": cs.get("word_count", 0),
                    "industry": cs.get("industry", ""),
                    "problem_type": cs.get("problem_type", ""),
                    "short_description": cs.get("short_description", "")  # Add short_description
                }
                all_metadata.append(metadata_entry)
                all_texts.append(embed_text)
                raw_texts.append(embed_text)
                
                # Debug: Print first case study details
                if cs.get("id") == 1:
                    print(f"DEBUG: Case study 1 embed text preview: {embed_text[:200]}...")
            
        except Exception as e:
            print(f"Error processing case studies: {e}")
            continue
    else:
        # Original Excel processing logic
        filepath = os.path.join("data", config["filename"])

        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue

        try:
            # Read Excel with proper sheet and skip_rows handling
            if "skip_rows" in config and config["skip_rows"] > 0:
                # Skip metadata rows if needed
                df = pd.read_excel(filepath, sheet_name=config["sheet_name"], header=0, skiprows=config["skip_rows"], nrows=config["max_rows"])
            else:
                # Normal reading (for cleaned sheets with proper headers)
                df = pd.read_excel(filepath, sheet_name=config["sheet_name"], header=0, nrows=config["max_rows"])
            print(f"Loaded {len(df)} rows from {config['filename']} sheet '{config['sheet_name']}' (max: {config['max_rows']})")
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            continue

        # Remove the old skip_row logic since we now use skiprows in read_excel

        try:
            embed_df = df.iloc[:, config["embed_cols"]]
            display_df = df.iloc[:, config["display_cols"]]
        except IndexError:
            print(f"Column indices out of range in {config['filename']}")
            continue

        # Convert to clean strings and join for embedding
        texts = embed_df.fillna("").astype(str).agg(" ".join, axis=1).tolist()
        display_data = display_df.fillna("").astype(str).values.tolist()
        
        # Store raw texts for TF-IDF
        raw_texts.extend(texts)

        for row_data in display_data:
            # Extract short_description (last item in row_data based on our config)
            short_desc = row_data[-1] if len(row_data) > 0 else ""
            # Remove short_description from values array (keep only display fields)
            values_without_short_desc = row_data[:-1] if len(row_data) > 1 else row_data
            
            metadata_entry = {
                "sheet": config["sheet_name"],
                "column_headers": config["column_headers"][:-1],  # Exclude short_description from headers
                "values": values_without_short_desc,
                "short_description": short_desc  # Add as separate field
            }
            all_metadata.append(metadata_entry)

        all_texts.extend(texts)

# Generate and save embeddings
print(f"Generating embeddings for {len(all_texts)} rows...")
embeddings = model.encode(all_texts)

# Generate TF-IDF vectors
print("Generating TF-IDF vectors...")
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

print(f"FAISS index built with {len(all_texts)} entries.")
print(f"TF-IDF vectors generated with {tfidf_vectors.shape[1]} features.")
print("Row boundaries applied:")
print("  - Sheet 1: 231 rows")
print("  - Sheet 2: 25 rows") 
print("  - Sheet 3: 110 rows")