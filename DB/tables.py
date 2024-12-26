#!/usr/bin/env python3
"""
All modules
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()
from sqlalchemy import Column, String
import uuid  # Import for generating UUIDs

class User(Base):
    """User Class"""

    __tablename__ = 'users'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # String to store UUIDs
    email = Column(String(250), nullable=False)
    user_name = Column(String(250))
    hashed_password = Column(String(250), nullable=False)
    session_id = Column(String(250), nullable=True)
    reset_token = Column(String(250), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships with cascade delete
    expenses = relationship('Expense', back_populates='user', cascade="all, delete-orphan")
    goals = relationship('Goal', back_populates='user', cascade="all, delete-orphan")


class Expense(Base):
    """Expense Class"""

    __tablename__ = 'expenses'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # Use String for UUID
    category = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)  # Match with User's id type

    # Relationship
    user = relationship('User', back_populates='expenses')


class Goal(Base):
    """Goal Class"""

    __tablename__ = 'goals'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # Use String for UUID
    amount = Column(DECIMAL(10, 2), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    achieved = Column(Boolean, default=False)  # to be remouved before datawipe no need
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)  # Match with User's id type

    # Relationship
    user = relationship('User', back_populates='goals')
