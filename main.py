from fastmcp import FastMCP
import os
import sqlite3
import json

# -----------------------------
# Paths
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "expenses.db")
CATEGORIES_PATH = os.path.join(BASE_DIR, "categories.json")


# -----------------------------
# MCP Server
# -----------------------------

mcp = FastMCP("expensesTracker")


# -----------------------------
# Load Categories
# -----------------------------

def load_categories():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# -----------------------------
# Initialize Database
# -----------------------------

def init_db():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            )
        """)


init_db()


# -----------------------------
# Tool: Get Categories
# -----------------------------

@mcp.tool
def get_categories() -> dict:
    """
    Return all available expense categories and their subcategories.
    """

    return load_categories()


# -----------------------------
# Tool: Add Expense
# -----------------------------

@mcp.tool
def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    notes: str = ""
) -> dict:
    """
    Add a new expense using the available categories.
    """

    categories = load_categories()

    if category not in categories:
        return {
            "status": "error",
            "message": f"Invalid category. Available categories: {list(categories.keys())}"
        }

    if subcategory and subcategory not in categories[category]:
        return {
            "status": "error",
            "message": f"Invalid subcategory for {category}. "
                       f"Available subcategories: {categories[category]}"
        }

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            """
            INSERT INTO expenses
            (date, amount, category, subcategory, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (date, amount, category, subcategory, notes)
        )

        return {
            "status": "ok",
            "message": "Expense added successfully",
            "id": cursor.lastrowid
        }


# -----------------------------
# Tool: List Expenses
# -----------------------------

@mcp.tool
def list_expenses(start_date: str, end_date: str) -> list[dict]:
    """
    List all expenses between two dates.
    """

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            """
            SELECT id, date, amount, category, subcategory, notes
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (start_date, end_date)
        )

        columns = [description[0] for description in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


# -----------------------------
# Tool: Delete Expense
# -----------------------------

@mcp.tool
def delete_expense(expense_id: int) -> dict:
    """
    Delete an expense using its ID.
    """

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )

        if cursor.rowcount == 0:
            return {
                "status": "error",
                "message": "Expense not found"
            }

        return {
            "status": "ok",
            "message": f"Expense {expense_id} deleted successfully"
        }


# -----------------------------
# Tool: Edit Expense
# -----------------------------

@mcp.tool
def edit_expense(
    expense_id: int,
    date: str = None,
    amount: float = None,
    category: str = None,
    subcategory: str = None,
    notes: str = None
) -> dict:
    """
    Edit an existing expense. Only provided fields will be updated.
    """

    categories = load_categories()

    if category is not None and category not in categories:
        return {
            "status": "error",
            "message": "Invalid category"
        }

    if category is not None and subcategory:
        if subcategory not in categories[category]:
            return {
                "status": "error",
                "message": "Invalid subcategory for selected category"
            }

    updates = []
    values = []

    if date is not None:
        updates.append("date = ?")
        values.append(date)

    if amount is not None:
        updates.append("amount = ?")
        values.append(amount)

    if category is not None:
        updates.append("category = ?")
        values.append(category)

    if subcategory is not None:
        updates.append("subcategory = ?")
        values.append(subcategory)

    if notes is not None:
        updates.append("notes = ?")
        values.append(notes)

    if not updates:
        return {
            "status": "error",
            "message": "No fields provided for update"
        }

    values.append(expense_id)

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            f"""
            UPDATE expenses
            SET {", ".join(updates)}
            WHERE id = ?
            """,
            values
        )

        if cursor.rowcount == 0:
            return {
                "status": "error",
                "message": "Expense not found"
            }

        return {
            "status": "ok",
            "message": f"Expense {expense_id} updated successfully"
        }


# -----------------------------
# Start Server
# -----------------------------

if __name__ == "__main__":
    mcp.run(transport="http",host="0.0.0.0",port=8000 )
  
