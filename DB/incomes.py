#!/usr/bin/env python3
"""
Expenses methodes
"""
from DB.tables import Income
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List
from flask import jsonify
from sqlalchemy import text

class IncomesDB:
    """Separate DB class for managing expenses."""
    
    def __init__(self, session):
        """Initialize with an existing session."""
        self._session = session
    
    def add_income(self, amount: float, user_id: int, frequency: str, name: str):
        """create a new goal"""
        time = datetime.now()
        id = str(uuid4())
        if frequency == "daily":
            next_occurrence = time + timedelta(days=1)
        elif frequency == "weekly":
            next_occurrence = time + timedelta(weeks=1)
        elif frequency == "monthly":
            next_occurrence = time.replace(month=time.month % 12 + 1)
        elif frequency == "yearly":
            next_occurrence = time.replace(year=time.year + 1)
        else:
            next_occurrence = None
            frequency = None
        income = Income(id=id, amount=amount, date=time, user_id=user_id, frequency=frequency, next_date=next_occurrence, name=name)
        self._session.add(income)
        self._session.commit()
        return income
    
    def findincomebyid(self, **kwargs: List[any]):
        """find a goal by its a specific attribute"""
        return self._session.query(Income).filter_by(**kwargs).first()
    
    def modify(self, income_id: str, **kwargs: List[any]):
        """modify an expense in the database."""
        income = self.findincomebyid(id=income_id)
        if income is None:
            return None
        for key, value in kwargs.items():
            setattr(income, key, value)
        self._session.commit()
        return income
    
    def deleteincome(self, income_id: str):
        """delete an income from the database."""
        income = self.findincomebyid(id=income_id)
        if income is None:
            return None
        self._session.delete(income)
        self._session.commit()
        return
    
    def findincomes(self, user_id: int) -> List[Income]:
        """find all incomes for a specific user."""
        incomes = self._session.query(Income).filter_by(user_id=user_id).all()
        if incomes is None:
            return None
        return incomes
    
    def findallincome(self, user_id: int):
        """find all incomes for a specific user."""
        result = self._session.query(Income).filter_by(user_id=user_id).all()
        data = [{"amount": float(row.amount), "name": row.name} for row in result]
        return data
    
    def total_income(self, user_id: int):
        """find all daily incomes for a specific user."""
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Dynamic query using f-string
        query = f"""
        SELECT 
            SUM(amount) AS total_amount
        FROM 
            incomes
        WHERE 
            user_id = '{user_id}'
            AND date >= DATE('now', '-30 days')
        """
        # Execute the query
        results = self._session.execute(text(query)).fetchall()

        # Convert results to a list of dictionaries
        data = [{"total_amount": row[0]} for row in results]
        return data[0]