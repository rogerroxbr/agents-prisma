"""Synthesis phase - Generating final outputs (pure function)."""
from typing import Any, Dict

from src.agents.state import PRISMAState, SynthesisState

def synthesize_node(state: PRISMAState) -> PRISMAState:
    """Pure function: Synthesize all data into final reports.
    
    Args:
        state: Current PRISMAState
        
    Returns:
        Updated state with synthesis outputs
    """
    eligibility_state = state.get("eligibility")
    
    if not eligibility_state or not eligibility_state.pico_data:
        print("[SYNTHESIZE_NODE] No eligible articles for synthesis")
        return {"phase": "done", "progress": 100.0}
        
    print(f"[SYNTHESIZE_NODE] Synthesizing {len(eligibility_state.pico_data)} articles...")
    
    synthesis_state = state.get("synthesis")
    if not synthesis_state:
        synthesis_state = SynthesisState()
        
    markdown_outputs = []
    markdown_outputs.append("# PRISMA Synthesis Report\n")
    
    for pico in eligibility_state.pico_data:
        aid = pico.get("article_id")
        markdown_outputs.append(f"## Article {aid}\n- **Population**: {pico.get('population')}\n- **Intervention**: {pico.get('intervention')}\n")
        
    synthesis_state.markdown_outputs = markdown_outputs
    synthesis_state.flowchart_generated = True
    
    print("[SYNTHESIZE_NODE] Synthesis complete!")
    
    return {
        "synthesis": synthesis_state,
        "progress": 100.0,
        "phase": "done"
    }

__all__ = ["synthesize_node"]
