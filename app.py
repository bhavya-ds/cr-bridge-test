"""
Simple user authentication API - intentionally vulnerable for testing

WARNING: This code contains intentional security vulnerabilities for cr-bridge testing.
DO NOT use in production!
"""

import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/login", methods=["POST"])
def login():
    """Login endpoint with SQL injection vulnerability"""
    email = request.form.get("email")
    password = request.form.get("password")

    # SECURITY ISSUE: SQL Injection vulnerability
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE email = '{email}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "success", "user": user[0]})
    return jsonify({"status": "error", "message": "Invalid credentials"})


@app.route("/search", methods=["GET"])
def search():
    """Search endpoint with XSS vulnerability"""
    query = request.args.get("q", "")

    # SECURITY ISSUE: XSS vulnerability - no escaping
    results = f"<h1>Search results for: {query}</h1>"

    return results


@app.route("/api/users/<user_id>", methods=["GET"])
def get_user(user_id):
    """Get user by ID - no authentication"""
    # SECURITY ISSUE: No authentication check
    # SECURITY ISSUE: SQL Injection in user_id
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    user = cursor.fetchone()
    conn.close()

    if user:
        # SECURITY ISSUE: Exposing sensitive data
        return jsonify(
            {
                "id": user[0],
                "email": user[1],
                "password": user[2],  # NEVER expose passwords!
                "credit_card": user[3],  # NEVER expose PII!
            }
        )
    return jsonify({"error": "User not found"}), 404


@app.route("/admin/delete", methods=["POST"])
def delete_user():
    """Delete user - no CSRF protection"""
    # SECURITY ISSUE: No CSRF token validation
    # SECURITY ISSUE: No admin authentication
    user_id = request.form.get("user_id")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
    conn.commit()
    conn.close()

    return jsonify({"status": "deleted"})


@app.route("/api/transfer", methods=["POST"])
def transfer_money():
    """Money transfer endpoint - FIXED: SQL injection removed"""
    from_account = request.form.get("from")
    to_account = request.form.get("to")
    amount = request.form.get("amount")

    # FIX #1: Input validation
    if not all([from_account, to_account, amount]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    if from_account == to_account:
        return jsonify(
            {"status": "error", "message": "Cannot transfer to same account"}
        ), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify(
                {"status": "error", "message": "Amount must be positive"}
            ), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid amount"}), 400

    # FIX #2 & #3 & #4: Parameterized queries + atomic transaction + rowcount validation
    conn = sqlite3.connect("banking.db")
    cursor = conn.cursor()

    try:
        # Use parameterized queries to prevent SQL injection
        cursor.execute(
            "UPDATE accounts SET balance = balance - ? WHERE account_id = ?",
            (amount, from_account),
        )
        # FIX #4: Validate that the account exists
        if cursor.rowcount != 1:
            conn.rollback()
            return jsonify(
                {"status": "error", "message": "Source account not found"}
            ), 404

        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE account_id = ?",
            (amount, to_account),
        )
        # FIX #4: Validate destination account exists
        if cursor.rowcount != 1:
            conn.rollback()
            return jsonify(
                {"status": "error", "message": "Destination account not found"}
            ), 404

        conn.commit()
    except sqlite3.Error:
        # FIX #4: Catch specific exception, don't leak internals
        conn.rollback()
        return jsonify({"status": "error", "message": "Database error"}), 500
    finally:
        # FIX #4: Always cleanup connection
        conn.close()

    return jsonify({"status": "transferred", "amount": amount})


if __name__ == "__main__":
    # SECURITY ISSUE: Debug mode enabled in production
    # SECURITY ISSUE: Running on 0.0.0.0 exposes to all interfaces
    app.run(host="0.0.0.0", debug=True, port=5000)
