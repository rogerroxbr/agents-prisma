"""Read / Eligibility phase - Deep reading (pure function)."""
from typing import Any, Dict

from src.agents.state import PRISMAState, EligibilityState

def read_node(state: PRISMAState) -> PRISMAState:
    """Pure function: Deep read full text for eligible articles.
    
    Args:
        state: Current PRISMAState
        
    Returns:
        Updated state with eligibility results
    """
    screen_state = state.get("screening")
    
    if not screen_state or not screen_state.decisions:
        print("[READ_NODE] No screened articles found")
        return {"phase": "synthesize"}
        
    # Get all included articles
    included_ids = [aid for aid, decision_dict in screen_state.decisions.items() if decision_dict.get("decision") == "include"]
    
    if not included_ids:
        print("[READ_NODE] No articles were included for reading")
        return {"phase": "synthesize"}
        
    print(f"[READ_NODE] Deep reading {len(included_ids)} eligible articles...")
    
    eligibility_state = state.get("eligibility")
    if not eligibility_state:
        eligibility_state = EligibilityState()
        
    # Mocking deep reading / PDF extraction
    pico_data = []
    for aid in included_ids:
        pico_data.append({
            "article_id": aid,
            "population": "Extracted population data",
            "intervention": "Extracted intervention data",
            "comparator": "Extracted comparator data",
            "outcome": "Extracted outcome data"
        })
        
    eligibility_state.pdfs_extracted = len(included_ids)
    eligibility_state.pico_data = pico_data
    eligibility_state.extraction_confidence = 0.85
    eligibility_state.markdown_outputs = [
        f"# Article {aid}\n\nDeep read summary..." for aid in included_ids
    ]
    
    return {
        "eligibility": eligibility_state,
        "progress": 75.0,
        "phase": "synthesize"
    }

__all__ = ["read_node"]
