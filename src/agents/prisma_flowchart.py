from typing import Any


class PRISMAFlowchartGenerator:
    """
    Generates PRISMA flowcharts in Mermaid.js syntax based on pipeline statistics.
    """

    def __init__(self):
        pass

    def generate_mermaid(self, stats: dict[str, Any]) -> str:
        """
        Generates the PRISMA flowchart in Mermaid syntax.

        Expected stats dictionary structure:
        {
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
        """
        # Set default values if keys are missing
        identified = stats.get("identified", 0)
        screened = stats.get("screened", 0)
        screening_excluded = stats.get("screening_excluded", 0)
        screening_duplicates = stats.get("screening_duplicates", 0)
        sought = stats.get("sought_for_retrieval", 0)
        not_retrieved = stats.get("not_retrieved", 0)
        assessed = stats.get("assessed_for_eligibility", 0)
        eligibility_excluded = stats.get("eligibility_excluded", 0)
        included = stats.get("included", 0)

        mermaid_template = f"""```mermaid
flowchart TD
    %% Identificação
    Identified["Registros identificados nas bases de dados (n = {identified})"]
    
    %% Triagem
    Screened["Registros triados (n = {screened})"]
    Identified --> Screened
    
    Duplicates["Registros removidos antes da triagem: Duplicatas (n = {screening_duplicates})"]
    Identified -.-> Duplicates
    
    ExcludedScreening["Registros excluídos na triagem (n = {screening_excluded})"]
    Screened --> ExcludedScreening
    
    %% Elegibilidade
    SoughtRetrieval["Relatórios buscados para recuperação (n = {sought})"]
    Screened --> SoughtRetrieval
    
    NotRetrieved["Relatórios não recuperados (n = {not_retrieved})"]
    SoughtRetrieval --> NotRetrieved
    
    AssessedElig["Relatórios avaliados para elegibilidade (n = {assessed})"]
    SoughtRetrieval --> AssessedElig
    
    ExcludedElig["Relatórios excluídos: Não atendem aos critérios (n = {eligibility_excluded})"]
    AssessedElig --> ExcludedElig
    
    %% Inclusão
    Included["Estudos incluídos na revisão (n = {included})"]
    AssessedElig --> Included
    
    %% Estilização
    style Identified fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style Screened fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style SoughtRetrieval fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style AssessedElig fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style Included fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style ExcludedScreening fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style ExcludedElig fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style NotRetrieved fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style Duplicates fill:#ffebee,stroke:#d32f2f,stroke-width:2px
```"""
        return mermaid_template
