from src.agents.prisma_flowchart import PRISMAFlowchartGenerator

def test_generate_mermaid():
    generator = PRISMAFlowchartGenerator()
    stats = {
        "identified": 150,
        "screened": 150,
        "screening_excluded": 100,
        "screening_duplicates": 5,
        "sought_for_retrieval": 45,
        "not_retrieved": 5,
        "assessed_for_eligibility": 40,
        "eligibility_excluded": 25,
        "included": 15
    }
    mermaid = generator.generate_mermaid(stats)
    
    assert "```mermaid" in mermaid
    assert "(n = 150)" in mermaid
    assert "(n = 100)" in mermaid
    assert "(n = 45)" in mermaid
    assert "(n = 15)" in mermaid
    assert "flowchart TD" in mermaid
