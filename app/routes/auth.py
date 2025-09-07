from flask import Blueprint, render_template, request, redirect, flash, url_for, session

# Initialize Blueprint
auth = Blueprint('auth', __name__)

# Route for user login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html')