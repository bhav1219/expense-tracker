
from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "expense.db"
DEFAULT_BUDGET = 10000


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL UNIQUE,
            amount REAL NOT NULL
        )
    """)

    conn.close()


@app.route("/")
def home():
    conn = get_connection()

    rows = conn.execute("""
        SELECT name, amount, category, date
        FROM expenses
        ORDER BY date DESC, rowid DESC
    """).fetchall()

    current_month = datetime.now().strftime("%Y-%m")
    current_month_label = datetime.now().strftime("%B %Y")

    budget_row = conn.execute("""
        SELECT amount
        FROM budgets
        WHERE month = ?
    """, (current_month,)).fetchone()

    budget = budget_row["amount"] if budget_row else DEFAULT_BUDGET

    month_data = {}

    for row in rows:
        date_value = row["date"]
        month_key = date_value[:7]

        try:
            month_label = datetime.strptime(
                month_key, "%Y-%m"
            ).strftime("%B %Y")
        except ValueError:
            month_label = month_key

        if month_key not in month_data:
            month_data[month_key] = {
                "key": month_key,
                "label": month_label,
                "total": 0,
                "count": 0,
                "expenses": []
            }

        expense = {
            "name": row["name"],
            "amount": row["amount"],
            "category": row["category"],
            "date": row["date"]
        }

        month_data[month_key]["expenses"].append(expense)
        month_data[month_key]["total"] += row["amount"]
        month_data[month_key]["count"] += 1

    month_groups = sorted(
        month_data.values(),
        key=lambda item: item["key"],
        reverse=True
    )

    current_total = month_data.get(
        current_month, {"total": 0}
    )["total"]

    balance = budget - current_total

    conn.close()

    return render_template(
        "index.html",
        month_groups=month_groups,
        current_month=current_month,
        current_month_label=current_month_label,
        total=current_total,
        budget=budget,
        balance=balance
    )


@app.route("/add_expense", methods=["POST"])
def add_expense():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    category = str(data.get("category", "")).strip()
    date_value = str(data.get("date", "")).strip()

    try:
        amount = float(data.get("amount", 0))
        datetime.strptime(date_value, "%Y-%m-%d")
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount or date"}), 400

    if not name or not category or amount <= 0:
        return jsonify({"error": "Please enter valid details"}), 400

    conn = get_connection()

    conn.execute("""
        INSERT INTO expenses (name, amount, category, date)
        VALUES (?, ?, ?, ?)
    """, (name, amount, category, date_value))

    conn.commit()
    conn.close()

    return jsonify({"message": "Expense added successfully"})


@app.route("/set_budget", methods=["POST"])
def set_budget():
    data = request.get_json(silent=True) or {}

    try:
        amount = float(data.get("amount", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid budget amount"}), 400

    if amount <= 0:
        return jsonify({"error": "Budget must be greater than 0"}), 400

    month = datetime.now().strftime("%Y-%m")

    conn = get_connection()

    conn.execute("""
        INSERT INTO budgets (month, amount)
        VALUES (?, ?)
        ON CONFLICT(month)
        DO UPDATE SET amount = excluded.amount
    """, (month, amount))

    conn.commit()
    conn.close()

    return jsonify({"message": "Budget updated successfully"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
