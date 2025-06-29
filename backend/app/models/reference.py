"""
Reference data SQLAlchemy models
===============================
Models for reference/lookup tables.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import List

from app.database.connection import Base


class DataSource(Base):
    """
    Sources of strain data (laboratories, publications, etc.)
    """
    __tablename__ = "data_sources"
    __table_args__ = {"schema": "lysobacter"}
    
    source_id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(200), nullable=False)
    source_type = Column(String(50), nullable=True)  # 'laboratory', 'publication', 'database'
    contact_info = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # Relationships
    strains = relationship("Strain", back_populates="data_source")
    
    def __repr__(self) -> str:
        return f"<DataSource(id={self.source_id}, name='{self.source_name}', type='{self.source_type}')>"
    
    @property
    def strain_count(self) -> int:
        """Get number of strains from this source"""
        return len(self.strains) if self.strains else 0
    
    @property
    def display_name(self) -> str:
        """Get display name with type if available"""
        if self.source_type:
            return f"{self.source_name} ({self.source_type})"
        return self.source_name


class CollectionNumber(Base):
    """
    Collection numbers/identifiers (DSM, ATCC, etc.)
    """
    __tablename__ = "collection_numbers"
    __table_args__ = {"schema": "lysobacter"}
    
    collection_number_id = Column(Integer, primary_key=True, index=True)
    collection_code = Column(String(50), nullable=False, index=True)  # DSM, ATCC, etc.
    collection_number = Column(String(100), nullable=False)
    collection_name = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # Relationships
    strain_collections = relationship("StrainCollection", back_populates="collection_number")
    
    def __repr__(self) -> str:
        return f"<CollectionNumber(id={self.collection_number_id}, code='{self.collection_code}', number='{self.collection_number}')>"
    
    @property
    def full_identifier(self) -> str:
        """Get full collection identifier"""
        return f"{self.collection_code} {self.collection_number}"
    
    @property
    def display_name(self) -> str:
        """Get display name with collection name if available"""
        if self.collection_name:
            return f"{self.full_identifier} - {self.collection_name}"
        return self.full_identifier
    
    @property
    def strain_count(self) -> int:
        """Get number of strains with this collection number"""
        return len(self.strain_collections) if self.strain_collections else 0 