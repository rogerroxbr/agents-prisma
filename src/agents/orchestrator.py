"""Orchestrador principal da pipeline PRISMA."""
from typing import Dict, Any, Optional
from datetime import datetime
import json
import logging

from sqlalchemy.orm import Session
from src.db.models import Base, Project, Phase, Article, PipelineState


class PipelinePhase:
    """Enum-like class for pipeline phases."""
    
    IDENTIFICATION = "identification"
    SCREENING = "screening"  
    ELIGIBILITY = "eligibility"
    SYNTHESIS = "synthesis"
    
    ALL_PHASES = [IDENTIFICATION, SCREENING, ELIGIBILITY, SYNTHESIS]


class OrchestratorAgent:
    """Agente Orquestrador para gerenciar o fluxo da pipeline PRISMA."""
    
    def __init__(self, project_id: int, db_session: Session):
        self.project_id = project_id
        self.db_session = db_session
        self.current_phase = None
        self.state_history: list[Dict[str, Any]] = []
        
        # Configurar logging
        self.logger = self._setup_logging()
        
        self.logger.info(
            "OrchestratorAgent initialized",
            extra={
                "project_id": project_id,
                "db_session": db_session
            }
        )
    
    def _setup_logging(self) -> logging.Logger:
        """Configura logging estruturado JSON."""
        logger = logging.getLogger(f"orchestrator.{self.project_id}")
        logger.setLevel(logging.INFO)
        
        # Handler para console
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        
        # Handler para arquivo JSON
        file_handler = logging.FileHandler(f"/tmp/orchestrator_{self.project_id}.log")
        file_handler.setFormatter(handler.formatter)
        
        logger.addHandler(handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def _get_current_state(self) -> Optional[PipelineState]:
        """Busca ou cria estado atual do pipeline."""
        state = self.db_session.query(PipelineState).filter_by(
            project_id=self.project_id,
            phase=self.current_phase
        ).first()
        
        if not state:
            # Cria novo estado para a fase atual
            state = PipelineState(
                project_id=self.project_id,
                phase="identification",  # Default phase
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            self.db_session.add(state)
        
        return state
    
    def transition_to(self, target_phase: str):
        """Transiciona para uma nova fase do pipeline."""
        if target_phase not in PipelinePhase.ALL_PHASES:
            raise ValueError(
                f"Invalid phase: {target_phase}. Must be one of "
                f"{PipelinePhase.ALL_PHASES}"
            )
        
        old_phase = self.current_phase
        
        # Log a transicao
        self.logger.info(f"Transitioning from '{old_phase}' to '{target_phase}'",
                         extra={
                             "project_id": self.project_id,
                             "from_phase": old_phase,
                             "to_phase": target_phase
                         })
        
        # Atualiza estado atual
        self.current_phase = target_phase
        
        # Salva checkpoint
        state = self._get_current_state()
        state.last_updated = datetime.utcnow()
        state.progress = 25 if old_phase == "identification" else \
                           50 if old_phase == "screening" else \
                           75 if old_phase == "eligibility" else 100
        
        self.db_session.commit()
        
        # Registra na historia
        self.state_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "from": old_phase,
            "to": target_phase,
            "project_id": self.project_id
        })
        
        self.logger.info(f"Transition complete: {old_phase} -> {target_phase}",
                         extra={
                             "project_id": self.project_id,
                             "current_progress": state.progress
                         })
    
    def get_state_json(self) -> str:
        """Serializa estado atual para JSON."""
        state = self._get_current_state()
        
        last_updated = None
        if hasattr(state, 'last_updated') and state.last_updated:
            last_updated = str(state.last_updated.isoformat())
        
        return json.dumps({
            "project_id": self.project_id,
            "phase": self.current_phase,
            "history": self.state_history[-10:],  # Ultimos 10 eventos
            "last_updated": last_updated
        }, indent=2)
    
    def load_state_json(self, json_str: str):
        """Carrega estado a partir de JSON string."""
        data = json.loads(json_str)
        
        self.project_id = data.get("project_id")
        self.current_phase = data.get("phase")
        self.state_history = data.get("history", [])
    
    def reset(self):
        """Reseta o estado do orquestrador."""
        self.current_phase = None
        self.state_history.clear()
        
        # Remove estados antigos no banco (opcional)
        states_to_delete = [s for s in self.db_session.query(PipelineState).
                          filter_by(project_id=self.project_id)]
        for state in states_to_delete:
            self.db_session.delete(state)
        
        self.logger.info("Orchestrator reset complete",
                         extra={"project_id": self.project_id})


# Factory function para criar instancias do OrchestratorAgent
def create_orchestrator(project_id: int, db_session: Session) -> OrchestratorAgent:
    """Cria uma nova instancia do OrchestratorAgent."""
    return OrchestratorAgent(project_id=project_id, db_session=db_session)


__all__ = ["OrchestratorAgent", "PipelinePhase", "create_orchestrator"]
