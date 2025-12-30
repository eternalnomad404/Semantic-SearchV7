"""
Search Evaluation System for Semantic Search
Evaluates search performance using golden dataset with Precision@10, Recall@10, NDCG@10
"""

import json
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple
from src.core.search_engine import SemanticSearcher


class SearchEvaluator:
    """
    Evaluates search system performance using a golden dataset.
    
    Calculates:
    - Precision@K: Proportion of relevant documents in top K results
    - Recall@K: Proportion of all relevant documents found in top K results  
    - NDCG@K: Normalized Discounted Cumulative Gain (ranking quality)
    - Final Accuracy: Weighted combination of above metrics
    
    Golden dataset format:
    - queries.json: Test queries with IDs
    - relevance_judgments.json: Document relevance scores (1-10 scale)
    """
    
    def __init__(self, golden_data_path: str = "search-evaluation-goldens/goldens/v1"):
        """
        Initialize evaluator with golden dataset.
        
        Args:
            golden_data_path: Path to golden dataset folder containing:
                - queries.json
                - relevance_judgments.json
        """
        self.golden_data_path = Path(golden_data_path)
        self.queries, self.relevance_judgments = self.load_golden_dataset()
        self.slug_to_id_map = self._build_slug_to_id_map()
        self.title_to_id_map = self._build_title_to_id_map()
        
    def _build_title_to_id_map(self) -> Dict[str, str]:
        """
        Build mapping from document titles to golden dataset IDs.
        
        Returns:
            Dictionary mapping titles (lowercase) to document IDs
        """
        title_map = {}
        
        for query_id, judgment in self.relevance_judgments.items():
            results = judgment.get('results', [])
            for result in results:
                doc_id = result.get('id', '')
                title = result.get('title', '')
                
                if doc_id and title:
                    # Map lowercase title to ID
                    title_lower = title.lower().strip()
                    title_map[title_lower] = doc_id
                    
                    # Also map simplified version (remove special chars)
                    title_simple = title_lower.replace('-', ' ').replace('_', ' ')
                    title_map[title_simple] = doc_id
        
        return title_map
        
    def load_golden_dataset(self) -> Tuple[List[Dict], Dict]:
        """
        Load golden dataset files.
        
        Returns:
            Tuple of (queries list, relevance_judgments dict)
        """
        # Load queries
        queries_file = self.golden_data_path / "queries.json"
        with open(queries_file, 'r', encoding='utf-8') as f:
            queries_data = json.load(f)
            queries = queries_data.get('queries', [])
        
        # Load relevance judgments
        judgments_file = self.golden_data_path / "relevance_judgments.json"
        with open(judgments_file, 'r', encoding='utf-8') as f:
            judgments_data = json.load(f)
            judgments = judgments_data.get('judgments', [])
        
        # Build dict for easier lookup
        relevance_dict = {}
        for judgment in judgments:
            query_id = judgment.get('query_id')
            if query_id:
                relevance_dict[query_id] = judgment
        
        return queries, relevance_dict
    
    def _build_slug_to_id_map(self) -> Dict[str, str]:
        """
        Build mapping from document slugs/titles to document IDs.
        
        Returns:
            Dictionary mapping slugified titles to document IDs
        """
        slug_map = {}
        
        for query_id, judgment in self.relevance_judgments.items():
            results = judgment.get('results', [])
            for result in results:
                doc_id = result.get('id', '')
                title = result.get('title', '')
                
                if doc_id and title:
                    # Create slug from title (lowercase, spaces to underscores)
                    slug = title.lower().replace(' ', '_').replace('-', '_')
                    slug_map[slug] = doc_id
                    slug_map[title.lower()] = doc_id
                    slug_map[doc_id] = doc_id  # Also map ID to itself
        
        return slug_map
    
    def _match_result_to_golden(self, result: Dict, query_id: str) -> str:
        """
        Match a search result to a golden dataset document ID.
        
        Args:
            result: Search result dictionary
            query_id: Query ID for context
            
        Returns:
            Matched document ID or empty string if no match
        """
        # Try to get document ID from result metadata
        metadata = result.get('metadata', {})
        
        # Get judgment data for this query
        judgment = self.relevance_judgments.get(query_id, {})
        golden_results = judgment.get('results', [])
        
        # Extract values for matching
        values = metadata.get('values', [])
        sheet = metadata.get('sheet', '').lower()
        slug = metadata.get('slug', '')
        
        # Determine category and title based on sheet type
        if 'case' in sheet and 'stud' in sheet:
            category = 'case_study'
            title = values[0] if len(values) > 0 else ''
        elif 'cleaned sheet' in sheet or 'tool' in sheet:
            category = 'tool'
            title = values[2] if len(values) >= 3 else ''
        elif 'training' in sheet or 'course' in sheet:
            category = 'course'
            title = values[2] if len(values) >= 3 else ''
        elif 'service provider' in sheet:
            category = 'service_provider'
            title = values[0] if len(values) > 0 else ''
        else:
            category = ''
            title = values[0] if len(values) > 0 else ''
        
        # Method 1: Try exact title match using the title_to_id_map
        if title:
            title_lower = title.lower().strip()
            if title_lower in self.title_to_id_map:
                matched_id = self.title_to_id_map[title_lower]
                # Verify it's in this query's golden set
                if any(gr.get('id') == matched_id for gr in golden_results):
                    return matched_id
        
        # Method 2: Try slug-based matching
        if slug:
            # Check if any golden result has a matching title derived from slug
            slug_title = slug.replace('-', ' ').replace('_', ' ').lower().strip()
            for gr in golden_results:
                golden_title = gr.get('title', '').lower().strip()
                golden_simple = golden_title.replace('-', ' ').replace('_', ' ')
                if slug_title == golden_simple or slug_title in golden_simple or golden_simple in slug_title:
                    return gr.get('id', '')
        
        # Method 3: Fuzzy title matching against this query's golden results
        if title:
            title_lower = title.lower().strip()
            title_simple = title_lower.replace('-', ' ').replace('_', ' ')
            
            for gr in golden_results:
                golden_title = gr.get('title', '').lower().strip()
                golden_simple = golden_title.replace('-', ' ').replace('_', ' ')
                
                # Exact match
                if title_lower == golden_title:
                    return gr.get('id', '')
                
                # Simplified match
                if title_simple == golden_simple:
                    return gr.get('id', '')
                
                # Substring match (either direction)
                if title_simple in golden_simple or golden_simple in title_simple:
                    return gr.get('id', '')
        
        return ""
    
    def calculate_precision_at_k(self, relevant_ids: set, retrieved_ids: List[str], k: int) -> float:
        """
        Calculate Precision@K.
        
        Precision@K = (# of relevant docs in top K) / K
        
        Args:
            relevant_ids: Set of relevant document IDs
            retrieved_ids: List of retrieved document IDs (ordered by rank), may contain "" for non-matches
            k: Cutoff position
            
        Returns:
            Precision@K score (0.0 to 1.0)
        """
        if k == 0:
            return 0.0
        
        # Take only top K results
        top_k = retrieved_ids[:k]
        
        # Count how many are relevant (ignore empty strings)
        relevant_count = sum(1 for doc_id in top_k if doc_id and doc_id in relevant_ids)
        
        # CRITICAL: Always divide by K, not by len(top_k)
        return relevant_count / k
    
    def calculate_recall_at_k(self, relevant_ids: set, retrieved_ids: List[str], k: int) -> float:
        """
        Calculate Recall@K.
        
        Recall@K = (# of relevant docs in top K) / (total # of relevant docs in golden dataset)
        
        CRITICAL: The denominator is ALWAYS the total relevant documents in the golden truth,
        NOT the number of retrieved documents, NOT K itself.
        
        Args:
            relevant_ids: Set of ALL relevant document IDs from golden dataset
            retrieved_ids: List of retrieved document IDs (ordered by rank), may contain "" for non-matches
            k: Cutoff position
            
        Returns:
            Recall@K score (0.0 to 1.0)
        """
        if len(relevant_ids) == 0:
            return 0.0
        
        # Take only top K results
        top_k = retrieved_ids[:k]
        
        # Count how many relevant docs were retrieved in top K (ignore empty strings)
        retrieved_relevant = sum(1 for doc_id in top_k if doc_id and doc_id in relevant_ids)
        
        # CRITICAL: Divide by TOTAL relevant documents, not by K
        return retrieved_relevant / len(relevant_ids)
    
    def calculate_ndcg_at_k(self, relevance_scores: Dict[str, float], retrieved_ids: List[str], k: int) -> float:
        """
        Calculate NDCG@K (Normalized Discounted Cumulative Gain).
        
        NDCG measures ranking quality, considering both relevance and position.
        Higher relevance scores at top positions contribute more.
        
        DCG@K = Σ (relevance_score / log2(position + 1))
        NDCG@K = DCG@K / IDCG@K  (normalized by ideal DCG)
        
        Args:
            relevance_scores: Dict mapping document IDs to relevance scores
            retrieved_ids: List of retrieved document IDs (ordered by rank), may contain "" for non-matches
            k: Cutoff position
            
        Returns:
            NDCG@K score (0.0 to 1.0)
        """
        if k == 0:
            return 0.0
        
        # Take only top K results
        top_k = retrieved_ids[:k]
        
        # Calculate DCG
        dcg = 0.0
        for i, doc_id in enumerate(top_k, start=1):
            # Ignore empty strings (non-matches)
            if doc_id:
                relevance = relevance_scores.get(doc_id, 0.0)
                # DCG formula: relevance / log2(position + 1)
                dcg += relevance / math.log2(i + 1)
        
        # Calculate IDCG (ideal DCG with perfect ranking)
        ideal_scores = sorted(relevance_scores.values(), reverse=True)[:k]
        idcg = 0.0
        for i, relevance in enumerate(ideal_scores, start=1):
            idcg += relevance / math.log2(i + 1)
        
        # Normalize
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def evaluate_query(self, query_text: str, query_id: str, searcher: SemanticSearcher, k: int = 5) -> Dict[str, Any]:
        """
        Evaluate a single query.
        
        Args:
            query_text: Query string
            query_id: Query ID for looking up golden data
            searcher: SemanticSearcher instance
            k: Number of top results to evaluate (default: 5)
            
        Returns:
            Dictionary with metrics:
                - precision_at_k: Precision@K score
                - recall_at_k: Recall@K score
                - ndcg_at_k: NDCG@K score
                - retrieved_count: Number of results retrieved
                - relevant_count: Total number of relevant documents
                - matched_count: Number of retrieved docs that matched golden set
        """
        # Get search results (retrieve 10 but evaluate only k)
        results, _ = searcher.search(query_text, k=10, min_score=0.0)
        
        # Get relevance judgments for this query
        judgment = self.relevance_judgments.get(query_id, {})
        golden_results = judgment.get('results', [])
        
        # Build relevance scores dict and relevant IDs set
        relevance_scores = {}
        relevant_ids = set()
        
        for golden_result in golden_results:
            doc_id = golden_result.get('id', '')
            relevance_score = golden_result.get('relevance_score', 0)
            
            if doc_id:
                relevance_scores[doc_id] = float(relevance_score)
                # In 1-3 scale, all scores are relevant (1, 2, 3)
                if relevance_score > 0:
                    relevant_ids.add(doc_id)
        
        # Match retrieved results to golden IDs - PRESERVE POSITION INFORMATION
        # Retrieved_ids must be same length as results, with "" for non-matches
        retrieved_ids = []
        matched_count = 0
        for result in results:
            matched_id = self._match_result_to_golden(result, query_id)
            if matched_id:
                retrieved_ids.append(matched_id)
                matched_count += 1
            else:
                # CRITICAL: Add empty string to preserve position information
                retrieved_ids.append("")
        
        # Calculate metrics
        precision = self.calculate_precision_at_k(relevant_ids, retrieved_ids, k)
        # RECALL: Always compare top 10 golden results with top 10 system output
        recall = self.calculate_recall_at_k(relevant_ids, retrieved_ids, k=10)
        ndcg = self.calculate_ndcg_at_k(relevance_scores, retrieved_ids, k)
        
        return {
            'precision_at_k': precision,
            'recall_at_k': recall,
            'ndcg_at_k': ndcg,
            'retrieved_count': len(results),
            'relevant_count': len(relevant_ids),
            'matched_count': matched_count
        }
    
    def evaluate_all(self, searcher: SemanticSearcher, k: int = 5, verbose: bool = False) -> Dict[str, Any]:
        """
        Evaluate all queries in golden dataset.
        
        Args:
            searcher: SemanticSearcher instance
            k: Number of top results to evaluate per query
            verbose: If True, print per-query results
            
        Returns:
            Dictionary with aggregated metrics:
                - mean_precision: Average Precision@K across all queries
                - mean_recall: Average Recall@K across all queries
                - mean_ndcg: Average NDCG@K across all queries
                - final_accuracy_score: Weighted combination (50% NDCG, 25% Precision, 25% Recall)
                - per_query_results: List of individual query results
        """
        per_query_results = []
        
        total_queries = len(self.queries)
        
        if verbose:
            print(f"\nEvaluating {total_queries} queries...\n")
        
        for i, query_data in enumerate(self.queries, 1):
            # Flexible query ID handling - supports both 'id' and 'query_id' fields
            query_id = query_data.get('id') or query_data.get('query_id', f'q{i:03d}')
            query_text = query_data.get('query', '')
            
            if not query_text:
                if verbose:
                    print(f"Warning: Query {i} has no text, skipping...")
                continue
            
            # Evaluate this query
            result = self.evaluate_query(query_text, query_id, searcher, k=k)
            result['query_id'] = query_id
            result['query_text'] = query_text
            per_query_results.append(result)
            
            if verbose:
                print(f"[{i}/{total_queries}] {query_id}: "
                      f"P@{k}={result['precision_at_k']:.3f}, "
                      f"R@{k}={result['recall_at_k']:.3f}, "
                      f"NDCG@{k}={result['ndcg_at_k']:.3f}")
        
        # Calculate aggregate metrics
        if len(per_query_results) > 0:
            mean_precision = sum(r['precision_at_k'] for r in per_query_results) / len(per_query_results)
            mean_recall = sum(r['recall_at_k'] for r in per_query_results) / len(per_query_results)
            mean_ndcg = sum(r['ndcg_at_k'] for r in per_query_results) / len(per_query_results)
            
            # Final accuracy: 50% NDCG + 25% Precision + 25% Recall
            final_accuracy = 0.5 * mean_ndcg + 0.25 * mean_precision + 0.25 * mean_recall
        else:
            mean_precision = 0.0
            mean_recall = 0.0
            mean_ndcg = 0.0
            final_accuracy = 0.0
        
        if verbose:
            print("\n" + "=" * 80)
            print("EVALUATION COMPLETE")
            print("=" * 80)
            print(f"Final Accuracy: {final_accuracy:.4f} ({final_accuracy * 100:.2f}%)")
            print(f"Precision@{k}:   {mean_precision:.4f} ({mean_precision * 100:.2f}%)")
            print(f"Recall@{k}:      {mean_recall:.4f} ({mean_recall * 100:.2f}%)")
            print(f"NDCG@{k}:        {mean_ndcg:.4f} ({mean_ndcg * 100:.2f}%)")
            print("=" * 80 + "\n")
        
        return {
            'mean_precision_at_k': mean_precision,
            'mean_recall_at_k': mean_recall,
            'mean_ndcg_at_k': mean_ndcg,
            'final_accuracy_score': final_accuracy,
            'per_query_results': per_query_results,
            'query_results': per_query_results,  # Alias for compatibility
            'k': k,
            'total_queries': len(per_query_results)
        }


def run_evaluation(k: int = 10, verbose: bool = True):
    """
    Convenience function to run full evaluation.
    
    Args:
        k: Number of top results to evaluate
        verbose: Print detailed results
        
    Returns:
        Evaluation results dictionary
    """
    print(f"Initializing search engine...")
    searcher = SemanticSearcher()
    
    print(f"Initializing evaluator...")
    evaluator = SearchEvaluator()
    
    print(f"Running evaluation...\n")
    results = evaluator.evaluate_all(searcher, k=k, verbose=verbose)
    
    return results


if __name__ == "__main__":
    # Run evaluation when script is executed directly
    results = run_evaluation(k=10, verbose=True)
