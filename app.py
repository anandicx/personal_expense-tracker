from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

DATABASE = "expenses.db"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route("/")
def index():

    conn = get_db()

    expenses = conn.execute("""
        SELECT * FROM expenses
        ORDER BY expense_date DESC, id DESC
    """).fetchall()

    total = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
    """).fetchone()[0]

    categories = conn.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        categories=categories
    )


# ---------------- ADD EXPENSE ----------------

@app.route("/add", methods=["GET", "POST"])
def add_expense():

    if request.method == "POST":

        expense_date = request.form["expense_date"]
        category = request.form["category"]
        description = request.form["description"]
        amount = request.form["amount"]

        conn = get_db()

        conn.execute("""
            INSERT INTO expenses
            (expense_date, category, description, amount)
            VALUES (?, ?, ?, ?)
        """, (
            expense_date,
            category,
            description,
            amount
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template(
        "add_expense.html",
        today=date.today().isoformat()
    )


# ---------------- DELETE EXPENSE ----------------

@app.route("/delete/<int:expense_id>")
def delete_expense(expense_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ---------------- RUN APP ----------------

if __name__ == "__main__":

    create_database()

    app.run(
        debug=True
    )