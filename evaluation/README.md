# Search Evaluation System - Complete Guide

## 📋 Overview

This folder contains the complete evaluation system for measuring search quality. The system uses a golden dataset with 26 test queries and 2,009 relevance judgments to calculate Precision@10, Recall@10, NDCG@10, and an overall accuracy score.

**Key Features:**
- ✅ No code changes needed when updating golden dataset
- ✅ Real-time progress tracking in UI
- ✅ Flexible handling of query ID formats
- ✅ Comprehensive metrics with detailed explanations
- ✅ Automated evaluation with verbose logging

---

## 🚀 Quick Start

### Method 1: Streamlit UI (Recommended)

1. **Start the app:**
   ```bash
   streamlit run src/ui/streamlit_app.py
   ```

2. **Navigate to "Search Evaluation" section**

3. **Click "🔄 Recalculate Search Accuracy"**

4. **Watch the progress bar** - Shows which query is being evaluated (e.g., "Evaluating query 5/26...")

5. **View results** - Metrics displayed immediately after completion

### Method 2: Python Script

```python
from src.core.evaluation import SearchEvaluator
from src.core.search_engine import SemanticSearcher

# Initialize
searcher = SemanticSearcher()
evaluator = SearchEvaluator()

# Run evaluation
results = evaluator.evaluate_all(searcher, k=10, verbose=True)

# Print summary
print(f"Final Accuracy: {results['final_accuracy_score']:.2%}")
print(f"Precision@10:   {results['mean_precision']:.2%}")
print(f"Recall@10:      {results['mean_recall']:.2%}")
print(f"NDCG@10:        {results['mean_ndcg']:.2%}")
```

---

## 📊 Metrics Explained

### Precision@10
**What it measures:** Percentage of top 10 results that are actually relevant

**Formula:** `(# of relevant docs in top 10) / 10`

**Example:**
- Top 10 results returned
- 7 are marked as relevant in golden dataset
- Precision@10 = 7/10 = 70%

**Range:** 0.0 to 1.0 (0% to 100%)
**Higher is better** ✅

---

### Recall@10
**What it measures:** Percentage of all relevant documents that appear in top 10

**Formula:** `(# of relevant docs in top 10) / (total # of relevant docs)`

**Example:**
- 20 relevant documents exist (per golden dataset)
- 5 appear in top 10 results
- Recall@10 = 5/20 = 25%

**Range:** 0.0 to 1.0 (0% to 100%)
**Higher is better** ✅

---

### NDCG@10 (Normalized Discounted Cumulative Gain)
**What it measures:** Ranking quality considering relevance scores and positions

**Why it matters:** Penalizes highly relevant documents that appear lower in results

**Formula:**
```
DCG@10 = Σ (relevance_score / log2(position + 1))
IDCG@10 = DCG with perfect ranking
NDCG@10 = DCG@10 / IDCG@10
```

**Example:**
- Document with relevance=10 at position 1: High contribution
- Document with relevance=10 at position 10: Lower contribution
- NDCG rewards better positioning

**Range:** 0.0 to 1.0 (0% to 100%)
**Higher is better** ✅

---

### Final Accuracy Score
**Formula:** `0.5 × NDCG@10 + 0.25 × Precision@10 + 0.25 × Recall@10`

**Why this formula:**
- NDCG weighted 50% (ranking quality most important)
- Precision weighted 25% (result relevance)
- Recall weighted 25% (coverage of relevant docs)

**Range:** 0.0 to 1.0 (0% to 100%)
**Higher is better** ✅

---

## 📁 Golden Dataset Format

### File Locations
```
search-evaluation-goldens/goldens/v1/
├── queries.json              # Test queries (REQUIRED)
├── relevance_judgments.json  # Relevance scores (REQUIRED)
├── expected_results.json     # Expected rankings (OPTIONAL)
└── metadata.json            # Dataset info (OPTIONAL)
```

### queries.json Format

```json
{
  "version": "1.0",
  "queries": [
    {
      "id": "q001",              // Can be "id" OR "query_id" - both work!
      "query": "search query text",  // REQUIRED
      "intent": "informational",     // OPTIONAL
      "difficulty": "medium"         // OPTIONAL
    }
  ]
}
```

**Required:**
- `queries` (array): List of query objects
- `id` or `query_id` (string): Unique identifier
- `query` (string): Search query text

**Optional:**
- `version`, `description`, `created_date`
- `intent`, `difficulty`, custom fields

