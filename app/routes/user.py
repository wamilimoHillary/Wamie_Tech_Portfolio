from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.database import get_db_connection

# Initialize Blueprint
user = Blueprint('user', __name__)

# Route for user dashboard
@user.route('/user_dashboard')
def user_dashboard():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("You need to log in to access the dashboard.", "warning")
        return redirect(url_for('auth.login'))

    # Fetch user details from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if user_data:
        return render_template('user/user_dashboard.html', user=user_data)
    else:
        flash("User not found.", "danger")
        return redirect(url_for('auth.login'))

# Route for user logout
@user.route('/user_logout')
def user_logout():
    # Remove user_id from session
    session.pop('user_id', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('auth.login'))