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


if __name__ == "__main__":
    # SECURITY ISSUE: Debug mode enabled in production
    # SECURITY ISSUE: Running on 0.0.0.0 exposes to all interfaces
    app.run(host="0.0.0.0", debug=True, port=5000)
