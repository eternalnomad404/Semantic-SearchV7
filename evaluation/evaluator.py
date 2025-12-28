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
    Evaluates search system performance using golden dataset.
    Calculates Precision@10, Recall@10, NDCG@10 for each query and aggregates results.
    """
    
    def __init__(self, golden_dataset_path: str = "search-evaluation-goldens/goldens/v1"):
        """
        Initialize evaluator with golden dataset.
        
        Args:
            golden_dataset_path: Path to golden dataset directory
        """
        self.golden_path = Path(golden_dataset_path)
        self.queries = self._load_queries()
        self.relevance_judgments = self._load_relevance_judgments()
        
        # Load data files to create slug->ID mapping
        self.slug_to_id = self._build_slug_to_id_mapping()
        
    def _build_slug_to_id_mapping(self) -> Dict[str, str]:
        """
        Build mapping from slug to document_id by loading all data files.
        
        Returns:
            Dict mapping slug -> document_id (e.g., "chatgpt" -> "tool_12")
        """
        slug_to_id = {}
        
        # Load tools
        tools_path = Path("data/tools")
        if tools_path.exists():
            for json_file in sorted(tools_path.glob("*.json")):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        items = json.load(f)
                        for item in items:
                            slug = item.get('slug', '')
                            item_id = item.get('id')
                            if slug and item_id:
                                slug_to_id[slug] = f"tool_{item_id}"
                except Exception as e:
                    print(f"Warning: Could not load {json_file}: {e}")
        
        # Load courses
        courses_path = Path("data/courses")
        if courses_path.exists():
            for json_file in sorted(courses_path.glob("*.json")):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        items = json.load(f)
                        for item in items:
                            slug = item.get('slug', '')
                            item_id = item.get('id')
                            if slug and item_id:
                                slug_to_id[slug] = f"course_{item_id}"
                except Exception as e:
                    print(f"Warning: Could not load {json_file}: {e}")
        
        # Load service providers
        services_path = Path("data/service_providers")
        if services_path.exists():
            for json_file in sorted(services_path.glob("*.json")):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        items = json.load(f)
                        for item in items:
                            slug = item.get('slug', '')
                            item_id = item.get('id')
                            if slug and item_id:
                                slug_to_id[slug] = f"service_{item_id}"
                except Exception as e:
                    print(f"Warning: Could not load {json_file}: {e}")
        
        # Load case studies
        case_studies_path = Path("data/case_studies")
        if case_studies_path.exists():
            for json_file in sorted(case_studies_path.glob("*.json")):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        items = json.load(f)
                        for item in items:
                            slug = item.get('slug', '')
                            item_id = item.get('id')
                            if slug and item_id:
                                slug_to_id[slug] = f"case_study_{item_id}"
                except Exception as e:
                    print(f"Warning: Could not load {json_file}: {e}")
        
        return slug_to_id
        
    def _load_queries(self) -> List[Dict[str, Any]]:
        """Load test queries from golden dataset."""
        queries_file = self.golden_path / "queries.json"
        with open(queries_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('queries', [])
    
    def _load_relevance_judgments(self) -> Dict[str, Dict[str, int]]:
        """
        Load relevance judgments from golden dataset.
        
        Returns:
            Dict mapping query_id -> {document_id -> relevance_score}
        """
        judgments_file = self.golden_path / "relevance_judgments.json"
        with open(judgments_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to dictionary format: query_id -> {doc_id -> score}
        judgments_dict = {}
        for judgment in data.get('judgments', []):
            query_id = judgment['query_id']
            judgments_dict[query_id] = {}
            for result in judgment.get('results', []):
                doc_id = result['id']
                relevance_score = result['relevance_score']
                judgments_dict[query_id][doc_id] = relevance_score
        
        return judgments_dict
    
    def _match_document_id(self, result: Dict[str, Any]) -> str:
        """
        Match search result to golden dataset document ID.
        
        Uses the pre-built slug-to-ID mapping for fast lookup.
        
        Args:
            result: Search result with metadata
            
        Returns:
            Document ID string (e.g., "tool_232")
        """
        metadata = result.get('metadata', {})
        slug = metadata.get('slug', '')
        
        if not slug:
            return "unknown_unknown"
        
        # Look up in pre-built mapping
        return self.slug_to_id.get(slug, f"unknown_{slug}")
    
    def calculate_precision_at_k(self, retrieved_docs: List[str], relevant_docs: List[str], k: int = 10) -> float:
        """
        Calculate Precision@K.
        
        Precision@K = (# of relevant documents in top K) / K
        
        Args:
            retrieved_docs: List of retrieved document IDs (in ranked order)
            relevant_docs: List of relevant document IDs from golden dataset
            k: Number of top results to consider
            
        Returns:
            Precision@K score (0.0 to 1.0)
        """
        top_k_docs = retrieved_docs[:k]
        relevant_in_top_k = len([doc for doc in top_k_docs if doc in relevant_docs])
        return relevant_in_top_k / k if k > 0 else 0.0
    
    def calculate_recall_at_k(self, retrieved_docs: List[str], relevant_docs: List[str], k: int = 10) -> float:
        """
        Calculate Recall@K.
        
        Recall@K = (# of relevant documents in top K) / (total # of relevant documents)
        
        Args:
            retrieved_docs: List of retrieved document IDs (in ranked order)
            relevant_docs: List of relevant document IDs from golden dataset
            k: Number of top results to consider
            
        Returns:
            Recall@K score (0.0 to 1.0)
        """
        if len(relevant_docs) == 0:
            return 0.0
        
        top_k_docs = retrieved_docs[:k]
        relevant_in_top_k = len([doc for doc in top_k_docs if doc in relevant_docs])
        return relevant_in_top_k / len(relevant_docs)
    
    def calculate_dcg_at_k(self, retrieved_docs: List[str], relevance_scores: Dict[str, int], k: int = 10) -> float:
        """
        Calculate Discounted Cumulative Gain at K.
        
        DCG@K = sum(rel_i / log2(i + 1)) for i in 1..k
        
        Args:
            retrieved_docs: List of retrieved document IDs (in ranked order)
            relevance_scores: Dict mapping document ID to relevance score
            k: Number of top results to consider
            
        Returns:
            DCG@K score
        """
        dcg = 0.0
        for i, doc_id in enumerate(retrieved_docs[:k], start=1):
            relevance = relevance_scores.get(doc_id, 0)
            # DCG formula: rel / log2(rank + 1)
            dcg += relevance / math.log2(i + 1)
        return dcg
    
    def calculate_ndcg_at_k(self, retrieved_docs: List[str], relevance_scores: Dict[str, int], k: int = 10) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain at K.
        
        NDCG@K = DCG@K / IDCG@K
        
        Where IDCG@K is the ideal DCG (documents sorted by relevance).
        
        Args:
            retrieved_docs: List of retrieved document IDs (in ranked order)
            relevance_scores: Dict mapping document ID to relevance score
            k: Number of top results to consider
            
        Returns:
            NDCG@K score (0.0 to 1.0)
        """
        # Calculate DCG for retrieved results
        dcg = self.calculate_dcg_at_k(retrieved_docs, relevance_scores, k)
        
        # Calculate IDCG (ideal DCG) - sort by relevance score descending
        ideal_docs = sorted(relevance_scores.keys(), key=lambda x: relevance_scores[x], reverse=True)
        idcg = self.calculate_dcg_at_k(ideal_docs, relevance_scores, k)
        
        # Normalize
        if idcg == 0:
            return 0.0
        return dcg / idcg
    
    def evaluate_query(self, query: str, query_id: str, searcher: SemanticSearcher, k: int = 10) -> Dict[str, Any]:
        """
        Evaluate a single query.
        
        Args:
            query: Query text
            query_id: Query ID (e.g., "q001")
            searcher: SemanticSearcher instance
            k: Number of results to retrieve and evaluate
            
        Returns:
            Dict with evaluation metrics for this query
        """
        # Get search results
        results, _ = searcher.search(query, k=k, min_score=0.0)  # No min_score for evaluation
        
        # Extract document IDs from results
        retrieved_doc_ids = []
        for result in results:
            doc_id = self._match_document_id(result)
            retrieved_doc_ids.append(doc_id)
        
        # Get relevance judgments for this query
        query_judgments = self.relevance_judgments.get(query_id, {})
        
        # Get list of relevant documents (any relevance score > 0)
        relevant_docs = [doc_id for doc_id, score in query_judgments.items() if score > 0]
        
        # Calculate metrics
        precision = self.calculate_precision_at_k(retrieved_doc_ids, relevant_docs, k)
        recall = self.calculate_recall_at_k(retrieved_doc_ids, relevant_docs, k)
        ndcg = self.calculate_ndcg_at_k(retrieved_doc_ids, query_judgments, k)
        
        return {
            'query_id': query_id,
            'query': query,
            'precision_at_k': precision,
            'recall_at_k': recall,
            'ndcg_at_k': ndcg,
            'retrieved_count': len(retrieved_doc_ids),
            'relevant_count': len(relevant_docs),
            'retrieved_doc_ids': retrieved_doc_ids[:k]  # For debugging
        }
    
    def evaluate_all(self, searcher: SemanticSearcher, k: int = 10, verbose: bool = True) -> Dict[str, Any]:
        """
        Evaluate all queries in the golden dataset.
        
        Args:
            searcher: SemanticSearcher instance
            k: Number of results to retrieve and evaluate for each query
            verbose: Whether to print detailed logs
            
        Returns:
            Dict with aggregated evaluation results
        """
        if verbose:
            print("\n" + "="*80)
            print("SEARCH EVALUATION SYSTEM")
            print("="*80)
            print(f"Evaluating {len(self.queries)} queries from golden dataset")
            print(f"Metrics: Precision@{k}, Recall@{k}, NDCG@{k}")
            print(f"K = {k}")
            print("="*80 + "\n")
        
        query_results = []
        
        for i, query_data in enumerate(self.queries, 1):
            query_id = query_data['id']  # Changed from 'query_id' to 'id'
            query_text = query_data['query']
            
            if verbose:
                print(f"[{i}/{len(self.queries)}] Evaluating: {query_id} - \"{query_text}\"")
            
            # Evaluate query
            result = self.evaluate_query(query_text, query_id, searcher, k)
            query_results.append(result)
            
            if verbose:
                print(f"    * Precision@{k}: {result['precision_at_k']:.4f}")
                print(f"    * Recall@{k}:    {result['recall_at_k']:.4f}")
                print(f"    * NDCG@{k}:      {result['ndcg_at_k']:.4f}")
                print()
        
        # Calculate aggregated metrics
        mean_precision = sum(r['precision_at_k'] for r in query_results) / len(query_results)
        mean_recall = sum(r['recall_at_k'] for r in query_results) / len(query_results)
        mean_ndcg = sum(r['ndcg_at_k'] for r in query_results) / len(query_results)
        
        # Calculate Final Accuracy Score
        # Formula: 0.5 × NDCG@10 + 0.25 × Precision@10 + 0.25 × Recall@10
        final_accuracy = (0.5 * mean_ndcg) + (0.25 * mean_precision) + (0.25 * mean_recall)
        
        aggregated_results = {
            'total_queries': len(query_results),
            'k': k,
            'mean_precision_at_k': mean_precision,
            'mean_recall_at_k': mean_recall,
            'mean_ndcg_at_k': mean_ndcg,
            'final_accuracy_score': final_accuracy,
            'per_query_results': query_results
        }
        
        if verbose:
            print("\n" + "="*80)
            print("AGGREGATED EVALUATION RESULTS")
            print("="*80)
            print(f"Total Queries Evaluated: {len(query_results)}")
            print(f"\nMean Metrics (K={k}):")
            print(f"  * Mean Precision@{k}:  {mean_precision:.4f} ({mean_precision*100:.2f}%)")
            print(f"  * Mean Recall@{k}:     {mean_recall:.4f} ({mean_recall*100:.2f}%)")
            print(f"  * Mean NDCG@{k}:       {mean_ndcg:.4f} ({mean_ndcg*100:.2f}%)")
            print(f"\nFINAL ACCURACY SCORE: {final_accuracy:.4f} ({final_accuracy*100:.2f}%)")
            print(f"\n   Formula: 0.5 x NDCG@{k} + 0.25 x Precision@{k} + 0.25 x Recall@{k}")
            print(f"          = 0.5 x {mean_ndcg:.4f} + 0.25 x {mean_precision:.4f} + 0.25 x {mean_recall:.4f}")
            print(f"          = {final_accuracy:.4f}")
            print("="*80 + "\n")
        
        return aggregated_results


def run_evaluation(k: int = 10, verbose: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run full evaluation.
    
    Args:
        k: Number of results to evaluate (default: 10)
        verbose: Whether to print detailed logs
        
    Returns:
        Dict with evaluation results
    """
    # Initialize searcher
    searcher = SemanticSearcher()
    
    # Initialize evaluator
    evaluator = SearchEvaluator()
    
    # Run evaluation
    results = evaluator.evaluate_all(searcher, k=k, verbose=verbose)
    
    return results


if __name__ == "__main__":
    # Run evaluation when script is executed directly
    run_evaluation(k=10, verbose=True)