**Flexible Features:**
✅ Use either `"id"` or `"query_id"` field
✅ Add any number of queries (not limited to 26)
✅ Query IDs don't need to be sequential
✅ Optional fields won't break evaluation

---

### relevance_judgments.json Format

```json
{
  "version": "1.0",
  "judgments": [
    {
      "query_id": "q001",        // Must match query id
      "query": "search query text",
      "results": [
        {
          "id": "tool_123",      // Document ID (format: category_number)
          "title": "Tool Name",  // OPTIONAL but helpful
          "relevance_score": 10, // REQUIRED: 1-10 scale
          "reason": "Why relevant"  // OPTIONAL
        }
      ]
    }
  ]
}
```

**Required:**
- `judgments` (array): List of judgment objects
- `query_id` (string): Must match ID from queries.json
- `results` (array): List of relevant documents
  - `id` (string): Document identifier
  - `relevance_score` (integer): 1-10 scale

**Document ID Format:**
- Format: `{category}_{number}`
- Examples: `tool_123`, `course_45`, `provider_7`
- Categories: `tool`, `course`, `case_study`, `service_provider`

---

## 🔄 Updating the Golden Dataset

### Will I Need to Change Code?

**NO!** The evaluation system is completely flexible.

### What You CAN Change (No Code Needed):
✅ Add/remove queries
✅ Change query text
✅ Modify relevance scores
✅ Add/remove relevant documents
✅ Update metadata fields
✅ Change from `"id"` to `"query_id"` or vice versa
✅ Increase/decrease number of queries

### What You CANNOT Change:
❌ JSON file structure (must keep same keys)
❌ Document ID format (must be `category_number`)
❌ File names (queries.json, relevance_judgments.json)
❌ Relevance score scale (must be 1-10)

### How to Update:

1. **Edit JSON files** in `search-evaluation-goldens/goldens/v1/`
2. **Keep the same format** (see examples above)
3. **Run evaluation** - No code changes required!

**Example Update Scenarios:**

**Add a new query:**
```json
// Just add to queries.json
{
  "id": "q027",
  "query": "new search query"
}

// And add corresponding judgment
{
  "query_id": "q027",
  "results": [...]
}
```

**Change relevance scores:**
```json
// Just edit the scores
{
  "id": "tool_123",
  "relevance_score": 9  // Changed from 10
}
```

**Remove a query:**
```json
// Just delete from both files
// System automatically adapts to new count
```

---

## 📈 Understanding Results

### Sample Output

```
================================================================================
EVALUATION COMPLETE
================================================================================
Final Accuracy: 0.4448 (44.48%)
Precision@10:   0.5269 (52.69%)
Recall@10:      0.2459 (24.59%)
NDCG@10:        0.5031 (50.31%)
================================================================================
```

### What These Numbers Mean:

**Final Accuracy: 44.48%**
- Overall search quality score
- Baseline for comparison
- Track this over time to measure improvements

**Precision@10: 52.69%**
- On average, 5.27 out of 10 results are relevant
- Room for improvement in result quality
- Focus: Better ranking algorithms

**Recall@10: 24.59%**
- Finding about 1/4 of all relevant documents
- Many relevant docs not in top 10
- Focus: Better retrieval methods

**NDCG@10: 50.31%**
- Ranking quality is moderate
- Highly relevant docs not always at top
- Focus: Improve scoring/boosting

### Per-Query Results

```
[1/26] q001: P@10=0.000, R@10=0.000, NDCG@10=0.000
[2/26] q002: P@10=0.500, R@10=0.250, NDCG@10=0.450
[3/26] q003: P@10=0.700, R@10=0.350, NDCG@10=0.620
...
```

**How to interpret:**
- **All zeros (q001):** No relevant results found - investigate this query
- **High scores:** Query works well - analyze what makes it successful
- **Low scores:** Query needs attention - refine algorithm or dataset

---

## 🎨 UI Features

### Progress Tracking

When you click "Recalculate Search Accuracy", you'll see:

1. **Initialization message:**
   ```
   🔄 Initializing evaluation system...
   ```

2. **Progress bar:**
   - Visual bar showing 0% → 100%
   - Updates in real-time as queries are evaluated

3. **Status updates:**
   ```
   🔍 Evaluating query 5/26: 'digital tools for NGOs'
   ```

