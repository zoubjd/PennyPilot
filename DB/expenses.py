#!/usr/bin/env python3
"""
Expenses methodes
"""
from DB.tables import Expense
from datetime import datetime
from uuid import uuid4
from typing import List

class ExpensesDB:
    """Separate DB class for managing expenses."""
    
    def __init__(self, session):
        """Initialize with an existing session."""
        self._session = session
    
    def add_expense(self, category: str, amount: float, user_id: int):
        """Add an expense to the database."""
        time = datetime.now()
        id = str(uuid4())
        expense = Expense(id=id, category=category, amount=amount, date=time, user_id=user_id)
        self._session.add(expense)
        self._session.commit()
        return expense
    
    def findexpensebyid(self, **kwargs: List[any]) -> Expense:
        """Find an expense by its a specific attribute."""
        expense = self._session.query(Expense).filter_by(**kwargs).first()
        if expense is None:
            return None
        return expense
    
    def findallexp(self, user_id: int) -> List[Expense]:
        """find all expenses for a specific user."""
        expenses = self._session.query(Expense).filter_by(user_id=user_id).all()
        if expenses is None:
            return None
        return expenses
    
    def modify(self, expid: int, **kwargs: List[any]) -> None:
        """modify an expense in the database."""
        expense = self.findexpensebyid(id=expid)
        if expense is None:
            return None
        for key, value in kwargs.items():
            setattr(expense, key, value)
        self._session.commit()
        return expense
    
    def deleteexp(self, expid: int) -> None:
        """delete an expense from the database."""
        expense = self.findexpensebyid(id=expid)
        if expense is None:
            return None
        self._session.delete(expense)
        self._session.commit()



