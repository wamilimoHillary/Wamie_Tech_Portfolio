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
from app.utils.token_utils import generate_reset_token, get_reset_expiry

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


# ==============================================
# Route: Forgot Password
# Purpose: Handles password reset requests.
#  - User enters their registered email.
#  - If found, a secure reset token and expiry are generated.
#  - A reset link is emailed to the user.
#  - The link directs to the password reset page to set a new password.
# ==============================================

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash("Please enter your email.", "warning")
            return redirect(url_for('auth.forgot_password'))

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, is_active FROM users WHERE email = %s", (email,))
            user = cur.fetchone()

            # Security note: Do not reveal existence. We'll still update/send only if exists
            if user:
                reset_token = generate_reset_token()
                reset_expiry = get_reset_expiry(hours=1)  # 1 hour expiry

                cur.execute("""
                    UPDATE users SET reset_token = %s, reset_expiry = %s WHERE email = %s
                """, (reset_token, reset_expiry, email))
                conn.commit()

                reset_link = url_for('auth.reset_password', token=reset_token, _external=True)

                # Prepare and send email
                msg = Message(
                    subject="WamieTech — Password Reset",
                    sender=EmailConfig.MAIL_DEFAULT_SENDER,
                    recipients=[email]
                )
                msg.html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                  <h2>Password Reset Request</h2>
                  <p>We received a request to reset the password for this email.</p>
                  <p><a href="{reset_link}" style="display:inline-block;padding:10px 18px;
                    background:#007bff;color:#fff;text-decoration:none;border-radius:5px;">
                    Reset Password</a></p>
                  <p>This link expires in 1 hour. If you didn't request this, ignore this email.</p>
                  <p>— WamieTech Team</p>
                </body>
                </html>
                """

                try:
                    mail.send(msg)
                except Exception as e:
                    # Mail failed — log on server and notify user but do not expose details
                    print("Mail send error:", e)
                    flash("If your email is registered, a reset link has been sent (mail delivery failed, logged).", "info")
                    cur.close()
                    conn.close()
                    return redirect(url_for('auth.login'))

            # Generic message (do not leak whether email exists)
            flash("If the email is registered, you will receive a password reset link shortly.", "info")
            return redirect(url_for('auth.login'))

        finally:
            cur.close()
            conn.close()

    # GET - render request form
    return render_template('auth/request_reset.html')


# ==============================================
# Route: Reset Password
# Purpose: Allows users to set a new password.
#  - Triggered when the user clicks the reset link in their email.
#  - Verifies the validity and expiry of the reset token.
#  - Updates the user’s password if valid, then clears the token.
#  - Displays success or error messages accordingly.
# ==============================================

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Validate token existence and expiry
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT email, reset_expiry FROM users WHERE reset_token = %s", (token,))
        row = cur.fetchone()
        if not row:
            flash("Invalid or expired reset link.", "danger")
            return redirect(url_for('auth.forgot_password'))

        email, expiry = row
        if not expiry or datetime.utcnow() > expiry:
            flash("Reset link has expired. Please request a new one.", "warning")
            # Clear token server-side if you like
            cur.execute("UPDATE users SET reset_token = NULL, reset_expiry = NULL WHERE email = %s", (email,))
            conn.commit()
            return redirect(url_for('auth.forgot_password'))

        if request.method == 'POST':
            password = request.form.get('password', '')
            confirm = request.form.get('confirm_password', '')
            if not password or not confirm:
                flash("Please fill out both fields.", "warning")
                return redirect(url_for('auth.reset_password', token=token))
            if password != confirm:
                flash("Passwords do not match.", "danger")
                return redirect(url_for('auth.reset_password', token=token))

            hashed = generate_password_hash(password)
            cur.execute("""
                UPDATE users
                SET password_hash = %s, reset_token = NULL, reset_expiry = NULL
                WHERE email = %s
            """, (hashed, email))
            conn.commit()
            flash("Your password has been reset. You can now log in.", "success")
            return redirect(url_for('auth.login'))

    finally:
        cur.close()
        conn.close()

    # GET - show reset form
    return render_template('auth/reset_password.html', token=token)



# ==============================================
# ADMIN PASSWORD RESET FLOW
# ==============================================

# ----------------------------------------------
# Route: Admin Forgot Password
# Purpose: Sends password reset email to admin
# ----------------------------------------------
@auth.route('/admin_forgot_password', methods=['GET', 'POST'])
def admin_forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash("Please enter your admin email.", "warning")
            return redirect(url_for('auth.admin_forgot_password'))

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT admin_id FROM admins WHERE email = %s", (email,))
            admin = cur.fetchone()

            # Even if not found, keep message generic
            if admin:
                reset_token = generate_reset_token()
                reset_expiry = get_reset_expiry(hours=1)

                cur.execute("""
                    UPDATE admins
                    SET reset_token = %s, reset_expiry = %s
                    WHERE email = %s
                """, (reset_token, reset_expiry, email))
                conn.commit()

                reset_link = url_for('auth.admin_reset_password', token=reset_token, _external=True)

                # Send reset email
                msg = Message(
                    subject="WamieCrafts Admin Password Reset",
                    sender=EmailConfig.MAIL_DEFAULT_SENDER,
                    recipients=[email]
                )
                msg.html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                  <h2>Admin Password Reset Request</h2>
                  <p>We received a request to reset your admin account password.</p>
                  <p><a href="{reset_link}" 
                        style="display:inline-block;padding:10px 18px;
                        background:#007bff;color:#fff;text-decoration:none;
                        border-radius:5px;">Reset Password</a></p>
                  <p>This link expires in 1 hour. If you did not request this, ignore this email.</p>
                  <p>— WamieCrafts Admin Team</p>
                </body>
                </html>
                """
                try:
                    mail.send(msg)
                except Exception as e:
                    print("Admin mail send error:", e)
                    flash("If the email is registered, a reset link has been sent (mail delivery failed, logged).", "info")
                    return redirect(url_for('auth.admin_login'))

            flash("If the admin email is registered, you will receive a reset link shortly.", "info")
            return redirect(url_for('auth.admin_login'))

        finally:
            cur.close()
            conn.close()

    return render_template('auth/admin_request_reset.html')


