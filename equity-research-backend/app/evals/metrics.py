from typing import Dict, Any, List

def compute_eval_metrics(total_claims: int, unsupported_claims: List[str]) -> Dict[str, Any]:
    """
    Computes citation coverage % and groundedness.
    """
    unsupported_count = len(unsupported_claims)
    
    if total_claims == 0:
        coverage = 100.0
    else:
        supported_count = total_claims - unsupported_count
        coverage = (supported_count / total_claims) * 100.0
        
    groundedness = unsupported_count == 0
    
    return {
        "citation_coverage_percent": round(coverage, 2),
        "groundedness": groundedness,
        "total_claims": total_claims,
        "unsupported_claims_count": unsupported_count,
        "unsupported_claims": unsupported_claims
    }
