import random
import string
from datetime import datetime, timedelta
from functools import wraps
from flask import redirect, url_for, flash, session

def generate_token(length=50):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_token_expiry():
    return datetime.now() + timedelta(minutes=3)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash("You need to log in to access this page.", "warning")
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

