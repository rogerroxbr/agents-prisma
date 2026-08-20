import os

from src.agents.prisma_flowchart import PRISMAFlowchartGenerator
from src.agents.state import PRISMAState, SynthesisState
from src.agents.synthesizer import SynthesizerAgent


def synthesize_node(state: PRISMAState) -> PRISMAState:
    """Pure function: Synthesize all data into final reports.

    Args:
        state: Current PRISMAState

    Returns:
        Updated state with synthesis outputs
    """
    eligibility_state = state.get("eligibility")
    screening_state = state.get("screening")
    identify_state = state.get("identify")

    # Reconstruct the eligible articles array
    eligible_articles = []

    # We will build it from the articles currently tracked in the state
    if eligibility_state and eligibility_state.pico_data:
        # PICO data acts as our proof of eligibility
        for pico in eligibility_state.pico_data:
            aid = pico.get("article_id")
            # We can find the matching article in identify_state
            art_meta = {}
            if identify_state and identify_state.sources:
                for source_articles in identify_state.sources.values():
                    for art in source_articles:
                        if art.get("id") == aid or art.get("doi") == aid:
                            art_meta = art
                            break
                    if art_meta:
                        break

            eligible_articles.append(
                {
                    "id": aid,
                    "title": art_meta.get("title", f"Article {aid}"),
                    "doi": art_meta.get("doi", ""),
                    "extracted_data": {
                        "pico": {
                            "population": pico.get("population", []),
                            "intervention": pico.get("intervention", []),
                            "comparison": pico.get("comparison", []),
                            "outcome": pico.get("outcome", []),
                        },
                        "risk_of_bias": pico.get("risk_of_bias", {}),
                    },
                }
            )

    if not eligible_articles:
        print("[SYNTHESIZE_NODE] No eligible articles for synthesis")
        return {"phase": "done", "progress": 100.0}

    print(f"[SYNTHESIZE_NODE] Synthesizing {len(eligible_articles)} articles...")

    # Initialize agents
    synthesizer = SynthesizerAgent()
    flowchart_gen = PRISMAFlowchartGenerator()

    # Generate thematic synthesis
    synthesis_result = synthesizer.synthesize(eligible_articles)

    # Generate Markdown Report without Flowchart yet
    markdown_report = synthesizer.generate_markdown_report(
        eligible_articles,
        synthesis_result,
        {"name": "Revisão Sistemática (Agents-Prisma)"},
    )

    # Calculate PRISMA Flowchart Stats
    identified = identify_state.total_found if identify_state else 0
    screened = len(screening_state.articles_reviewed) if screening_state else identified

    # If using batches, the number of screened excludes could be the sum of those excluded
    screening_excluded = 0
    if screening_state and screening_state.decisions:
        for decision_data in screening_state.decisions.values():
            decision = (
                decision_data.get("decision")
                if isinstance(decision_data, dict)
                else decision_data
            )
            if decision == "exclude":
                screening_excluded += 1

    sought = len(
        eligible_articles
    )  # In a real scenario, could be higher if some couldn't be downloaded
    not_retrieved = 0  # Simplified
    assessed = len(eligible_articles)
    eligibility_excluded = 0  # If deep reader rejected them, they wouldn't be here
    included = len(eligible_articles)

    stats = {
        "identified": identified,
        "screened": screened,
        "screening_excluded": screening_excluded,
        "screening_duplicates": 0,
        "sought_for_retrieval": sought,
        "not_retrieved": not_retrieved,
        "assessed_for_eligibility": assessed,
        "eligibility_excluded": eligibility_excluded,
        "included": included,
    }

    mermaid_chart = flowchart_gen.generate_mermaid(stats)

    # Append Flowchart to Markdown
    final_markdown = markdown_report + "\n\n## Fluxograma PRISMA\n\n" + mermaid_chart

    # Save physically to outputs/reports/ folder
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "outputs", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    out_path_md = os.path.join(reports_dir, "synthesis_report.md")
    with open(out_path_md, "w", encoding="utf-8") as f:
        f.write(final_markdown)

    # Save JSON export
    import json
    json_export = {
        "metadata": {"name": "Revisão Sistemática (Agents-Prisma)"},
        "stats": stats,
        "eligible_articles": eligible_articles,
        "synthesis": synthesis_result.model_dump()
    }
    out_path_json = os.path.join(reports_dir, "synthesis_report.json")
    with open(out_path_json, "w", encoding="utf-8") as f:
        json.dump(json_export, f, ensure_ascii=False, indent=2)

    print(f"[SYNTHESIZE_NODE] Report saved to {out_path_md}")
    print(f"[SYNTHESIZE_NODE] JSON export saved to {out_path_json}")

    # Update state
    synthesis_state = state.get("synthesis")
    if not synthesis_state:
        synthesis_state = SynthesisState()

    synthesis_state.markdown_outputs = [final_markdown]
    synthesis_state.flowchart_generated = True

    print("[SYNTHESIZE_NODE] Synthesis complete!")

    return {"synthesis": synthesis_state, "progress": 100.0, "phase": "done"}


__all__ = ["synthesize_node"]
