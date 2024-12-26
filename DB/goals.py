#!/usr/bin/env python3
"""
Expenses methodes
"""
from DB.tables import Goal
from datetime import datetime
from uuid import uuid4
from typing import List
from flask import jsonify
from sqlalchemy import text
import requests

class GoalsDB:
    """Separate DB class for managing goals."""
    
    def __init__(self, session):
        """Initialize with an existing session."""
        self._session = session
    
    def add_goal(self, amount: float, user_id: int):
        """create a new goal"""
        time = datetime.now()
        id = str(uuid4())
        goal = Goal(id=id, amount=amount, date=time, user_id=user_id)
        self._session.add(goal)
        self._session.commit()
        return goal
    
    def findgoalbyid(self, **kwargs: List[any]):
        """find a goal by its a specific attribute"""
        return self._session.query(Goal).filter_by(**kwargs).first()
    
    def findallgoals(self, user_id: int):
        """find all goals for a specific user"""
        return self._session.query(Goal).filter_by(user_id=user_id).all()
    
    def modify(self, goalid: int, amount: float):
        """modify an expense in the database"""
        goal = self.findgoalbyid(id=goalid)
        if goal is None:
            return None
        goal.amount = amount
        self._session.commit()
        return goal
    
    def deletegoal(self, goalid: int):
        """delete an expense from the database"""
        goal = self.findgoalbyid(id=goalid)
        if goal is None:
            return None
        self._session.delete(goal)
        self._session.commit()

    def monthgoal(self, user_id: int):
        """find all daily expenses for a specific user"""
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Dynamic query using f-string
        query = f"""
        SELECT 
            SUM(amount) AS total_amount
        FROM 
            goals
        WHERE 
            user_id = '{user_id}'
            AND date >= DATE('now', '-30 days')
        """
        # Execute the query
        results = self._session.execute(text(query)).fetchall()

        # Convert results to a list of dictionaries
        data = [{"total_amount": row[0]} for row in results]
        return data[0]
    
    def comparison(self, user_id: int, totalexpenses: float):
        """Calculates the difference between the total expenses and the user's goal."""
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Retrieve the user's monthly goal (budget)
        goal = self.monthgoal(user_id)

        if goal is None:
            return jsonify({"error": "Goal not set"}), 400
        
        goal = goal["total_amount"]
        totalexpenses = totalexpenses["total_amount"]

        # Calculate the difference between total expenses and the goal
        difference = totalexpenses - goal

        status = ""
        message = ""

        # Provide a more detailed response
        if difference > 0:
            status = "Over budget"
            message = f"You've exceeded your budget by ${difference:.2f}."
        elif difference < 0:
            status = "Under budget"
            message = f"You are under budget by ${abs(difference):.2f}."
        else:
            status = "On budget"
            message = "You are exactly on budget."

        return jsonify({
            "status": status,
            "message": message,
            "total_expenses": totalexpenses,
            "budget": goal
        })
