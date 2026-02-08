import sqlite3
from datetime import datetime, date
from typing import List, Dict, Tuple
import os

DB_FILE = "expenses.db"


def init_db():
    """Initialize database with schema"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with open("schema.sql", "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def save_expense(
    user_id: int,
    amount: float,
    category: str,
    description: str,
    expense_date: str = None,
) -> int:
    """Save an expense to database"""
    if expense_date is None:
        expense_date = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO expenses (user_id, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, amount, category, description, expense_date),
    )

    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return expense_id


def get_today_expenses(user_id: int) -> List[Dict]:
    """Get today's expenses for a user"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM expenses 
        WHERE user_id = ? AND date = date('now')
        ORDER BY created_at DESC
        """,
        (user_id,),
    )

    expenses = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return expenses


def get_week_expenses(user_id: int) -> List[Dict]:
    """Get this week's expenses for a user"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM expenses 
        WHERE user_id = ? AND date >= date('now', '-7 days')
        ORDER BY date DESC, created_at DESC
        """,
        (user_id,),
    )

    expenses = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return expenses


def get_month_expenses(user_id: int) -> List[Dict]:
    """Get this month's expenses for a user"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM expenses 
        WHERE user_id = ? AND date >= date('now', 'start of month')
        ORDER BY date DESC, created_at DESC
        """,
        (user_id,),
    )

    expenses = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return expenses


def get_category_summary(expenses: List[Dict]) -> Tuple[Dict[str, float], float]:
    """Get category-wise summary and total from expenses"""
    summary = {}
    total = 0.0

    for expense in expenses:
        category = expense["category"] or "Uncategorized"
        amount = expense["amount"]

        if category not in summary:
            summary[category] = 0.0

        summary[category] += amount
        total += amount

    return summary, total


# Initialize database on import
if not os.path.exists(DB_FILE):
    init_db()
