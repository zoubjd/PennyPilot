from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from DB.tables import Expense, Savings, User
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

# Use a sessionmaker to create new sessions when needed
SessionMaker = None

def initialize_session(engine):
    global SessionMaker
    SessionMaker = sessionmaker(bind=engine)

def add_recurring_expenses():
    """Automatically add recurring expenses."""
    session = SessionMaker()
    try:
        now = datetime.now()

        # Query recurring expenses whose next occurrence is due
        recurring_expenses = session.query(Expense).filter(
            Expense.next_occurrence <= now
        ).all()

        for expense in recurring_expenses:
            # Add a new expense entry for the recurring expense
            new_expense = Expense(
                id=str(uuid4()),
                category=expense.category,
                amount=expense.amount,
                date=now,
                user_id=expense.user_id,
                frequency=expense.frequency,
            )
            session.add(new_expense)

            # Update the next_occurrence based on frequency
            if expense.frequency == "daily":
                expense.next_occurrence += timedelta(days=1)
            elif expense.frequency == "weekly":
                expense.next_occurrence += timedelta(weeks=1)
            elif expense.frequency == "monthly":
                # Handle end-of-month wrapping
                next_month = (expense.next_occurrence.month % 12) + 1
                year = expense.next_occurrence.year + (expense.next_occurrence.month // 12)
                expense.next_occurrence = expense.next_occurrence.replace(
                    month=next_month, year=year
                )
            elif expense.frequency == "yearly":
                expense.next_occurrence = expense.next_occurrence.replace(
                    year=expense.next_occurrence.year + 1
                )

            # Commit the updates
            session.add(expense)

        session.commit()
    except Exception as e:
        print(f"Error in add_recurring_expenses: {e}")
    finally:
        session.close()

def add_savings_at_end_of_month():
    """Automatically add savings for all users at the end of the month."""
    session = SessionMaker()
    try:
        now = datetime.now()
        if now.day == 1:  # Run only on the first day of the month
            users = session.query(User).all()

            for user in users:
                total_income = sum(income.amount for income in user.incomes)
                total_expenses = sum(expense.amount for expense in user.expenses)

                savings_amount = total_income - total_expenses
                if savings_amount > 0:
                    new_savings = Savings(
                        id=str(uuid4()),
                        amount=savings_amount,
                        user_id=user.id,
                        date=now
                    )

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
        add_savings_at_end_of_month,
        'cron',
        day=1,
        hour=0,
        id='add_savings_at_end_of_month',
        replace_existing=True
    )

    scheduler.start()
    return scheduler
