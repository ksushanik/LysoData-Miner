"""
Test result SQLAlchemy models
=============================
Models for storing test results in different formats.
"""

from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date
from typing import Optional, Union, Any

from app.database.connection import Base


class TestResultBoolean(Base):
    """
    Boolean/categorical test results
    Links strain + test + value (e.g., positive/negative)
    """
    __tablename__ = "test_results_boolean"
    __table_args__ = {"schema": "lysobacter"}
    
    result_id = Column(Integer, primary_key=True, index=True)
    strain_id = Column(Integer, ForeignKey("lysobacter.strains.strain_id", ondelete="CASCADE"), nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("lysobacter.tests.test_id"), nullable=False, index=True)
    value_id = Column(Integer, ForeignKey("lysobacter.test_values.value_id"), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    confidence_level = Column(String(20), default='high', nullable=False)  # 'high', 'medium', 'low'
    tested_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
    
    # Relationships
    strain = relationship("Strain", back_populates="boolean_results")
    test = relationship("Test", back_populates="boolean_results")
    test_value = relationship("TestValue", back_populates="boolean_results")
    
    def __repr__(self) -> str:
        return f"<TestResultBoolean(strain_id={self.strain_id}, test_id={self.test_id}, value_id={self.value_id})>"
    
    @property
    def result_display(self) -> str:
        """Get human-readable result"""
        if self.test_value:
            return self.test_value.display_value
        return "Unknown"
    
    @property
    def is_positive(self) -> bool:
        """Check if result is positive"""
        return self.test_value.is_positive if self.test_value else False
    
    @property
    def is_negative(self) -> bool:
        """Check if result is negative"""
        return self.test_value.is_negative if self.test_value else False
    
    @property
    def has_data(self) -> bool:
        """Check if result has actual data (not 'no data')"""
        return not (self.test_value.is_no_data if self.test_value else True)


class TestResultNumeric(Base):
    """
    Numeric test results (temperature, pH, etc.)
    Supports minimum, maximum, optimal, and single values
    """
    __tablename__ = "test_results_numeric"
    __table_args__ = {"schema": "lysobacter"}
    
    result_id = Column(Integer, primary_key=True, index=True)
    strain_id = Column(Integer, ForeignKey("lysobacter.strains.strain_id", ondelete="CASCADE"), nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("lysobacter.tests.test_id"), nullable=False, index=True)
    value_type = Column(String(20), nullable=False)  # 'minimum', 'maximum', 'optimal', 'single'
    numeric_value = Column(DECIMAL(10,4), nullable=False)
    measurement_unit = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    confidence_level = Column(String(20), default='high', nullable=False)
    tested_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
    
    # Relationships
    strain = relationship("Strain", back_populates="numeric_results")
    test = relationship("Test", back_populates="numeric_results")
    
    def __repr__(self) -> str:
        return f"<TestResultNumeric(strain_id={self.strain_id}, test_id={self.test_id}, value={self.numeric_value}, type='{self.value_type}')>"
    
    @property
    def result_display(self) -> str:
        """Get formatted numeric result with unit"""
        unit = self.measurement_unit or (self.test.measurement_unit if self.test else "")
        if unit:
            return f"{self.numeric_value} {unit}"
        return str(self.numeric_value)
    
    @property
    def is_minimum(self) -> bool:
        """Check if this is a minimum value"""
        return self.value_type == 'minimum'
    
    @property
    def is_maximum(self) -> bool:
        """Check if this is a maximum value"""
        return self.value_type == 'maximum'
    
    @property
    def is_optimal(self) -> bool:
        """Check if this is an optimal value"""
        return self.value_type == 'optimal'
    
    @property
    def is_single(self) -> bool:
        """Check if this is a single value"""
        return self.value_type == 'single'


class TestResultText(Base):
    """
    Text-based test results
    For free-form data that doesn't fit boolean or numeric categories
    """
    __tablename__ = "test_results_text"
    __table_args__ = {"schema": "lysobacter"}
    
    result_id = Column(Integer, primary_key=True, index=True)
    strain_id = Column(Integer, ForeignKey("lysobacter.strains.strain_id", ondelete="CASCADE"), nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("lysobacter.tests.test_id"), nullable=False, index=True)
    text_value = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    confidence_level = Column(String(20), default='high', nullable=False)
    tested_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
    
    # Relationships
    strain = relationship("Strain", back_populates="text_results")
    test = relationship("Test", back_populates="text_results")
    
    def __repr__(self) -> str:
        return f"<TestResultText(strain_id={self.strain_id}, test_id={self.test_id}, value='{self.text_value[:50]}...')>"
    
    @property
    def result_display(self) -> str:
        """Get formatted text result"""
        return self.text_value
    
    @property
    def text_preview(self) -> str:
        """Get preview of text content (first 100 chars)"""
        if len(self.text_value) <= 100:
            return self.text_value
        return self.text_value[:97] + "..."
    
    @property
    def has_data(self) -> bool:
        """Check if result has actual data"""
        return bool(self.text_value and self.text_value.strip())
    
    @property
    def word_count(self) -> int:
        """Get word count of text value"""
        return len(self.text_value.split()) if self.text_value else 0 