"""Screening phase - LLM-based filtering (pure function)."""

from src.agents.screener import ScreeningAgent
from src.agents.state import PRISMAState, ScreeningState


def screen_node(state: PRISMAState) -> PRISMAState:
    """Pure function: Screen articles with LLM-based PICO extraction.

    Args:
        state: Current PRISMAState

    Returns:
        Updated state with screening_results
    """
    ident_state = state.get("identification")
    if not ident_state or not ident_state.sources:
        print("[SCREEN_NODE] No articles found in identification state")
        return {"phase": "read"}

    # Gather all raw metadata from all sources
    raw_metadata = []
    for source_articles in ident_state.sources.values():
        raw_metadata.extend(source_articles)

    screen_state = state.get("screening")
    if not screen_state:
        screen_state = ScreeningState()

    batch_size = screen_state.current_batch_size

    try:
        screener = ScreeningAgent()
        # criteria logic could be added here
        results = screener.screen_batch(raw_metadata, batch_size=batch_size)
        print(f"[SCREEN_NODE] Screened {len(results)} articles")
    except Exception as e:
        print(f"[SCREEN_NODE] Error during screening: {e}")
        results = []

    # Update decisions dictionary in ScreeningState
    decisions = screen_state.decisions
    for i, r in enumerate(results):
        # We use index or DOI as ID. Let's use index for simplicity in this MVP
        article = r.get("article", {})
        article_id = hash(article.get("doi") or article.get("title") or str(i))
        decisions[article_id] = {
            "decision": r.get("decision"),
            "reason": r.get("reason"),
            "score": r.get("score"),
            "pico_extracted": r.get("pico_extracted"),
        }
        if article_id not in screen_state.articles_reviewed:
            screen_state.articles_reviewed.append(article_id)

    screen_state.decisions = decisions
    screen_state.batches_processed += 1

    included = [r for r in results if r.get("decision") == "include"]

    return {
        "screening": screen_state,
        "progress": min(50.0, (len(results) / max(len(raw_metadata), 1)) * 25 + 25),
        "phase": "read",  # Proceed to read phase next
    }


__all__ = ["screen_node"]
