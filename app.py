#!/usr/bin/env python3
"""
Main file
"""
from flask import Flask, jsonify, request, redirect, abort, make_response, url_for, render_template, flash
from DB.auth import Auth
from flask_babel import Babel
from datetime import datetime
from DB.expenses import ExpensesDB
from DB.goals import GoalsDB
from DB.incomes import IncomesDB
from DB.savings import SavingsDB
from tasks.automation import start_scheduler


AUTH = Auth()
expenses_db = ExpensesDB(AUTH._db._session)
goals_db = GoalsDB(AUTH._db._session)
income_db = IncomesDB(AUTH._db._session)
app = Flask(__name__)
app.secret_key = "my_secret_key" 


@app.route('/', strict_slashes=False)
def hello():
    """the main route"""
    return render_template("index.html")

@app.route('/home', strict_slashes=False)
def home():
    """the main route"""
    user = AUTH.get_user_from_session_id(request.cookies.get('session_id'))
    if user is not None:
        return render_template("home.html", user=user)
    return redirect("/login")



@app.route('/register', methods=['GET', 'POST'], strict_slashes=False)
def register():
    """the register route"""
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = AUTH._db.find_user_by(email=email)
        if user is not None:
            error = "User already exists"
            return render_template("login.html", error=error)
        else:
            user = AUTH.register_user(email, password)
            #to be redirect to the main page when created
            user_name = request.form.get('user_name')
            user.user_name = user_name
            zakaat = request.form.get('Zakaat')
            if zakaat == 'yes':
                user.zakaat = True
            # Set created_at to the current datetime object
            user.created_at = datetime.utcnow() 
            AUTH._db._session.commit()
            session_id = AUTH.create_session(user.email)
            resp = make_response(redirect('/home'))
            resp.set_cookie('session_id', session_id)
            print(user)
            return resp

    return render_template("login.html", error=error)

@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    """the login route"""
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if AUTH.valid_login(email, password):
            user = AUTH._db.find_user_by(email=email)
            session_id = AUTH.create_session(user.email)
            resp = make_response(redirect('home/'))
            resp.set_cookie('session_id', session_id)
            return resp
        else:
            error = "Invalid email or password"
    return render_template("login.html", error=error)


@app.route('/logout', methods=['GET'], strict_slashes=False)
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
        return redirect('/login')
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        return jsonify({"message": "No User found"}), 403
    return jsonify(user.to_dict()), 200


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
            print(request.form) 
            category = request.form.get('category')
            amount = float(request.form.get('amount'))
            frequency = request.form.get('frequency')
            if frequency not in ['once', 'weekly', 'monthly', 'yearly']:
                frequency = 'once'
            expenses_db.add_expense(category=category, amount=amount, user_id=user.id, frequency=frequency)
            return redirect('/expenses')
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

@app.route('/expenses/daily', methods=['GET'], strict_slashes=False)
def dailysummary():
    '''creates the summary of data based on date ana category'''
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        dailyspend = expenses_db.daily_expenses(user.id)
        return dailyspend
    return None
@app.route('/expenses/category', methods=['GET'], strict_slashes=False)
def categorysummary():
    '''creates the summary of data based on date ana category'''
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        income = income_db.total_income(user.id)
        totalexpenses = expenses_db.onetimeuseexpenses(user.id)
        savings = income["total_amount"] - totalexpenses
        incomes = income_db.findallincome(user.id)
        categoryspend = expenses_db.expenses_by_category(user.id, savings, incomes)
        return categoryspend
    return None

@app.route('/goals', methods=['GET'], strict_slashes=False)
def allgoals():
    """get all the goals for the user"""
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        return render_template("login.html")
    goals = goals_db.findallgoals(user.id)
    return render_template("goals.html", user=user, goals=goals)

@app.route('/addgoal', methods=['GET' ,'POST'], strict_slashes=False)
def addgoal():
    """Add a new goal."""
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user is not None:
        if request.method == 'POST':
            amount = float(request.form.get('amount'))   
            goals_db.add_goal(amount=amount, user_id=user.id)
            return redirect('/goals')
        return render_template("addgoal.html", user=user)
    return render_template("login.html")

