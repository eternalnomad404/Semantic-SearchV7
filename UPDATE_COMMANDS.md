# 🚀 API Data Update Commands

## ⚡ Quick Reference

### **Step 1: Fetch Fresh Data from Live API**
```powershell
python src/utils/fetch_data_from_apis.py
```

**What this does:**
- Calls all 4 DT4SI APIs:
  - `https://dt4si.com/api/v1/tools`
  - `https://dt4si.com/api/v1/services`
  - `https://dt4si.com/api/v1/courses`
  - `https://dt4si.com/api/v1/case-studies`
- Saves data to JSON cache files in `data/` folder:
  - `data/tools_data.json`
  - `data/services_data.json`
  - `data/courses_data.json`
  - `data/case_studies_data.json`

**Output Example:**
```
================================================================================
🚀 FETCHING DATA FROM DT4SI APIs
================================================================================

📡 Fetching tools from API...
   ✅ Successfully fetched 199 tools
   💾 Saved to data\tools_data.json

📡 Fetching services from API...
   ✅ Successfully fetched 22 services
   💾 Saved to data\services_data.json

📡 Fetching courses from API...
   ✅ Successfully fetched 107 courses
   💾 Saved to data\courses_data.json

📡 Fetching case_studies from API...
   ✅ Successfully fetched 14 case_studies
   💾 Saved to data\case_studies_data.json

✨ All data fetched successfully!
```

---

### **Step 2: Generate Embeddings from Cached Data**
```powershell
python src/utils/generate_embeddings.py
```

**What this does:**
- Reads the 4 JSON cache files from `data/` folder
- Processes all items (tools, services, courses, case studies)
- Creates semantic embeddings using sentence transformers
- Generates TF-IDF vectors for keyword matching
- Saves everything to `vectorstore/` folder:
  - `vectorstore/faiss_index.index` (semantic embeddings)
  - `vectorstore/metadata.json` (all item details)
  - `vectorstore/tfidf.pkl` (keyword vectors)

**Output Example:**
```
================================================================================
📚 LOADING DATA FROM API CACHE FILES
================================================================================

✅ Loaded 199 tools from data/tools_data.json
✅ Loaded 22 services from data/services_data.json
✅ Loaded 107 courses from data/courses_data.json
✅ Loaded 14 case studies from data/case_studies_data.json

================================================================================
🔄 Generating embeddings for 342 items...
🔄 Generating TF-IDF vectors...
✅ FAISS index built with 342 entries.
✅ TF-IDF vectors generated with 1000 features.
================================================================================
✨ Embeddings generation complete!
```

---

## 🔄 Complete Workflow

### **When to Update:**
- ✅ After adding/editing content in your CMS/database
- ✅ Daily/weekly scheduled updates
- ✅ Before deploying to production
- ✅ After bulk content changes

### **Full Update Process:**
```powershell
# Step 1: Fetch fresh data from live API
python src/utils/fetch_data_from_apis.py

# Step 2: Generate embeddings
python src/utils/generate_embeddings.py

# Step 3: Restart your services (if running)
# For API: Ctrl+C then restart
# For Streamlit: Ctrl+C then restart
```

---

## 🎯 What Changes After Running These Commands

### **Before Update:**
- Search uses old embeddings from `vectorstore/`
- Old data from previous API fetch

### **After Update:**
- ✅ Fresh data from live database
- ✅ New/updated tools, services, courses, case studies
- ✅ Updated embeddings with latest content
- ✅ Search results reflect current database state

### **Services Affected:**
1. **FastAPI Server** (`python main.py`)
   - Loads embeddings at startup
   - **Must restart** after regenerating embeddings
   
2. **Streamlit UI** (`streamlit run streamlit_app.py`)
   - Caches embeddings at startup
   - **Must restart** after regenerating embeddings

---

## ⚠️ Important Notes

### **Restart Required:**
After running both commands, **restart your API/Streamlit servers** for changes to take effect:

```powershell
# Press Ctrl+C in the terminal running the server
# Then restart it:

# For API:
python main.py

# For Streamlit:
streamlit run streamlit_app.py
```

### **No Internet Needed for Step 2:**
- Step 1 (fetch) **requires internet** to call APIs
- Step 2 (generate) **works offline** using cached JSON files
- This means you can regenerate embeddings anytime without API calls

### **Data Validation:**
Both scripts will show errors if something fails:
- API connection issues
- Missing data files
- Invalid JSON format
- Model loading errors

---

## 📊 Data Flow Diagram

```
┌─────────────────────────┐
│   Live Database         │
│   (Your CMS/Backend)    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  DT4SI Live APIs        │
│  /api/v1/tools          │
│  /api/v1/services       │
│  /api/v1/courses        │
│  /api/v1/case-studies   │
└────────────┬────────────┘
             │
             ▼ (Step 1: fetch_data_from_apis.py)
┌─────────────────────────┐
│  JSON Cache Files       │
│  data/tools_data.json   │
│  data/services_data.json│
│  data/courses_data.json │
│  data/case_studies_.json│
└────────────┬────────────┘
             │
             ▼ (Step 2: generate_embeddings.py)
┌─────────────────────────┐
│  Vector Store           │
│  vectorstore/           │
│  - faiss_index.index    │
│  - metadata.json        │
│  - tfidf.pkl            │
└────────────┬────────────┘
             │
             ▼ (Load at startup)
┌─────────────────────────┐
│  Search System          │
│  - FastAPI Server       │
│  - Streamlit UI         │
└─────────────────────────┘
```

---

## ✅ Verification

### **Check if Update Worked:**

**Test the API:**
```powershell
# PowerShell command
Invoke-RestMethod -Uri "http://localhost:8000/search" -Method POST -Body '{"query": "Salesforce", "k": 3}' -ContentType "application/json"
```

**Check total documents:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/stats" -Method GET
```

You should see the updated count (342 items from new API data).

---

## 🎯 Summary

**Two simple commands:**
1. `python src/utils/fetch_data_from_apis.py` - Get fresh data
2. `python src/utils/generate_embeddings.py` - Create embeddings

**That's it!** Your search system now uses the latest data from your live database. 🚀
