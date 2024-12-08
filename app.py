#!/usr/bin/env python3
"""
Main file
"""
from flask import Flask, jsonify, request, redirect, abort, make_response, url_for, render_template, flash
from DB.auth import Auth
from flask_babel import Babel
from datetime import datetime
from DB.expenses import ExpensesDB


AUTH = Auth()
expenses_db = ExpensesDB(AUTH._db._session)
app = Flask(__name__)
app.secret_key = "my_secret_key" 


@app.route('/', strict_slashes=False)
def hello():
    """the main route"""
    user = AUTH.get_user_from_session_id(request.cookies.get('session_id'))
    if user is not None:
        return render_template("index.html", user=user)
    return render_template("index.html")



@app.route('/register', methods=['GET', 'POST'], strict_slashes=False)
def register():
    """the register route"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = AUTH.register_user(email, password)
        if user is not None:
            #to be redirect to the main page when created
            user_name = request.form.get('user_name')
            user.user_name = user_name
            # Set created_at to the current datetime object
            user.created_at = datetime.utcnow() 
            AUTH._db._session.commit()
            session_id = AUTH.create_session(user.email)
            resp = make_response(redirect('/'))
            resp.set_cookie('session_id', session_id)
            return resp
        else:
            return flash("User already exists", "error")

    return render_template("login.html")

@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    """the login route"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if AUTH.valid_login(email, password):
            user = AUTH._db.find_user_by(email=email)
            session_id = AUTH.create_session(user.email)
            resp = make_response(redirect('/'))
            resp.set_cookie('session_id', session_id)
            return resp
        else:
            flash("Invalid email or password", "error")
    return render_template("login.html")


@app.route('/sessions', methods=['DELETE'], strict_slashes=False)
def logout():
    """the logout route"""
    session_id = request.cookies.get('session_id')
    if session_id is None:
        return jsonify({"message": "No session id found"}), 403
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        return jsonify({"message": "No User found"}), 403
    AUTH.destroy_session(user.id)
    return redirect("/")


@app.route('/profile', methods=['GET'], strict_slashes=False)
def profile():
    """user profile's link"""
    session_id = request.cookies.get('session_id')
    if session_id is None:
        return jsonify({"message": "No session id found"}), 403
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        return jsonify({"message": "No User found"}), 403
    return jsonify({"email": user.email}), 200


@app.route('/reset_password', methods=['POST'], strict_slashes=False)
def get_reset_password_token():
    """the way for the user to reset his password"""
    email = request.form.get('email')
    if email is None:
        abort(403)
    user = AUTH._db.find_user_by(email=email)
    if user is None:
        return jsonify({"message": "No user found with email"}), 403
    token = AUTH.get_reset_password_token(email)
    return jsonify({"email": email, "reset_token": token}), 200


@app.route('/reset_password', methods=['PUT'], strict_slashes=False)
def update_password():
    """updates the forgotten pwd"""
    email = request.form.get("email")
    tocken = request.form.get("reset_token")
    pwd = request.form.get("new_password")
    try:
        AUTH.update_password(tocken, pwd)
        return jsonify({"email": email, "message": "Password updated"}), 200
    except ValueError:
        return jsonify({"message": "Data entered not valid"}), 403
    
@app.route('/addexpense', methods=['GET', 'POST'], strict_slashes=False)
def addexpense():
    """Add a new expense."""
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user is not None:
        if request.method == 'POST':
            category = request.form.get('category')
            amount = float(request.form.get('amount'))
            expenses_db.add_expense(category=category, amount=amount, user_id=user.id)
            return redirect('/expenses', code=302)
        return render_template("addexpense.html", user=user)
    return render_template("login.html")

@app.route('/expenses', methods=['GET'], strict_slashes=False)
def getexpenses():
    """the expenses route"""
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user is not None:
        expenses = expenses_db.findallexp(user.id)
        return render_template("expenses.html", user=user, expenses=expenses)
    return render_template("login.html")

@app.route('/expenses/delete/<expense_id>', methods=['POST'], strict_slashes=False)
def deleteexpense(expense_id):
    """Delete a specific expense."""
    expenses_db.deleteexp(expense_id)
    return redirect("/expenses")


@app.route('/expenses/<expense_id>', methods=['GET'], strict_slashes=False)
def getspecificexpense(expense_id):
    """View and modify a specific expense."""
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user is not None:
        expense = expenses_db.findexpensebyid(id=expense_id)
        if expense is None:
            return redirect("/expenses")
        return render_template("specific_expense.html", expense=expense)
    return render_template("login.html")

@app.route('/expenses/modify/<expense_id>', methods=['POST'], strict_slashes=False)
def modifyexpense(expense_id):
    """Modify a specific expense."""
    expense = expenses_db.findexpensebyid(id=expense_id)
    if expense is None:
        return redirect("/expenses")
    
    category = request.form.get('category')
    amount = float(request.form.get('amount'))
    expenses_db.modify(expense_id, category=category, amount=amount)
    return redirect("/expenses")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
