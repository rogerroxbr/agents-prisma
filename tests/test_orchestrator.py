"""Tests for the Orchestrator Agent."""
import sys
sys.path.insert(0, '.')

from src.agents.orchestrator import OrchestratorAgent, PipelinePhase


def test_orchestrator_initialization():
    """Test basic initialization."""
    orchestrator = OrchestratorAgent(project_id=1, db_session=None)
    
    assert orchestrator.project_id == 1
    assert orchestrator.current_phase is None
    
    print("OK: Test passed - Orchestrator initialized correctly")


def test_transition_to_valid_phase():
    """Test transition to valid phases."""
    class MockSession:
        def query(self, cls): return self
        def filter_by(self, **kwargs): return self
        def first(self): return None
        def add(self, obj): pass
        def commit(self): pass
    
    orchestrator = OrchestratorAgent(project_id=1, db_session=MockSession())
    
    # Test all valid phases
    for phase in PipelinePhase.ALL_PHASES:
        orchestrator.transition_to(phase)
        assert orchestrator.current_phase == phase
    
    print("OK: All valid phases transitioned correctly")


def test_transition_invalid_phase():
    """Test transition to invalid phase."""
    class MockSession:
        def query(self, cls): return self
        def filter_by(self, **kwargs): return self
        def first(self): return None
        def add(self, obj): pass
        def commit(self): pass
    
    orchestrator = OrchestratorAgent(project_id=1, db_session=MockSession())
    
    try:
        orchestrator.transition_to("invalid_phase")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"OK: Invalid phase caught - {str(e)[:50]}...")


def test_state_serialization():
    """Test JSON serialization."""
    class MockSession:
        def query(self, cls): return self
        def filter_by(self, **kwargs): return self
        def first(self): 
            from src.db.models import PipelineState
            state = PipelineState(project_id=1, phase="identification")
            return state
        def add(self, obj): pass
        def commit(self): pass
    
    orchestrator = OrchestratorAgent(project_id=1, db_session=MockSession())
    
    # Test serialization
    json_str = orchestrator.get_state_json()
    assert "project_id" in json_str
    assert "phase" in json_str
    
    print("OK: State serialization works")


if __name__ == "__main__":
    test_orchestrator_initialization()
    test_transition_to_valid_phase()
    test_transition_invalid_phase()
    test_state_serialization()
    print("\n=== All tests passed! ===")
