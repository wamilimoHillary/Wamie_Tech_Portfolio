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

#defining contant for routes

# Route for user signup
# Route for user signup
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        # Database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("An account with this email already exists. Please log in or use a different email.", "danger")
            return redirect(url_for('auth.signup'))

        # Generate email verification token
        token = generate_token()
        token_expiry = get_token_expiry()

        try:
            # Insert new user into users table
            cursor.execute("""
                INSERT INTO users (username, email, phone, password_hash, email_token, token_expiry)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, email, phone, password_hash, token, token_expiry))
            conn.commit()

            # Send verification email with styled HTML button
            verification_link = url_for('auth.verify_email_token', token=token, _external=True)
            msg = Message("Email Verification", sender=EmailConfig.MAIL_USERNAME, recipients=[email])
            msg.html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2>Welcome to WamieCrafts, {username}!</h2>
                    <p>Thank you for signing up. Please click the button below to verify your email address and activate your account:</p>
                    <p>
                        <a href="{verification_link}" 
                           style="display:inline-block; padding:10px 20px; 
                                  background-color:#4CAF50; color:white; 
                                  text-decoration:none; border-radius:5px;">
                           Verify My Email
                        </a>
                    </p>
                    <p>If you did not sign up, you can safely ignore this email.</p>
                    <br>
                    <p>Best regards,<br>WamieCrafts Team</p>
                </body>
            </html>
            """
            mail.send(msg)

            flash("Your account has been created. Please check your email for the verification link.", "success")
            return redirect(url_for('auth.verify_email'))

        except Exception as e:
            print(f"Error inserting user: {e}")
            conn.rollback()
            flash("An error occurred while creating your account. Please try again.", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template('auth/signup.html')


# Route to verify email
@auth.route('/verify_email')
def verify_email():
    return render_template('auth/verify_email.html')  # Template to inform the user to check their email

# Route to verify email token
@auth.route('/verify_email/<token>')
def verify_email_token(token):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email_token, token_expiry FROM users WHERE email_token = %s", (token,))
    user = cursor.fetchone()  # Fetch a single user, result will be a tuple

    if user:
        # Access token_expiry using its index in the tuple (1st index since `email_token` is index 0)
        token_expiry = user[1]  # Assuming token_expiry is the second column in SELECT query
        
        # Debug: Print token_expiry to verify its correctness
        print(f"Token expiry: {token_expiry}")

        # Check if the token is expired
        if datetime.now() > token_expiry:
            flash("The verification link has expired, click login, put email and passwords, and then be directed to resend link", "danger")
            return redirect(url_for('auth.verify_email'))  # Redirect to the verify email page

        # Update the user's status to active
        cursor.execute("UPDATE users SET is_active = True WHERE email_token = %s", (token,))
        conn.commit()
        flash("Your email has been successfully verified. Please log in.", "success")
    else:
        flash("Invalid or expired verification link.", "danger")

    cursor.close()
    conn.close()
    return redirect(url_for('auth.verify_email'))  # Redirect to the verify email page

# Route for user login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_phone = request.form['email_phone']
        password = request.form['password']

        # Check if email or phone number exists in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email = %s OR phone = %s", 
            (email_phone, email_phone)
        )
        user = cursor.fetchone()

        if user:
            # Check if the account is active/verified (using index 5 for is_active)
            if user[5] == 0:  # Ensure is_active is 0 (inactive)
                flash("Your account is not verified. Please verify your email to log in.", "danger")
                return redirect(url_for('auth.resend_verification'))  # Redirect to resend verification route

            # Check if the entered password matches the hashed password (using index 4 for password_hash)
            if check_password_hash(user[4], password):  # Ensure column positions match
                session['user_id'] = user[0]  # Store the user's ID in session (index 0 for user id)
                flash("Login successful!", "success")
                return redirect(url_for('user.user_dashboard'))  # Redirect to user dashboard
            else:
                flash("Incorrect password.", "danger")  # Show message for incorrect password
        else:
            flash("No account found with the provided email or phone number.", "danger")

        cursor.close()
        conn.close()

    return render_template('auth/login.html')


# Route to resend verification email
@auth.route('/resend_verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form['email']

        # Connect to DB
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            # Check if user is inactive
            if user[5] == 0:  # is_active == 0
                # Generate new token & expiry
                new_token = generate_token()
                new_expiry = get_token_expiry()

                # Update DB with new token
                cursor.execute("""
                    UPDATE users 
                    SET email_token = %s, token_expiry = %s 
                    WHERE email = %s
                """, (new_token, new_expiry, email))
                conn.commit()

                # Prepare verification link
                verification_link = url_for(
                    'auth.verify_email_token',
                    token=new_token,
                    _external=True
                )

                # Send email with HTML body
                msg = Message(
                    "Email Verification",
                    sender=EmailConfig.MAIL_USERNAME,
                    recipients=[email]
                )
                msg.html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; color: #333;">
                        <h2>Email Verification</h2>
                        <p>Hello,</p>
                        <p>You requested a new verification link. Please click the button below to verify your email:</p>
                        <p>
                            <a href="{verification_link}" 
                               style="display:inline-block; padding:10px 20px; 
                                      background-color:#4CAF50; color:white; 
                                      text-decoration:none; border-radius:5px;">
                               Verify My Email
                            </a>
                        </p>
                        <p>If you did not make this request, you can safely ignore this email.</p>
                        <br>
                        <p>Best regards,<br>WamieTech Team</p>
                    </body>
                </html>
                """

                mail.send(msg)

                flash("A new verification link has been sent to your email.", "success")
                return redirect(url_for('auth.login'))

            else:
                flash("Your email is already verified.", "info")
                return redirect(url_for('auth.login'))

        else:
            flash("No account found with that email address.", "danger")

        # Close DB connection
        cursor.close()
        conn.close()

    # Render resend verification page
    return render_template('auth/resend_verification.html')


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