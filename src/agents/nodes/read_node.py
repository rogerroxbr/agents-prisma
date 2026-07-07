"""Read / Eligibility phase - Deep reading (pure function)."""
from typing import Any, Dict

from src.agents.state import PRISMAState, EligibilityState
from src.tools.markitdown_tool import MarkItDownTool
from src.agents.deep_reader import DeepReaderAgent

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
        
    md_tool = MarkItDownTool()
    reader = DeepReaderAgent()
        
    pico_data = []
    markdown_outputs = []
    
    # Retrieve raw metadata dictionary for context to extract the DOI
    # We can fetch it by iterating through ident_state.sources
    ident_state = state.get("identification")
    articles_map = {}
    if ident_state and ident_state.sources:
        for source_articles in ident_state.sources.values():
            for art in source_articles:
                # Same ID logic as in screen_node.py
                art_id = hash(art.get("doi") or art.get("title") or "")
                articles_map[art_id] = art
    
    pdfs_extracted = 0
    total_confidence = 0.0
    
    for aid in included_ids:
        article = articles_map.get(aid, {"title": f"Unknown {aid}", "doi": ""})
        doi = article.get("doi")
        
        # 1. Download and convert to Markdown
        if doi:
            markdown_text = md_tool.process_article(doi)
            pdfs_extracted += 1
        else:
            print(f"[READ_NODE] Warning: No DOI for article {aid}, falling back to abstract if available.")
            markdown_text = article.get("abstract", "No full text available.")
            
        # 2. Deep read extraction
        result = reader.analyze_article(article, markdown_text)
        result["article_id"] = aid
        pico_data.append(result)
        
        total_confidence += result.get("confidence", 0.0)
        
        # Format the markdown output for the user
        md_output = f"# {article.get('title')}\n\n**DOI**: {doi}\n\n"
        md_output += f"## Extraction Results\n"
        md_output += f"- **Population**: {result['population']}\n"
        md_output += f"- **Intervention**: {result['intervention']}\n"
        md_output += f"- **Comparator**: {result['comparator']}\n"
        md_output += f"- **Outcome**: {result['outcome']}\n"
        md_output += f"- **Risk of Bias**: {result['risk_of_bias']}\n\n"
        md_output += f"## Full Text Markdown\n\n{markdown_text[:1000]}...\n" # Truncated for display
        
        markdown_outputs.append(md_output)
        
    eligibility_state.pdfs_extracted = pdfs_extracted
    eligibility_state.pico_data = pico_data
    eligibility_state.extraction_confidence = total_confidence / len(included_ids) if included_ids else 0.0
    eligibility_state.markdown_outputs = markdown_outputs
    
    return {
        "eligibility": eligibility_state,
        "progress": 75.0,
        "phase": "synthesize"
    }

__all__ = ["read_node"]
