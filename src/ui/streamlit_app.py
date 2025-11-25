"""
Streamlit UI for Semantic Search System
Web interface for searching across tools, services, courses, and case studies
"""

import streamlit as st
from src.core.search_engine import SemanticSearcher, get_git_commit_hash


@st.cache_resource
def initialize_searcher() -> SemanticSearcher:
    """Initialize and cache the SemanticSearcher resource."""
    return SemanticSearcher()


def main() -> None:
    """Streamlit app entry point."""
    st.set_page_config(
        page_title="Hybrid Search System",
        page_icon="🔎",
        layout="wide"
    )

    st.title("🔎 Hybrid Search System")
    st.markdown("### Search across tools, service providers, training courses, and case studies")
    st.markdown("*🤖 Powered by **Semantic Search (70%) + TF-IDF Keyword Matching (30%)**  for the best results*")

    # Initialize searcher and handle missing data
    try:
        searcher = initialize_searcher()
    except FileNotFoundError as e:
        st.error(f"⚠️ {e}")
        return

    query = st.text_input("Enter your search query:", placeholder="e.g. best AI tools, learn python, find a vendor, digital transformation case study")
    if query:
        if len(query.strip()) < 3:
            st.warning("Please enter a longer search query.")
        else:
            with st.spinner("🔍 Searching..."):
                results, detected_category = searcher.search(query, k=20, min_score=0.3)
                
                # Show search results grouped by semantic relevance
                st.info("🌐 **All Categories**: Results organized by semantic relevance")
                if results:
                    for i, res in enumerate(results, start=1):
                        header = ' | '.join(res['metadata'].get('values', []))
                        source_sheet = res['metadata'].get('sheet', 'Unknown')
                        
                        # Generate URL for this result
                        result_url = searcher._generate_result_url(res)
                        
                        # Determine category type and display info based on source
                        if "case-studies" in source_sheet.lower():
                            category_type = "CASE STUDY"
                            source_emoji = "📋"
                            # For case studies, use the clean title as header
                            case_study_title = res['metadata'].get('values', ['Unknown'])[0]
                            # Clean up the title display
                            clean_title = case_study_title.replace('- ', '').split('(')[0].strip()
                            display_header = clean_title
                        elif "tools" in source_sheet.lower() or "cleaned sheet" in source_sheet.lower():
                            category_type = "TOOL"
                            source_emoji = "🛠️"
                            # For tools, use the tool name (index 2)
                            values = res['metadata'].get('values', [])
                            display_header = values[2] if len(values) >= 3 else header
                        elif "training" in source_sheet.lower():
                            category_type = "COURSE"
                            source_emoji = "📚"
                            # For courses, use the course title (index 2)
                            values = res['metadata'].get('values', [])
                            display_header = values[2] if len(values) >= 3 else header
                        else:
                            category_type = "SERVICE PROVIDER"
                            source_emoji = "🏢"
                            # For service providers, use the provider name (index 0)
                            values = res['metadata'].get('values', [])
                            display_header = values[0] if len(values) >= 1 else header
                        
                        # Create clickable title with hyperlink
                        clickable_title = f"[{display_header}]({result_url})"
                        
                        # Handle case studies display
                        if "case-studies" in source_sheet.lower():
                            case_study_title = res['metadata'].get('values', ['Unknown'])[0]
                            industry = res['metadata'].get('industry', 'Unknown')
                            problem_type = res['metadata'].get('problem_type', 'Unknown')
                            word_count = res['metadata'].get('word_count', 0)
                            
                            with st.expander(f"{source_emoji} {category_type}: {display_header} (Score: {res['score']:.3f})"):
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.markdown("#### Case Study Details")
                                    st.markdown(f"**Title:** {clickable_title}")
                                    st.write(f"**Industry:** {industry}")
                                    st.write(f"**Problem Type:** {problem_type}")
                                
                                with col2:
                                    st.markdown("#### Relevance Scores")
                                    st.progress(res['score'])
                                    st.write(f"**Hybrid Score:** {res['score']:.3f}")
                                    st.write(f"🧠 Semantic: {res['semantic_score']:.3f} (70%)")
                                    st.write(f"🔍 TF-IDF: {res['tfidf_score']:.3f} (30%)")
                        else:
                            # Display for tools, courses, and service providers
                            with st.expander(f"{source_emoji} {category_type}: {display_header} (Score: {res['score']:.3f})"):
                                detail_col, score_col = st.columns([2, 1])
                                with detail_col:
                                    st.markdown("#### Details")
                                    st.markdown(f"**Title:** {clickable_title}")
                                    
                                    # Display remaining details based on category
                                    if "cleaned sheet" in source_sheet.lower():  # Tools
                                        values = res['metadata'].get('values', [])
                                        if len(values) >= 2:
                                            st.write(f"**Category:** {values[0]}")
                                            st.write(f"**Sub-Category:** {values[1]}")
                                    elif "service provider profiles" in source_sheet.lower():  # Service Providers
                                        # Only show the provider name as title, no additional details needed
                                        pass
                                    elif "training program" in source_sheet.lower():  # Courses
                                        values = res['metadata'].get('values', [])
                                        if len(values) >= 2:
                                            st.write(f"**Skill:** {values[0]}")
                                            st.write(f"**Topic:** {values[1]}")
                                    
                                    st.write(f"**Source:** {source_emoji} {source_sheet}")
                                with score_col:
                                    st.markdown("#### Relevance Scores")
                                    st.progress(res['score'])
                                    st.write(f"**Hybrid Score:** {res['score']:.3f}")
                                    st.write(f"🧠 Semantic: {res['semantic_score']:.3f} (70%)")
                                    st.write(f"🔍 TF-IDF: {res['tfidf_score']:.3f} (30%)")
                else:
                    st.info(f"No results found for your query. Try different search terms or be more specific.")

    with st.sidebar:
        st.markdown("### About")
        
        st.write(f"""
        🤖 **Hybrid AI Search** combining:
        - **70% Semantic Search**: Understanding context and meaning
        - **30% TF-IDF Keyword**: Exact keyword matching
        - **Smart Category Stacking**: Results organized by semantic relevance
        
        All categories are searched and results are dynamically stacked based on semantic similarity scores.
        """)
        
        st.markdown("### Debug Info")
        commit_hash = get_git_commit_hash()
        st.code(f"Commit: {commit_hash}")
        st.write(f"**Python Version:** {st.__version__}")
        
        st.markdown("### Search Tips")
        st.write("""
        - **Specific terms**: Use exact keywords for better TF-IDF matching
        - **Concepts**: Use descriptive phrases for better semantic matching
        - **Best results**: Combine both approaches in your query
        """)


if __name__ == "__main__":
    main()
