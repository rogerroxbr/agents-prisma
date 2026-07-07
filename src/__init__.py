"""Main package - PRISMA Multi-Agent System."""
from src.agents import SearcherAgent, ScreeningAgent, OrchestratorAgent
from src.tools.pubmed_tool import PubMedTool
from src.tools.scopus_tool import ScopusTool

__version__ = "0.1.5"
__all__ = [
    "SearcherAgent", 
    "ScreeningAgent", 
    "OrchestratorAgent",
    "PubMedTool",
    "ScopusTool"
]
