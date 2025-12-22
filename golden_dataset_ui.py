"""
Golden Dataset Viewer - Offline Search Evaluation UI
======================================================
This Streamlit application visualizes the golden dataset used for offline search evaluation.
It does NOT reflect live search results or interact with the production search API.

Purpose: Internal tool for engineers and reviewers to inspect, audit, and analyze
         the manually curated golden dataset used for search quality evaluation.

Run with: streamlit run golden_dataset_ui.py
"""

import streamlit as st
import json
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from collections import Counter

# ============================================================================
# Configuration & Data Loading
# ============================================================================

GOLDEN_DATA_PATH = Path("search-evaluation-goldens/goldens/v1")

@st.cache_data
def load_golden_data():
    """Load all golden dataset files from disk."""
    try:
        with open(GOLDEN_DATA_PATH / "metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        with open(GOLDEN_DATA_PATH / "queries.json", "r", encoding="utf-8") as f:
            queries = json.load(f)
        
        with open(GOLDEN_DATA_PATH / "expected_results.json", "r", encoding="utf-8") as f:
            expected_results = json.load(f)
        
        with open(GOLDEN_DATA_PATH / "relevance_judgments.json", "r", encoding="utf-8") as f:
            relevance_judgments = json.load(f)
        
        return {
            "metadata": metadata,
            "queries": queries,
            "expected_results": expected_results,
            "relevance_judgments": relevance_judgments
        }
    except Exception as e:
        st.error(f"Error loading golden data: {e}")
        return None

def get_relevance_distribution(data: Dict) -> Counter:
    """Calculate distribution of relevance scores across all judgments."""
    scores = []
    for result_set in data["expected_results"]["results"]:
        for item in result_set["expected_results"]:
            scores.append(item["relevance_score"])
    return Counter(scores)

def get_category_distribution(data: Dict) -> Counter:
    """Calculate distribution of categories across all results."""
    categories = []
    for result_set in data["expected_results"]["results"]:
        for item in result_set["expected_results"]:
            categories.append(item["category"])
    return Counter(categories)

# ============================================================================
# UI Components
# ============================================================================

def render_header():
    """Render the main header with disclaimer."""
    st.title("🔍 Golden Dataset Viewer")
    st.subheader("Offline Search Evaluation Interface")
    
    st.warning("""
    ⚠️ **IMPORTANT DISCLAIMER**  
    This interface visualizes the **golden dataset** used for **offline search evaluation**.  
    It does **NOT** reflect live search results or interact with the production search API.  
    
    **Purpose:** Internal inspection and quality assurance for manually curated evaluation data.
    """)
    st.divider()

def render_overview_screen(data: Dict):
    """Screen 1: Dataset Overview and Statistics."""
    st.header("📊 Dataset Overview")
    
    metadata = data["metadata"]
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Dataset Version", metadata["version"])
    
    with col2:
        st.metric("Total Queries", metadata["total_queries"])
    
    with col3:
        st.metric("Total Judgments", metadata["total_judgments"])
    
    with col4:
        st.metric("Last Updated", metadata["last_updated"])
    
    st.divider()
    
    # Relevance score distribution
    st.subheader("Relevance Score Distribution")
    relevance_dist = get_relevance_distribution(data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Display as metrics
        for score in [3, 2, 1]:
            count = relevance_dist.get(score, 0)
            label_map = {3: "Highly Relevant", 2: "Moderately Relevant", 1: "Weakly Relevant"}
            st.metric(f"{label_map[score]} (Score {score})", count)
    
    with col2:
        # Display as DataFrame for easy reading
        rel_df = pd.DataFrame([
            {"Relevance Score": score, "Count": relevance_dist.get(score, 0), 
             "Percentage": f"{relevance_dist.get(score, 0) / metadata['total_judgments'] * 100:.1f}%"}
            for score in [3, 2, 1]
        ])
        st.dataframe(rel_df, hide_index=True, use_container_width=True)
    
    st.divider()
    
    # Category distribution
    st.subheader("Category Distribution")
    category_dist = get_category_distribution(data)
    
    cat_df = pd.DataFrame([
        {"Category": cat, "Count": count}
        for cat, count in category_dist.most_common()
    ])
    st.dataframe(cat_df, hide_index=True, use_container_width=True)
    
    st.divider()
    
    # Metadata details
    st.subheader("Dataset Metadata")
    
    with st.expander("📝 Dataset Description & Notes"):
        st.write("**Description:**", metadata["description"])
        st.write("**Coverage Approach:**", metadata["coverage_approach"])
        st.write("**Notes:**", metadata["notes"])
    
    with st.expander("📂 Data Sources"):
        st.code(metadata["data_source"], language=None)
    
    with st.expander("📏 Evaluation Metrics"):
        for metric in metadata["evaluation_metrics"]:
            st.write(f"• {metric}")

def render_query_view_screen(data: Dict):
    """Screen 2: Query-Level Inspection."""
    st.header("🔎 Query-Level View")
    
    # Query selector
    queries = data["queries"]["queries"]
    query_options = {f"{q['id']}: {q['query']}": q for q in queries}
    
    selected = st.selectbox(
        "Select a query to inspect:",
        options=list(query_options.keys()),
        index=0
    )
    
    selected_query = query_options[selected]
    
    st.divider()
    
    # Query details
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Query ID", selected_query["id"])
    
    with col2:
        st.metric("Intent", selected_query["intent"].title())
    
    with col3:
        st.metric("Difficulty", selected_query["difficulty"].title())
    
    st.info(f"**Query Text:** \"{selected_query['query']}\"")
    
    # Get expected results for this query
    query_results = None
    for result_set in data["expected_results"]["results"]:
        if result_set["query_id"] == selected_query["id"]:
            query_results = result_set
            break
    
    if not query_results:
        st.warning("No expected results found for this query.")
        return
    
    # Get relevance judgments for this query
    query_judgments = None
    for judgment_set in data["relevance_judgments"]["judgments"]:
        if judgment_set["query_id"] == selected_query["id"]:
            query_judgments = judgment_set
            break
    
    st.divider()
    st.subheader(f"Expected Results ({len(query_results['expected_results'])} items)")
    
    # Create a mapping from document_id to reason
    reason_map = {}
    if query_judgments:
        for judgment in query_judgments["results"]:
            reason_map[judgment["id"]] = judgment["reason"]
    
    # Display results in compact expander format similar to original UI
    for result in query_results["expected_results"]:
        # Emoji and label based on relevance
        if result["relevance_score"] == 3:
            emoji = "🟢"
            relevance_label = "High"
        elif result["relevance_score"] == 2:
            emoji = "🟡"
            relevance_label = "Medium"
        else:
            emoji = "⚪"
            relevance_label = "Low"
        
        # Category emoji
        category_emoji = "🛠️" if result["category"] == "tool" else (
            "🏢" if result["category"] == "service_provider" else (
            "📚" if result["category"] == "course" else "📋"
        ))
        
        # Compact expander with title, category, and relevance
        expander_title = f"{category_emoji} {result['category'].replace('_', ' ').title()}: {result['document_title']} (Relevance: {result['relevance_score']}/3 {emoji})"
        
        with st.expander(expander_title):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### Details")
                st.write(f"**Title:** {result['document_title']}")
                st.write(f"**Category:** {result['category'].replace('_', ' ').title()}")
            
            with col2:
                st.markdown("#### Ranking Info")
                st.write(f"**Rank:** {result['rank']}")
                st.write(f"**Relevance:** {result['relevance_score']}/3 ({relevance_label})")
            
            # Show reasoning if available
            reason = reason_map.get(result["document_id"], "")
            if reason:
                st.markdown("#### 📝 Relevance Justification")
                st.info(reason)

def render_comparison_screen(data: Dict):
    """Screen 3: Ranking vs Coverage Comparison."""
    st.header("📐 Ranking Quality vs Coverage Analysis")
    
    st.info("""
    **Understanding the Golden Dataset:**
    
    - **Query Relevance (Coverage):** Focuses on ensuring comprehensive recall, including 
      long-tail results (relevance=1) that may be tangentially relevant.
    
    - **Ranking Quality:** Emphasizes precision at top ranks, ensuring the most relevant 
      items (relevance=3) appear first.
    
    This view helps you understand the balance between broad coverage and strict ranking quality.
    """)
    
    st.divider()
    
    # View toggle
    view_mode = st.radio(
        "Select View:",
        ["Coverage Analysis", "Ranking Quality", "Side-by-Side Comparison"],
        horizontal=True
    )
    
    if view_mode == "Coverage Analysis":
        st.subheader("Coverage Analysis (Long-Tail Inclusion)")
        
        for result_set in data["expected_results"]["results"]:
            query_text = result_set["query"]
            
            with st.expander(f"📋 {query_text}"):
                total_results = len(result_set["expected_results"])
                
                # Count by relevance
                rel_counts = Counter(r["relevance_score"] for r in result_set["expected_results"])
                
                st.write(f"**Total Results:** {total_results}")
                st.write(f"- Highly Relevant (3): {rel_counts.get(3, 0)}")
                st.write(f"- Moderately Relevant (2): {rel_counts.get(2, 0)}")
                st.write(f"- Weakly Relevant (1): {rel_counts.get(1, 0)}")
                
                # Show tail results (relevance=1)
                tail_results = [r for r in result_set["expected_results"] if r["relevance_score"] == 1]
                
                if tail_results:
                    st.write(f"\n**Long-Tail Results ({len(tail_results)} items):**")
                    tail_df = pd.DataFrame([
                        {
                            "Rank": r["rank"],
                            "Title": r["document_title"],
                            "Category": r["category"],
                            "ID": r["document_id"]
                        }
                        for r in tail_results
                    ])
                    st.dataframe(tail_df, hide_index=True, use_container_width=True)
    
    elif view_mode == "Ranking Quality":
        st.subheader("Ranking Quality (Top-Rank Precision)")
        
        for result_set in data["expected_results"]["results"]:
            query_text = result_set["query"]
            
            with st.expander(f"📋 {query_text}"):
                # Focus on top 10 results
                top_10 = result_set["expected_results"][:10]
                
                st.write("**Top 10 Results Analysis:**")
                
                top_10_df = pd.DataFrame([
                    {
                        "Rank": r["rank"],
                        "Title": r["document_title"],
                        "Category": r["category"],
                        "Relevance": r["relevance_score"],
                        "Quality": "✅ High" if r["relevance_score"] == 3 else ("⚠️ Medium" if r["relevance_score"] == 2 else "❌ Low")
                    }
                    for r in top_10
                ])
                
                st.dataframe(top_10_df, hide_index=True, use_container_width=True)
                
                # Quality metrics
                high_rel_count = sum(1 for r in top_10 if r["relevance_score"] == 3)
                st.metric("High Relevance in Top 10", f"{high_rel_count}/10")
    
    else:  # Side-by-Side Comparison
        st.subheader("Side-by-Side: Top Ranks vs Full Coverage")
        
        for result_set in data["expected_results"]["results"]:
            query_text = result_set["query"]
            
            with st.expander(f"📋 {query_text}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**🎯 Top 5 (Strict Ranking)**")
                    top_5 = result_set["expected_results"][:5]
                    
                    for r in top_5:
                        emoji = "🟢" if r["relevance_score"] == 3 else ("🟡" if r["relevance_score"] == 2 else "⚪")
                        st.write(f"{r['rank']}. {emoji} {r['document_title']} ({r['relevance_score']}/3)")
                
                with col2:
                    st.write("**📊 Coverage Summary**")
                    total = len(result_set["expected_results"])
                    rel_counts = Counter(r["relevance_score"] for r in result_set["expected_results"])
                    
                    st.write(f"Total items: {total}")
                    st.write(f"• High (3): {rel_counts.get(3, 0)}")
                    st.write(f"• Medium (2): {rel_counts.get(2, 0)}")
                    st.write(f"• Low (1): {rel_counts.get(1, 0)}")

def render_filters_analysis_screen(data: Dict):
    """Screen 4: Filters & Analysis."""
    st.header("🔬 Filters & Analysis")
    
    # Filters section
    st.subheader("Filters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category filter
        all_categories = set()
        for result_set in data["expected_results"]["results"]:
            for item in result_set["expected_results"]:
                all_categories.add(item["category"])
        
        selected_categories = st.multiselect(
            "Filter by Category:",
            options=sorted(all_categories),
            default=sorted(all_categories)
        )
    
    with col2:
        # Relevance filter
        selected_relevance = st.multiselect(
            "Filter by Relevance Score:",
            options=[3, 2, 1],
            default=[3, 2, 1],
            format_func=lambda x: f"{x} - {'High' if x == 3 else ('Medium' if x == 2 else 'Low')}"
        )
    
    st.divider()
    
    # Apply filters and build filtered dataset
    filtered_results = []
    
    for result_set in data["expected_results"]["results"]:
        query_id = result_set["query_id"]
        query_text = result_set["query"]
        
        for item in result_set["expected_results"]:
            if (item["category"] in selected_categories and 
                item["relevance_score"] in selected_relevance):
                
                filtered_results.append({
                    "Query ID": query_id,
                    "Query": query_text,
                    "Rank": item["rank"],
                    "Document Title": item["document_title"],
                    "Document ID": item["document_id"],
                    "Category": item["category"],
                    "Relevance": item["relevance_score"]
                })
    
    # Display filtered results
    st.subheader(f"Filtered Results ({len(filtered_results)} items)")
    
    if filtered_results:
        df = pd.DataFrame(filtered_results)
        
        # Add color coding with better contrast
        def color_relevance(val):
            if val == 3:
                return 'background-color: #d4edda; color: #155724; font-weight: bold'
            elif val == 2:
                return 'background-color: #fff3cd; color: #856404; font-weight: bold'
            else:
                return 'background-color: #e2e3e5; color: #383d41; font-weight: bold'
        
        styled_df = df.style.applymap(color_relevance, subset=['Relevance'])
        st.dataframe(styled_df, hide_index=True, use_container_width=True)
        
        st.divider()
        
        # Quick insights
        st.subheader("📊 Quick Insights")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            weak_matches = len([r for r in filtered_results if r["Relevance"] == 1])
            st.metric("Weak Matches (1)", weak_matches)
        
        with col2:
            medium_matches = len([r for r in filtered_results if r["Relevance"] == 2])
            st.metric("Medium Matches (2)", medium_matches)
        
        with col3:
            high_matches = len([r for r in filtered_results if r["Relevance"] == 3])
            st.metric("High Matches (3)", high_matches)
        
        with col4:
            avg_relevance = sum(r["Relevance"] for r in filtered_results) / len(filtered_results)
            st.metric("Avg Relevance", f"{avg_relevance:.2f}")
        
        # Distribution analysis
        st.divider()
        st.subheader("Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**By Category:**")
            cat_counts = Counter(r["Category"] for r in filtered_results)
            cat_df = pd.DataFrame([
                {"Category": cat, "Count": count}
                for cat, count in cat_counts.most_common()
            ])
            st.dataframe(cat_df, hide_index=True, use_container_width=True)
        
        with col2:
            st.write("**By Query:**")
            query_counts = Counter(r["Query ID"] for r in filtered_results)
            query_df = pd.DataFrame([
                {"Query ID": qid, "Results": count}
                for qid, count in query_counts.most_common()
            ])
            st.dataframe(query_df, hide_index=True, use_container_width=True)
        
        # Labeling insights
        st.divider()
        st.subheader("📝 Labeling Quality Assessment")
        
        total_judgments = data["metadata"]["total_judgments"]
        high_count = len([r for r in filtered_results if r["Relevance"] == 3])
        low_count = len([r for r in filtered_results if r["Relevance"] == 1])
        
        high_percentage = (high_count / total_judgments) * 100
        low_percentage = (low_count / total_judgments) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("High Relevance %", f"{high_percentage:.1f}%")
            if high_percentage < 30:
                st.warning("⚠️ Low proportion of highly relevant items. Consider if labeling is too strict.")
            elif high_percentage > 60:
                st.info("ℹ️ High proportion of highly relevant items. Ensure quality standards are maintained.")
        
        with col2:
            st.metric("Weak Relevance %", f"{low_percentage:.1f}%")
            if low_percentage > 50:
                st.warning("⚠️ High proportion of weak matches. Consider if coverage is too broad.")
            elif low_percentage < 20:
                st.info("ℹ️ Good precision. Most results are relevant.")
    
    else:
        st.info("No results match the selected filters.")

# ============================================================================
# Main Application
# ============================================================================

def main():
    st.set_page_config(
        page_title="Golden Dataset Viewer",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load data
    data = load_golden_data()
    
    if data is None:
        st.error("Failed to load golden dataset. Please check the file paths.")
        st.stop()
    
    # Render header
    render_header()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.info("Select a view to inspect the golden dataset")
    
    screen = st.sidebar.radio(
        "Choose Screen:",
        [
            "📊 Overview",
            "🔎 Query-Level View",
            "📐 Ranking vs Coverage",
            "🔬 Filters & Analysis"
        ]
    )
    
    st.sidebar.divider()
    
    # Dataset info in sidebar
    st.sidebar.subheader("Dataset Info")
    st.sidebar.write(f"**Version:** {data['metadata']['version']}")
    st.sidebar.write(f"**Queries:** {data['metadata']['total_queries']}")
    st.sidebar.write(f"**Judgments:** {data['metadata']['total_judgments']}")
    st.sidebar.write(f"**Updated:** {data['metadata']['last_updated']}")
    
    # Render selected screen
    if screen == "📊 Overview":
        render_overview_screen(data)
    
    elif screen == "🔎 Query-Level View":
        render_query_view_screen(data)
    
    elif screen == "📐 Ranking vs Coverage":
        render_comparison_screen(data)
    
    elif screen == "🔬 Filters & Analysis":
        render_filters_analysis_screen(data)

if __name__ == "__main__":
    main()