4. **Terminal logging:**
   ```
   [5/26] q005: P@10=0.600, R@10=0.300, NDCG@10=0.550
   ```

5. **Completion message:**
   ```
   ✅ Evaluation completed successfully!
   ```

### Results Display

**Aggregate Metrics Table:**
| Metric | Score |
|--------|-------|
| Final Accuracy | 44.48% ↑ 52.69% |
| Precision@10 | 52.69% ↑ 52.69% |
| Recall@10 | 24.59% ↑ 24.59% |
| NDCG@10 | 50.31% ↑ 50.31% |

**Per-Query Breakdown:**
- Expandable section showing all 26 queries
- Individual metrics for each query
- Query text and scores side-by-side

---

## 🔧 Technical Details

### System Architecture

**Main Components:**
1. `src/core/evaluation.py` - SearchEvaluator class
2. `src/ui/streamlit_app.py` - UI integration with progress tracking
3. `search-evaluation-goldens/` - Golden dataset storage

**Key Classes:**
- `SearchEvaluator` - Main evaluation engine
  - `load_golden_dataset()` - Loads queries and judgments
  - `evaluate_query()` - Evaluates single query
  - `evaluate_all()` - Runs full evaluation
  - `calculate_precision_at_k()` - Precision metric
  - `calculate_recall_at_k()` - Recall metric
  - `calculate_ndcg_at_k()` - NDCG metric

**Flexible Query ID Handling:**
```python
# Works with both 'id' and 'query_id' fields
query_id = query_data.get('id') or query_data.get('query_id', f'q{i:03d}')
```

This ensures compatibility with different JSON formats without code changes.

---

## 🐛 Troubleshooting

### Issue: KeyError: 'query_id'

**Cause:** Mismatch between field names in JSON files

**Fix:** Already handled! System now supports both `"id"` and `"query_id"`

**How it works:**
- Checks for `"id"` first
- Falls back to `"query_id"`
- Generates fallback ID if neither exists

---

### Issue: No results displayed

**Cause:** Golden dataset files not found

**Fix:**
1. Verify files exist: `search-evaluation-goldens/goldens/v1/queries.json`
2. Check file paths in terminal output
3. Ensure JSON is valid (use JSON validator)

---

### Issue: Unexpected scores (all zeros)

**Possible causes:**
- Search index needs rebuilding
- Document IDs don't match
- Relevance scores missing

**Fix:**
1. Delete `vectorstore/` folder
2. Restart Streamlit app (rebuilds index)
3. Verify document IDs match between index and judgments
4. Check relevance_judgments.json for completeness

---

### Issue: Progress bar stuck

**Cause:** Long-running query evaluation

**What to do:**
- Check terminal output - evaluation continues in background
- Large datasets take longer (26 queries ≈ 30-60 seconds)
- Don't refresh browser - wait for completion

---

## 💡 Best Practices

### 1. Regular Evaluation
Run evaluation after:
- Changing search algorithms
- Updating embeddings model
- Modifying ranking logic
- Adding new data sources

### 2. Baseline Tracking
```python
# Save baseline results
baseline = {
    'date': '2025-12-28',
    'accuracy': 0.4448,
    'precision': 0.5269,
    'recall': 0.2459,
    'ndcg': 0.5031
}

# Compare after changes
improvement = new_accuracy - baseline['accuracy']
print(f"Improvement: {improvement:+.2%}")
```

### 3. Query Analysis
Focus on queries with:
- **All zero scores** - Critical failures
- **Low NDCG (<0.3)** - Poor ranking
- **Low recall (<0.2)** - Missing relevant docs

### 4. Dataset Quality
- Review relevance scores quarterly
- Add edge cases and difficult queries
- Include variety of intents (navigational, informational, transactional)
- Maintain 1-10 scale consistency

### 5. Incremental Improvements
- Fix one query type at a time
- Document what changes improved scores
- Test on full dataset after each change
- Keep changelog of improvements

---

## 📝 Recent Implementation Details

### ✅ Fixed KeyError Issue
- **Problem:** `KeyError: 'query_id'` when running evaluation
- **Solution:** Flexible query ID handling supporting both `"id"` and `"query_id"`
- **Impact:** No code changes needed when updating golden dataset

### ✅ Enhanced UI
- Added real-time progress bar
- Live status updates for each query
- Smooth animations and transitions
- Terminal logging integration
- Better error handling and display

---

**Last Updated:** December 29, 2025
**System Version:** 2.0
