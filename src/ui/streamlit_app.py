"""
Streamlit UI for Semantic Search System
Web interface for searching across tools, services, courses, and case studies
"""

import streamlit as st
from src.core.search_engine import SemanticSearcher, get_git_commit_hash
from src.core.evaluation import SearchEvaluator


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
                        
                        # Get URL from metadata (API provides this directly)
                        result_url = res['metadata'].get('url', 'https://dt4si.com/')
                        
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

    # ========================================================================
    # SEARCH EVALUATION SECTION
    # ========================================================================
    st.markdown("---")
    st.markdown("## 📊 Search Evaluation")
    st.markdown("Evaluate search system performance using the golden dataset (42 test queries with 1-3 relevance scale)")
    
    # Create columns for button and info
    eval_col1, eval_col2 = st.columns([1, 2])
    
    with eval_col1:
        if st.button("🔄 Recalculate Search Accuracy", type="primary", use_container_width=True):
            # Store flag to trigger evaluation
            st.session_state.run_evaluation = True
    
    with eval_col2:
        st.info("Click to run all 42 evaluation queries and compute metrics")
    
    # Run evaluation if button was clicked
    if st.session_state.get('run_evaluation', False):
        st.markdown("---")
        
        # Create placeholder for progress updates
        progress_container = st.empty()
        status_container = st.empty()
        
        try:
            # Show initial progress
            with status_container:
                st.info("🔄 Initializing evaluation system...")
            
            # Initialize evaluator
            evaluator = SearchEvaluator()
            
            with status_container:
                st.info("✅ Evaluator initialized. Starting query evaluation...")
            
            # Create progress bar
            progress_bar = progress_container.progress(0)
            
            # Run evaluation with progress updates
            results_list = []
            total_queries = len(evaluator.queries)
            
            for i, query_data in enumerate(evaluator.queries, 1):
                # Flexible handling of query ID
                query_id = query_data.get('id') or query_data.get('query_id', f'q{i:03d}')
                query_text = query_data.get('query', '')
                
                # Update progress
                progress_percentage = (i - 1) / total_queries
                progress_bar.progress(progress_percentage)
                
                with status_container:
                    st.info(f"🔍 Evaluating query {i}/{total_queries}: \"{query_text[:50]}...\"")
                
                # Evaluate query
                result = evaluator.evaluate_query(query_text, query_id, searcher, k=5)
                
                # Add query_id and query_text to result
                result['query_id'] = query_id
                result['query_text'] = query_text
                
                results_list.append(result)
                
                # Print to terminal (verbose logging with debug info)
                print(f"[{i}/{total_queries}] {query_id}: P@5={result['precision_at_k']:.3f}, R@5={result['recall_at_k']:.3f}, NDCG@5={result['ndcg_at_k']:.3f} | Retrieved={result['retrieved_count']}, Matched={result.get('matched_count', 0)}/{result['relevant_count']}")
            
            # Complete progress
            progress_bar.progress(1.0)
            
            with status_container:
                st.info("📊 Calculating aggregated metrics...")
            
            # Calculate aggregated metrics
            mean_precision = sum(r['precision_at_k'] for r in results_list) / len(results_list)
            mean_recall = sum(r['recall_at_k'] for r in results_list) / len(results_list)
            mean_ndcg = sum(r['ndcg_at_k'] for r in results_list) / len(results_list)
            final_accuracy = (0.5 * mean_ndcg) + (0.25 * mean_precision) + (0.25 * mean_recall)
            
            results = {
                'total_queries': len(results_list),
                'k': 5,
                'mean_precision_at_k': mean_precision,
                'mean_recall_at_k': mean_recall,
                'mean_ndcg_at_k': mean_ndcg,
                'final_accuracy_score': final_accuracy,
                'per_query_results': results_list
            }
            
            # Store results in session state
            st.session_state.evaluation_results = results
            st.session_state.run_evaluation = False  # Reset flag
            
            # Clear progress displays
            progress_container.empty()
            status_container.empty()
            
            # Show success message
            st.success("✅ Evaluation completed successfully!")
            
            # Print summary to terminal
            print("\n" + "="*80)
            print("EVALUATION COMPLETE")
            print("="*80)
            print(f"Final Accuracy: {final_accuracy:.4f} ({final_accuracy*100:.2f}%)")
            print(f"Precision@5:    {mean_precision:.4f} ({mean_precision*100:.2f}%)")
            print(f"Recall@5:       {mean_recall:.4f} ({mean_recall*100:.2f}%)")
            print(f"NDCG@5:         {mean_ndcg:.4f} ({mean_ndcg*100:.2f}%)")
            print("="*80 + "\n")
            
        except Exception as e:
            # Clear progress displays
            progress_container.empty()
            status_container.empty()
            
            st.error(f"❌ Evaluation failed: {str(e)}")
            st.exception(e)
            st.session_state.run_evaluation = False
            
            # Print error to terminal
            import traceback
            print("\n" + "="*80)
            print("EVALUATION ERROR")
            print("="*80)
            traceback.print_exc()
            print("="*80 + "\n")
    
    # Display results if available
    if st.session_state.get('evaluation_results'):
        results = st.session_state.evaluation_results
        
        st.markdown("### 🎯 Evaluation Results")
        
        # Display final accuracy prominently
        final_accuracy = results['final_accuracy_score']
        st.markdown(f"#### 🏆 **Final Accuracy Score: {final_accuracy:.4f}** ({final_accuracy*100:.2f}%)")
        
        # Display formula
        with st.expander("📐 Formula Details"):
            st.markdown(f"""
            **Final Accuracy = 0.5 × NDCG@5 + 0.25 × Precision@5 + 0.25 × Recall@5**
            
            - 0.5 × {results['mean_ndcg_at_k']:.4f} (NDCG@5)
            - 0.25 × {results['mean_precision_at_k']:.4f} (Precision@5)
            - 0.25 × {results['mean_recall_at_k']:.4f} (Recall@5)
            - **= {final_accuracy:.4f}**
            """)
        
        # Create metrics columns
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric(
                label="📊 Mean Precision@5",
                value=f"{results['mean_precision_at_k']:.4f}",
                delta=f"{results['mean_precision_at_k']*100:.2f}%"
            )
        
        with metric_col2:
            st.metric(
                label="📊 Mean Recall@5",
                value=f"{results['mean_recall_at_k']:.4f}",
                delta=f"{results['mean_recall_at_k']*100:.2f}%"
            )
        
        with metric_col3:
            st.metric(
                label="📊 Mean NDCG@5",
                value=f"{results['mean_ndcg_at_k']:.4f}",
                delta=f"{results['mean_ndcg_at_k']*100:.2f}%"
            )
        
        # Add progress bars for visual representation
        st.markdown("#### 📈 Metric Visualization")
        
        progress_col1, progress_col2 = st.columns(2)
        
        with progress_col1:
            st.markdown("**Precision@5**")
            st.progress(results['mean_precision_at_k'])
            
            st.markdown("**Recall@5**")
            st.progress(results['mean_recall_at_k'])
        
        with progress_col2:
            st.markdown("**NDCG@5**")
            st.progress(results['mean_ndcg_at_k'])
            
            st.markdown("**Final Accuracy**")
            st.progress(final_accuracy)
        
        # Show per-query results in expander
        with st.expander(f"📋 Per-Query Results ({results['total_queries']} queries)"):
            st.markdown("Detailed metrics for each evaluation query:")
            
            # Create a table of results
            query_data = []
            for qr in results['per_query_results']:
                # Get query text with fallback
                query_text = qr.get('query_text', '') or qr.get('query', '') or 'N/A'
                query_display = (query_text[:50] + '...') if len(query_text) > 50 else query_text
                
                # Get query ID with fallback
                query_id = qr.get('query_id', '') or 'N/A'
                
                query_data.append({
                    'Query ID': query_id,
                    'Query': query_display,
                    'Precision@5': f"{qr.get('precision_at_k', 0.0):.4f}",
                    'Recall@5': f"{qr.get('recall_at_k', 0.0):.4f}",
                    'NDCG@5': f"{qr.get('ndcg_at_k', 0.0):.4f}",
                    'Retrieved': qr.get('retrieved_count', 0),
                    'Matched': qr.get('matched_count', 0),
                    'Relevant': qr.get('relevant_count', 0)
                })
            
            st.dataframe(query_data, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.info(f"✅ Evaluated {results['total_queries']} queries with K={results['k']}")

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
