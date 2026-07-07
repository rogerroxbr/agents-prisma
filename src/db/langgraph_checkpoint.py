"""LangGraph checkpoint saver for PostgreSQL."""
from typing import Dict, Any, Optional
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class SQLNodeCheckpointSaver:
    """Saves LangGraph state to PostgreSQL for fault-tolerant execution."""
    
    def __init__(self, engine=None):
        self.engine = engine
    
    async def save_checkpoint(
        self, 
        session: AsyncSession, 
        config: Dict[str, Any], 
        state: Dict[str, Any]
    ) -> int:
        """Save checkpoint to database.
        
        Args:
            session: SQLAlchemy async session
            config: Graph configuration (e.g., {"thread_id": "main"})
            state: Full TypedDict state snapshot
            
        Returns:
            Checkpoint ID
        """
        # Auto-increment parent_id for linear checkpoint chain
        last_checkpoint = await self._get_last_checkpoint(session, config)
        parent_id = last_checkpoint.id if last_checkpoint else None
        
        # Convert state to JSONB-compatible dict (remove non-serializable fields)
        clean_state = self._clean_state(state)
        
        checkpoint = LangGraphCheckpoint(
            config=json.dumps(config),
            parent_id=parent_id,
            state=clean_state,
            created_at=datetime.utcnow()
        )
        
        session.add(checkpoint)
        await session.commit()
        
        return checkpoint.id
    
    async def get_checkpoint(self, session: AsyncSession, config: Dict[str, Any]) -> Optional[int]:
        """Get last saved checkpoint for given config."""
        from src.db.models import LangGraphCheckpoint
        
        try:
            result = await session.execute(
                text("SELECT id FROM langgraph_checkpoints WHERE config = :config ORDER BY id DESC LIMIT 1"),
                {"config": json.dumps(config)}
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
    
    def _clean_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Remove non-serializable fields from state."""
        clean = {}
        for key, value in state.items():
            if isinstance(value, (dict, list)):
                try:
                    json.dumps(value)  # Test serializability
                    clean[key] = value
                except TypeError:
                    pass  # Skip non-serializable fields
            else:
                clean[key] = value
        return clean
    
    async def _get_last_checkpoint(self, session: AsyncSession, config: Dict[str, Any]) -> Optional['LangGraphCheckpoint']:
        """Get most recent checkpoint for given config."""
        from src.db.models import LangGraphCheckpoint
        
        try:
            result = await session.execute(
                text("SELECT id, state FROM langgraph_checkpoints WHERE config = :config ORDER BY id DESC LIMIT 1"),
                {"config": json.dumps(config)}
            )
            return result.scalar_one_or_none()
        except Exception:
            return None


__all__ = ["SQLNodeCheckpointSaver"]
