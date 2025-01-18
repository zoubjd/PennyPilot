from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from DB.tables import Expense, Savings, User, Income
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
from sqlalchemy import text
from dateutil.relativedelta import relativedelta

# Use a sessionmaker to create new sessions when needed
SessionMaker = None

def initialize_session(engine):
    global SessionMaker
    SessionMaker = sessionmaker(bind=engine)

def add_recurring_expenses():
    """Automatically add recurring expenses."""
    with SessionMaker() as session:
        now = datetime.now()

        # Query recurring expenses whose next occurrence is due
        recurring_expenses = session.query(Expense).filter(
            Expense.next_occurrence <= now
        ).all()

        for expense in recurring_expenses:
            try:
                # Add a new expense entry for the recurring expense
                new_expense = Expense(
                    id=str(uuid4()),
                    category=expense.category,
                    amount=expense.amount,
                    date=now,
                    user_id=expense.user_id,
                    frequency=None,
                )
                session.add(new_expense)

                # Update the next_occurrence based on frequency
                if expense.frequency == "daily":
                    expense.next_occurrence += timedelta(days=1)
                elif expense.frequency == "weekly":
                    expense.next_occurrence += timedelta(weeks=1)
                elif expense.frequency == "monthly":
                    expense.next_occurrence += relativedelta(months=1)
                elif expense.frequency == "yearly":
                    expense.next_occurrence += relativedelta(years=1)

            except Exception as e:
                print(f"Error processing expense {expense.id}: {e}")

        session.commit()
def add_recurring_incomes():
    """Automatically add recurring incomes."""
    session = SessionMaker()
    try:
        now = datetime.now()

        # Query recurring incomes whose next occurrence is due
        recurring_incomes = session.query(Income).filter(
            Income.next_occurrence <= now
        ).all()

        for income in recurring_incomes:
            # Add a new income entry for the recurring income
            new_income = Income(
                id=str(uuid4()),
                name=income.name,
                amount=income.amount,
                date=now,
                user_id=income.user_id,
                frequency=None,
            )
            session.add(new_income)

            # Update the next_occurrence based on frequency
            if income.frequency == "daily":
                income.next_occurrence += timedelta(days=1)
            elif income.frequency == "weekly":
                income.next_occurrence += timedelta(weeks=1)
            elif income.frequency == "monthly":
                income.next_occurrence += relativedelta(months=1)
            elif income.frequency == "yearly":
                income.next_occurrence += relativedelta(years=1)

        session.commit()
    except Exception as e:
        print(f"Error in add_recurring_incomes: {e}")
    finally:
        session.close()

def add_savings_at_end_of_month():
    """Automatically add savings for all users at the end of the month."""
    session = SessionMaker()
    try:
        now = datetime.now()
        if now.day == 1:  # Run only on the first day of the month
            users = session.query(User).all()
            # to fix income and expense to use queries for just the last 30 days 
            # add the same as reccuring expenses in incomes

            for user in users:
                query = f"""
                SELECT 
                    SUM(amount) AS total_amount
                FROM 
                    incomes
                WHERE 
                    user_id = '{user.id}'
                    AND date >= DATE('now', '-30 days')
                """
                # Execute the query
                total_income = session.execute(text(query)).fetchall()
                total_income = total_income[0][0]
                query = f"""
                SELECT 
                    DATE(date) AS day, 
                    SUM(amount) AS total_spent
                FROM 
                    expenses
                WHERE 
                    user_id = '{user.id}'
                    AND date >= DATE('now', '-30 days')
                GROUP BY 
                    DATE(date)
                ORDER BY 
                    DATE(date) ASC;
                """
    
                # Execute the query
                total_expenses = session.execute(text(query)).fetchall()
                total_expenses = total_expenses[0][0]

                savings_amount = total_income - total_expenses
                if savings_amount > 0:
                    new_savings = Savings(
                        id=str(uuid4()),
                        amount=savings_amount,
                        user_id=user.id,
                        date=now
                    )
                    session.add(new_savings)

            session.commit()
    except Exception as e:
        print(f"Error in add_savings_at_end_of_month: {e}")
    finally:
        session.close()

def start_scheduler(engine):
    """Start the APScheduler with SQLAlchemy job store."""
    global SessionMaker
    initialize_session(engine)

    # Use SQLAlchemyJobStore to persist jobs in the database
    jobstores = {
        'default': SQLAlchemyJobStore(engine=engine)
    }

    # Initialize the scheduler
    scheduler = BackgroundScheduler(jobstores=jobstores)
    scheduler.add_job(
        add_recurring_expenses,
        'interval',
        days=1,
        id='add_recurring_expenses',
        replace_existing=True
    )
    scheduler.add_job(
        add_recurring_incomes,
        'interval',
        days=1,
        id='add_recurring_incomes',
        replace_existing=True
    )
    scheduler.add_job(
        add_savings_at_end_of_month,
        'cron',
        day=1,
        hour=0,
        id='add_savings_at_end_of_month',
        replace_existing=True
    )

    scheduler.start()
    return scheduler
