"""
Audit trail SQLAlchemy model
============================
Model for tracking changes to database records.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from typing import Dict, Any, Optional, List

from app.database.connection import Base


class AuditLog(Base):
    """
    Audit trail for tracking changes to database records
    """
    __tablename__ = "audit_log"
    __table_args__ = {"schema": "lysobacter"}
    
    log_id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)
    operation = Column(String(20), nullable=False, index=True)  # 'INSERT', 'UPDATE', 'DELETE'
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changed_by = Column(String(100), nullable=True)
    changed_at = Column(DateTime, default=func.current_timestamp(), nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.log_id}, table='{self.table_name}', operation='{self.operation}', record_id={self.record_id})>"
    
    @property
    def is_insert(self) -> bool:
        """Check if this is an INSERT operation"""
        return self.operation == 'INSERT'
    
    @property
    def is_update(self) -> bool:
        """Check if this is an UPDATE operation"""
        return self.operation == 'UPDATE'
    
    @property
    def is_delete(self) -> bool:
        """Check if this is a DELETE operation"""
        return self.operation == 'DELETE'
    
    def get_changed_fields(self) -> List[str]:
        """Get list of fields that were changed in UPDATE operations"""
        if not self.is_update or not self.old_values or not self.new_values:
            return []
        
        changed = []
        for key, new_value in self.new_values.items():
            old_value = self.old_values.get(key)
            if old_value != new_value:
                changed.append(key)
        
        return changed
    
    def get_field_changes(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed field changes for UPDATE operations"""
        if not self.is_update or not self.old_values or not self.new_values:
            return {}
        
        changes = {}
        for key, new_value in self.new_values.items():
            old_value = self.old_values.get(key)
            if old_value != new_value:
                changes[key] = {
                    "old": old_value,
                    "new": new_value
                }
        
        return changes 