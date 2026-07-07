"""MainStateGraph for LangGraph PRISMA pipeline."""
from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph, START, END

from src.agents.state import PRISMAState
from src.agents.nodes.identify_node import identify_node
from src.agents.nodes.screen_node import screen_node


def route_after_identify(state: PRISMAState) -> str:
    """Routing logic after identification phase."""
    # Always proceed to screen for now
    return "screen"


def route_after_screen(state: PRISMAState) -> str:
    """Routing logic after screening phase."""
    # Pending reading phase implementation, go to END
    return END


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
        
        # Add Edges
        self.workflow.add_edge(START, "identify")
        
        # Conditional edges could be used if we process in batches
        self.workflow.add_conditional_edges("identify", route_after_identify)
        self.workflow.add_conditional_edges("screen", route_after_screen)
    
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