@app.route('/goals/delete/<goal_id>', methods=['POST'], strict_slashes=False)
def deletegoals(goal_id):
    """Delete a specific goals."""
    goals_db.deletegoal(goal_id)
    return redirect("/goals")

@app.route('/goals/<goal_id>', methods=['GET'], strict_slashes=False)
def getspecificgoal(goal_id):
    """View and modify a specific expense."""
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user is not None:
        goal = goals_db.findgoalbyid(id=goal_id)
        if goal is None:
            return redirect("/goals")
        return render_template("specific_goal.html", goal=goal)
    return render_template("login.html")

@app.route('/goals/modify/<goal_id>', methods=['POST'], strict_slashes=False)
def modifygoal(goal_id):
    """Modify a specific expense."""
    goal = goals_db.findgoalbyid(id=goal_id)
    if goal is None:
        return redirect("/goals")
    
    amount = float(request.form.get('amount'))
    goals_db.modify(goal_id, amount=amount)
    return redirect("/goals")

@app.route('/goalsummary', methods=['GET'], strict_slashes=False)
def goalsummary():
    """summerise the goals for the user"""
    """api point for the frontend homepage"""
    user = AUTH.get_user_from_session_id(request.cookies.get('session_id'))
    if user is not None:
        totalexpenses = expenses_db.total_expenses(user.id)
        totalgoals = goals_db.comparison(user.id, totalexpenses)
        return totalgoals
    return None

@app.route('/incomes', methods=['GET'], strict_slashes=False)
def allincomes():
    """get all the incomes for the user"""
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        return render_template("login.html")
    incomes = income_db.findincomes(user.id)
    return render_template("incomes.html", user=user, incomes=incomes)

@app.route('/addincome', methods=['GET' ,'POST'], strict_slashes=False)
def addincome():
    """Add a new income."""
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user is not None:
        if request.method == 'POST':
            amount = float(request.form.get('amount'))   
            name = request.form.get('name')
            frequency = request.form.get('frequency') or 'once'
            income_db.add_income(amount=amount, user_id=user.id, name=name, frequency=frequency)
            return redirect('/incomes')
        return render_template("addincome.html", user=user)
    return render_template("login.html")

@app.route('/income/delete/<income_id>', methods=['POST'], strict_slashes=False)
def deleteincome(income_id):
    """Delete a specific income."""
    income_db.deleteincome(income_id)
    return redirect("/incomes")

@app.route('/income/<income_id>', methods=['GET'], strict_slashes=False)
def getspecificincome(income_id):
    """View and modify a specific income."""
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user is not None:
        income = income_db.findincomebyid(id=income_id)
        if income is None:
            return redirect("/incomes")
        return render_template("specific_income.html", income=income)
    return render_template("login.html")

@app.route('/income/modify/<income_id>', methods=['POST'], strict_slashes=False)
def modifyincome(income_id):
    """Modify a specific income."""
    income = income_db.findincomebyid(id=income_id)
    if income is None:
        return redirect("/incomes")
    
    amount = float(request.form.get('amount'))
    frequency = request.form.get('frequency')
    name = request.form.get('name')
    income_db.modify(income_id, amount=amount, frequency=frequency, name=name)
    return redirect("/incomes")

@app.route('/savings', methods=['GET'], strict_slashes=False)
def savings():
    """get all the savings for the user"""
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        return render_template("login.html")
    savings = SavingsDB.findallsavings(user.id)
    return render_template("savings.html", user=user, savings=savings)

@app.route('/zakaat', methods=['GET'], strict_slashes=False)
def zakaat():
    """path for the zakaat page"""
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        return render_template("login.html")
    zakaat = SavingsDB.calculate_zakaat(user.id)
    return render_template("zakaat.html", user=user, zakaat=zakaat)









if __name__ == "__main__":
    start_scheduler(engine=AUTH._db._engine)
    app.run(host="0.0.0.0", port=5000)
