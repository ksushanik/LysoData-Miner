"""
Test-related SQLAlchemy models
==============================
Models for test categories, tests, and test values.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import List, Optional

from app.database.connection import Base


class TestCategory(Base):
    """
    Test categories for grouping related parameters
    Examples: Morphological, Physiological, Biochemical
    """
    __tablename__ = "test_categories"
    __table_args__ = {"schema": "lysobacter"}
    
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # Relationships
    tests = relationship("Test", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<TestCategory(id={self.category_id}, name='{self.category_name}')>"
    
    @property
    def test_count(self) -> int:
        """Get number of tests in this category"""
        return len(self.tests) if self.tests else 0


class Test(Base):
    """
    Individual tests/parameters that can be performed
    Each test belongs to a category and has a specific type
    """
    __tablename__ = "tests"
    __table_args__ = {"schema": "lysobacter"}
    
    test_id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("lysobacter.test_categories.category_id"), nullable=False, index=True)
    test_name = Column(String(150), nullable=False)
    test_code = Column(String(50), unique=True, nullable=True, index=True)
    test_type = Column(String(20), nullable=False, index=True)  # 'boolean', 'numeric', 'text'
    description = Column(Text, nullable=True)
    measurement_unit = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # Relationships
    category = relationship("TestCategory", back_populates="tests")
    test_values = relationship("TestValue", back_populates="test", cascade="all, delete-orphan")
    boolean_results = relationship("TestResultBoolean", back_populates="test")
    numeric_results = relationship("TestResultNumeric", back_populates="test")
    text_results = relationship("TestResultText", back_populates="test")
    
    def __repr__(self) -> str:
        return f"<Test(id={self.test_id}, name='{self.test_name}', type='{self.test_type}')>"
    
    @property
    def display_name(self) -> str:
        """Get display name with measurement unit if applicable"""
        if self.measurement_unit and self.test_type == 'numeric':
            return f"{self.test_name} ({self.measurement_unit})"
        return self.test_name
    
    @property
    def is_boolean(self) -> bool:
        """Check if this is a boolean test"""
        return self.test_type == 'boolean'
    
    @property
    def is_numeric(self) -> bool:
        """Check if this is a numeric test"""
        return self.test_type == 'numeric'
    
    @property
    def is_text(self) -> bool:
        """Check if this is a text test"""
        return self.test_type == 'text'


class TestValue(Base):
    """
    Possible values for boolean/categorical tests
    Examples: '+', '-', '+/-', 'n.d.' for boolean tests
    """
    __tablename__ = "test_values"
    __table_args__ = {"schema": "lysobacter"}
    
    value_id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("lysobacter.tests.test_id", ondelete="CASCADE"), nullable=False, index=True)
    value_code = Column(String(10), nullable=False)
    value_name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # Relationships
    test = relationship("Test", back_populates="test_values")
    boolean_results = relationship("TestResultBoolean", back_populates="test_value")
    
    def __repr__(self) -> str:
        return f"<TestValue(id={self.value_id}, code='{self.value_code}', name='{self.value_name}')>"
    
    @property
    def display_value(self) -> str:
        """Get display value combining code and name"""
        if self.value_code != self.value_name:
            return f"{self.value_code} ({self.value_name})"
        return self.value_code
    
    @property
    def is_positive(self) -> bool:
        """Check if this represents a positive result"""
        return self.value_code in ['+', 'positive', 'yes', 'true']
    
    @property
    def is_negative(self) -> bool:
        """Check if this represents a negative result"""
        return self.value_code in ['-', 'negative', 'no', 'false']
    
    @property
    def is_intermediate(self) -> bool:
        """Check if this represents an intermediate result"""
        return self.value_code in ['+/-', 'intermediate', 'weak', 'variable']
    
    @property
    def is_no_data(self) -> bool:
        """Check if this represents no data"""
        return self.value_code in ['n.d.', 'nd', 'no_data', 'unknown', 'not_tested'] 