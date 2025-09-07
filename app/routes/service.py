from flask import Blueprint, render_template
from app.database import get_db_connection

service_bp = Blueprint('service', __name__)

@service_bp.route('/services')
def services():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT service_name, description, price FROM services")
    services = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("main/services.html", services=services)
