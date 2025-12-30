"""
Golden Dataset Viewer UI - Streamlit application to view and explore the golden evaluation dataset
"""

import streamlit as st
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Golden Dataset Viewer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Golden Dataset Viewer")
st.markdown("View and explore the golden evaluation dataset for search quality assessment")

# Load golden dataset files
golden_dir = Path("search-evaluation-goldens/goldens/v1")

@st.cache_data
def load_golden_data():
    """Load all golden dataset files"""
    data = {}
    
    try:
        # Load queries
        queries_file = golden_dir / "queries.json"
        if queries_file.exists():
            with open(queries_file, 'r', encoding='utf-8') as f:
                data['queries'] = json.load(f)
        
        # Load expected results
        expected_file = golden_dir / "expected_results.json"
        if expected_file.exists():
            with open(expected_file, 'r', encoding='utf-8') as f:
                data['expected_results'] = json.load(f)
        
        # Load relevance judgments
        relevance_file = golden_dir / "relevance_judgments.json"
        if relevance_file.exists():
            with open(relevance_file, 'r', encoding='utf-8') as f:
                data['relevance_judgments'] = json.load(f)
        
        # Load metadata
        metadata_file = golden_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data['metadata'] = json.load(f)
        
        return data
    except Exception as e:
        st.error(f"Error loading golden dataset: {e}")
        return {}

# Load data
golden_data = load_golden_data()

if not golden_data:
    st.error("❌ Golden dataset not found. Please ensure the dataset exists in search-evaluation-goldens/goldens/v1/")
    st.stop()

# Display metadata
if 'metadata' in golden_data:
    metadata = golden_data['metadata']
    st.sidebar.markdown("### Dataset Information")
    st.sidebar.info(f"""
    **Version:** {metadata.get('version', 'N/A')}  
    **Created:** {metadata.get('created_date', 'N/A')}  
    **Total Queries:** {metadata.get('total_queries', 'N/A')}  
    **Relevance Scale:** {metadata.get('relevance_scale', 'N/A')}
    """)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Queries", "🎯 Relevance Judgments", "📋 Expected Results", "📊 Statistics"])

# Tab 1: Queries
with tab1:
    st.header("Query List")
    
    if 'queries' in golden_data:
        queries_data = golden_data['queries']
        
        if 'queries' in queries_data:
            queries_list = queries_data['queries']
            st.write(f"**Total Queries:** {len(queries_list)}")
            
            # Search/filter
            search_term = st.text_input("🔍 Search queries", "")
            
            # Display queries
            for i, query in enumerate(queries_list, 1):
                query_id = query.get('id') or query.get('query_id', f'q{i:03d}')
                query_text = query.get('query', '')
                
                if search_term.lower() in query_text.lower() or search_term.lower() in query_id.lower() or not search_term:
                    with st.expander(f"**{query_id}:** {query_text}"):
                        st.json(query)

# Tab 2: Relevance Judgments
with tab2:
    st.header("Relevance Judgments")
    
    if 'relevance_judgments' in golden_data:
        judgments_data = golden_data['relevance_judgments']
        
        if 'judgments' in judgments_data:
            judgments = judgments_data['judgments']
            st.write(f"**Total Judgments:** {len(judgments)}")
            
            # Query selector
            query_ids = [j.get('query_id', '') for j in judgments]
            selected_query = st.selectbox("Select Query", query_ids)
            
            # Display selected query's judgments
            for judgment in judgments:
                if judgment.get('query_id') == selected_query:
                    st.markdown(f"### Query: {judgment.get('query', '')}")
                    
                    results = judgment.get('results', [])
                    st.write(f"**Total Results:** {len(results)}")
                    
                    # Create table
                    if results:
                        st.markdown("#### Relevance Judgments")
                        
                        for idx, result in enumerate(results, 1):
                            doc_id = result.get('id', '')
                            title = result.get('title', '')
                            category = result.get('category', '')
                            relevance = result.get('relevance_score', 0)
                            reason = result.get('reason', '')
                            
                            # Color code by relevance
                            if relevance == 3:
                                color = "🟢"
                            elif relevance == 2:
                                color = "🟡"
                            elif relevance == 1:
                                color = "🟠"
                            else:
                                color = "⚪"
                            
                            with st.expander(f"{color} [{idx}] {title} (Score: {relevance})"):
                                st.markdown(f"""
                                - **Document ID:** {doc_id}
                                - **Category:** {category}
                                - **Relevance Score:** {relevance}/3
                                - **Reason:** {reason}
                                """)

# Tab 3: Expected Results
with tab3:
    st.header("Expected Results")
    
    if 'expected_results' in golden_data:
        expected_data = golden_data['expected_results']
        
        if 'expected_results' in expected_data:
            expected_list = expected_data['expected_results']
            st.write(f"**Total Queries with Expected Results:** {len(expected_list)}")
            
            # Query selector
            query_ids = [e.get('query_id', '') for e in expected_list]
            selected_query = st.selectbox("Select Query to View Expected Results", query_ids, key="expected_selector")
            
            # Display selected query's expected results
            for expected in expected_list:
                if expected.get('query_id') == selected_query:
                    st.markdown(f"### Query: {expected.get('query', '')}")
                    
                    results = expected.get('expected_results', [])
                    st.write(f"**Expected Results:** {len(results)}")
                    
                    # Display in table format
                    if results:
                        table_data = []
                        for idx, result in enumerate(results, 1):
                            table_data.append({
                                'Rank': idx,
                                'Document ID': result.get('id', ''),
                                'Title': result.get('title', ''),
                                'Category': result.get('category', ''),
                                'Relevance': result.get('relevance_score', 0)
                            })
                        
                        st.dataframe(table_data, use_container_width=True, hide_index=True)

# Tab 4: Statistics
with tab4:
    st.header("Dataset Statistics")
    
    if 'relevance_judgments' in golden_data and 'judgments' in golden_data['relevance_judgments']:
        judgments = golden_data['relevance_judgments']['judgments']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Queries", len(judgments))
        
        with col2:
            total_judgments = sum(len(j.get('results', [])) for j in judgments)
            st.metric("Total Judgments", total_judgments)
        
        with col3:
            avg_judgments = total_judgments / len(judgments) if judgments else 0
            st.metric("Avg Judgments/Query", f"{avg_judgments:.1f}")
        
        # Relevance score distribution
        st.markdown("### Relevance Score Distribution")
        
        score_counts = {1: 0, 2: 0, 3: 0}
        for judgment in judgments:
            for result in judgment.get('results', []):
                score = result.get('relevance_score', 0)
                if score in score_counts:
                    score_counts[score] += 1
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🟠 Score 1 (Relevant)", score_counts[1])
        
        with col2:
            st.metric("🟡 Score 2 (Highly Relevant)", score_counts[2])
        
        with col3:
            st.metric("🟢 Score 3 (Perfect Match)", score_counts[3])
        
        # Category distribution
        st.markdown("### Category Distribution")
        
        category_counts = {}
        for judgment in judgments:
            for result in judgment.get('results', []):
                category = result.get('category', 'unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts:
            st.bar_chart(category_counts)

st.markdown("---")
st.caption("Golden Dataset Viewer | Search Evaluation System")
