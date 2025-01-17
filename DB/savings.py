#!/usr/bin/env python3
"""
Expenses methodes
"""
from DB.tables import Savings
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List
from flask import jsonify
from sqlalchemy import text

class SavingsDB:
    """Separate DB class for managing expenses."""
    
    def __init__(self, session):
        """Initialize with an existing session."""
        self._session = session

    def add_savings(self, amount: float, user_id: int):
        """Add an expense to the database."""
        savings = Savings(amount=amount, user_id=user_id)
        self._session.add(savings)
        self._session.commit()
        return savings
    
    def findallsavings(self, user_id: int):
        """find all savings for a specific user."""
        result = self._session.query(Savings).filter_by(user_id=user_id).all()
        return result
    
    def calculate_zakaat(self, user_id: int) -> float:
        """find if user is qualified for zakaat"""
        query = f"""
        SELECT 
            SUM(amount) AS total_amount
        FROM 
            savings
        WHERE 
            user_id = '{user_id}'
            AND date >= DATE('now', '-12 months')
        """

        results = self._session.execute(text(query)).fetchall()
        result = results[0][0]
        goldprice = 85.93 * 89
        if result > goldprice:
            price_to_pay = result * 0.025
            return price_to_pay
        return None    
