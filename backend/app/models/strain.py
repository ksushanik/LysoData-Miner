"""
Strain-related SQLAlchemy models
===============================
Models for strains table and related collections.
"""

from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from typing import Optional, List

from app.database.connection import Base


class Strain(Base):
    """
    Main strains table model
    Represents a bacterial strain with its basic properties
    """
    __tablename__ = "strains"
    __table_args__ = {"schema": "lysobacter"}
    
    strain_id = Column(Integer, primary_key=True, index=True)
    strain_identifier = Column(String(100), unique=True, nullable=False, index=True)
    scientific_name = Column(String(200), nullable=True)
    common_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    isolation_source = Column(Text, nullable=True)
    isolation_location = Column(Text, nullable=True)
    isolation_date = Column(Date, nullable=True)
    source_id = Column(Integer, ForeignKey("lysobacter.data_sources.source_id"), nullable=True)
    gc_content_min = Column(DECIMAL(5,2), nullable=True)
    gc_content_max = Column(DECIMAL(5,2), nullable=True)
    gc_content_optimal = Column(DECIMAL(5,2), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # New fields for duplicate handling
    is_duplicate = Column(Boolean, default=False, nullable=False, index=True)
    master_strain_id = Column(Integer, ForeignKey("lysobacter.strains.strain_id"), nullable=True)
    
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="strains")
    collections = relationship("StrainCollection", back_populates="strain", cascade="all, delete-orphan")
    boolean_results = relationship("TestResultBoolean", back_populates="strain", cascade="all, delete-orphan")
    numeric_results = relationship("TestResultNumeric", back_populates="strain", cascade="all, delete-orphan")
    text_results = relationship("TestResultText", back_populates="strain", cascade="all, delete-orphan")
    
    # Relationships for master/duplicate strains
    master_strain = relationship("Strain", remote_side=[strain_id], back_populates="duplicates")
    duplicates = relationship("Strain", back_populates="master_strain")
    
    def __repr__(self) -> str:
        return f"<Strain(id={self.strain_id}, identifier='{self.strain_identifier}', name='{self.scientific_name}')>"
    
    @property
    def display_name(self) -> str:
        """Get display name for the strain"""
        if self.scientific_name:
            return f"{self.strain_identifier} - {self.scientific_name}"
        return self.strain_identifier
    
    @property
    def gc_content_range(self) -> Optional[str]:
        """Get GC content as a formatted range string"""
        if self.gc_content_min and self.gc_content_max:
            if self.gc_content_min == self.gc_content_max:
                return f"{self.gc_content_min}%"
            return f"{self.gc_content_min}-{self.gc_content_max}%"
        elif self.gc_content_optimal:
            return f"{self.gc_content_optimal}%"
        return None


class StrainCollection(Base):
    """
    Link table between strains and collection numbers
    Many-to-many relationship with additional metadata
    """
    __tablename__ = "strain_collections"
    __table_args__ = {"schema": "lysobacter"}
    
    strain_id = Column(Integer, ForeignKey("lysobacter.strains.strain_id", ondelete="CASCADE"), primary_key=True)
    collection_number_id = Column(Integer, ForeignKey("lysobacter.collection_numbers.collection_number_id"), primary_key=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # Relationships
    strain = relationship("Strain", back_populates="collections")
    collection_number = relationship("CollectionNumber", back_populates="strain_collections")
    
    def __repr__(self) -> str:
        return f"<StrainCollection(strain_id={self.strain_id}, collection_id={self.collection_number_id}, primary={self.is_primary})>" 