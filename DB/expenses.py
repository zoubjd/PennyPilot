#!/usr/bin/env python3
"""
Expenses methodes
"""
from DB.tables import Expense
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List
from flask import jsonify
from sqlalchemy import text

class ExpensesDB:
    """Separate DB class for managing expenses."""
    
    def __init__(self, session):
        """Initialize with an existing session."""
        self._session = session
    
    def add_expense(self, category: str, amount: float, user_id: int, frequency: str):
        """Add an expense to the database."""
        time = datetime.now()
        id = str(uuid4())
        next_occurrence = None

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
        expense = Expense(id=id, category=category, amount=amount, date=time, user_id=user_id, frequency=frequency, next_date=next_occurrence)
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

    def daily_expenses(self, user_id: int) -> List[dict]:
        """find all daily expenses for a specific user."""
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Dynamic query using f-string
        query = f"""
        SELECT 
            DATE(date) AS day, 
            SUM(amount) AS total_spent
        FROM 
            expenses
        WHERE 
            user_id = '{user_id}'
            AND date >= DATE('now', '-30 days')
        GROUP BY 
            DATE(date)
        ORDER BY 
            DATE(date) ASC;
        """
    
        # Execute the query
        results = self._session.execute(text(query)).fetchall()

        # Convert results to a list of dictionaries
        data = [{"day": row[0], "total_spent": row[1]} for row in results]
        return jsonify(data)

    
    def expenses_by_category(self, user_id: int, savings: float, incomes: list[any]) -> List[Expense]:
        """find all expenses for a specific user."""
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        query = f"""
        SELECT 
            category, 
            SUM(amount) AS total_spent
        FROM 
            expenses
        WHERE 
            user_id = '{user_id}' 
            AND date >= DATE('now', '-15 days')
        GROUP BY 
            category
        ORDER BY 
            total_spent DESC;
        """
        results = self._session.execute(text(query)).fetchall()
    
        # Convert results to a list of dictionaries
        data = [{"from": "income", "category": row[0], "total_spent": row[1]} for row in results]
        data.append({"from": "income", "category": "savings", "total_spent": savings})
        for income in incomes:
            data.append({"from": income["name"], "category": "income", "total_spent": income["amount"]})
        return jsonify(data)
    
    def total_expenses(self, user_id: int) -> List[dict]:
        """find all daily expenses for a specific user."""
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Dynamic query using f-string
        query = f"""
        SELECT 
            SUM(amount) AS total_amount
        FROM 
            expenses
        WHERE 
            user_id = '{user_id}'
            AND date >= DATE('now', '-30 days')
        """
        # Execute the query
        results = self._session.execute(text(query)).fetchall()

        # Convert results to a list of dictionaries
        data = [{"total_amount": row[0]} for row in results]
        return data[0]

    def onetimeuseexpenses(self, user_id: int) -> List[dict]:
        """find all daily expenses for a specific user."""
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Dynamic query using f-string
        query = f"""
        SELECT 
            SUM(amount) AS total_amount
        FROM 
            expenses
        WHERE 
            user_id = '{user_id}'
            AND date >= DATE('now', '-30 days')
        """
        # Execute the query
        results = self._session.execute(text(query)).fetchall()

        # Convert results to a list of dictionaries
        return results[0][0]


