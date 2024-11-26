#!/usr/bin/env python3
"""
User module
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User Class"""

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
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
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    date = Column(Date, nullable=False)  # Use Date instead of String
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationship
    user = relationship('User', back_populates='expenses')


class Goal(Base):
    """Goal Class"""

    __tablename__ = 'goals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    date = Column(Date, nullable=False)  # Use Date instead of String
    achieved = Column(Boolean, default=False)  # Track goal status
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationship
    user = relationship('User', back_populates='goals')
