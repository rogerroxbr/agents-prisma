"""MainStateGraph for LangGraph PRISMA pipeline."""
from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph, START, END

from src.agents.state import PRISMAState
from src.agents.nodes.identify_node import identify_node
from src.agents.nodes.screen_node import screen_node
from src.agents.nodes.read_node import read_node
from src.agents.nodes.synthesize_node import synthesize_node


def route_after_identify(state: PRISMAState) -> str:
    """Routing logic after identification phase."""
    return "screen"


def route_after_screen(state: PRISMAState) -> str:
    """Routing logic after screening phase."""
    screen_state = state.get("screening")
    ident_state = state.get("identification")
    
    if not screen_state or not ident_state:
        return "read"
        
    total_articles = ident_state.total_found
    batch_size = screen_state.current_batch_size
    processed = screen_state.batches_processed * batch_size
    
    # Simple pagination logic: if we haven't processed all articles, loop back to screen
    # For now, since identify returns all at once and screen processes all at once in MVP,
    # we just proceed to read. But this is where the batching condition would go.
    if processed < total_articles and total_articles > 0:
        pass # In a real batched setup, we'd return 'screen' to loop.
        
    return "read"


class MainStateGraph:
    """Main orchestrator using LangGraph StateGraph pattern."""
    
    def __init__(self, total_target: int = 100):
        self.total_target = total_target
        self.workflow = StateGraph(PRISMAState)
        self._build_graph()
        
    def _build_graph(self):
        """Build the nodes and edges of the StateGraph."""
        # Add Nodes
        self.workflow.add_node("identify", identify_node)
        self.workflow.add_node("screen", screen_node)
        self.workflow.add_node("read", read_node)
        self.workflow.add_node("synthesize", synthesize_node)
        
        # Add Edges
        self.workflow.add_edge(START, "identify")
        
        # Conditional edges
        self.workflow.add_conditional_edges("identify", route_after_identify)
        self.workflow.add_conditional_edges("screen", route_after_screen)
        
        # Linear edges for the rest
        self.workflow.add_edge("read", "synthesize")
        self.workflow.add_edge("synthesize", END)
    
    def compile(self, checkpointer=None) -> Any:
        """Compile and return the graph application.
        
        Args:
            checkpointer: Optional LangGraph checkpointer (e.g., PostgresSaver)
            
        Returns:
            Compiled LangGraph app ready for execution
        """
        print(f"[ORCHESTRATOR] Compiling MainStateGraph (target: {self.total_target})")
        
        if checkpointer:
            print("[ORCHESTRATOR] Using provided checkpointer (Postgres)")
            return self.workflow.compile(checkpointer=checkpointer)
            
        return self.workflow.compile()


__all__ = ["MainStateGraph"]
