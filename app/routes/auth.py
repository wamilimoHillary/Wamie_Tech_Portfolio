from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import os
import random
import string
from app.config import Config
from app.database import get_db_connection
from app.utils.helpers import generate_token, get_token_expiry
from app.email_config import EmailConfig




# Initialize Blueprint
auth = Blueprint('auth', __name__)

# Initialize Mail
mail = Mail()



# Route for user login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html')



# Route for admin login
@auth.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check admin credentials in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
        admin = cursor.fetchone()  # Fetch the admin record

        if admin:
            stored_password_hash = admin[3]  # Assuming the hashed password is in the 3rd column

            # Check if the entered password matches the stored hash
            if check_password_hash(stored_password_hash, password):
                session['admin_id'] = admin[0]  # Store admin's ID in session
                flash("Login successful!", "success")
                return redirect(url_for('admin.admin_dashboard'))  # Redirect to the admin dashboard
            else:
                flash("Incorrect password.", "danger")
        else:
            flash("No admin account found with that email.", "danger")

        cursor.close()
        conn.close()

    return render_template('auth/admin_login.html')


# Route for admin logout
@auth.route('/admin_logout')
def admin_logout():
    session.pop('admin_id', None)  # Remove admin from session
    flash("Logged out successfully.", "success")
    return redirect(url_for('auth.admin_login'))