# ----------------------------------------------
# Route: Admin Reset Password
# Purpose: Allows admin to set a new password
# ----------------------------------------------
@auth.route('/admin_reset_password/<token>', methods=['GET', 'POST'])
def admin_reset_password(token):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT email, reset_expiry FROM admins WHERE reset_token = %s", (token,))
        row = cur.fetchone()
        if not row:
            flash("Invalid or expired reset link.", "danger")
            return redirect(url_for('auth.admin_forgot_password'))

        email, expiry = row
        if not expiry or datetime.utcnow() > expiry:
            flash("Reset link has expired. Please request a new one.", "warning")
            cur.execute("UPDATE admins SET reset_token = NULL, reset_expiry = NULL WHERE email = %s", (email,))
            conn.commit()
            return redirect(url_for('auth.admin_forgot_password'))

        if request.method == 'POST':
            password = request.form.get('password', '')
            confirm = request.form.get('confirm_password', '')
            if not password or not confirm:
                flash("Please fill out both fields.", "warning")
                return redirect(url_for('auth.admin_reset_password', token=token))
            if password != confirm:
                flash("Passwords do not match.", "danger")
                return redirect(url_for('auth.admin_reset_password', token=token))

            hashed = generate_password_hash(password)
            cur.execute("""
                UPDATE admins
                SET password_hash = %s, reset_token = NULL, reset_expiry = NULL
                WHERE email = %s
            """, (hashed, email))
            conn.commit()

            flash("Your password has been successfully reset. You can now log in.", "success")
            return redirect(url_for('auth.admin_login'))

    finally:
        cur.close()
        conn.close()

    return render_template('auth/admin_reset_password.html', token=token)
