from flask import Blueprint, render_template
from app.database import get_db_connection

# Blueprint for services
service_bp = Blueprint('service', __name__)

@service_bp.route('/services')
def services():
    try:
        # Try connecting to the database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT service_name, description, price FROM services")
        services_data = cur.fetchall()
        cur.close()
        conn.close()

        # Render the normal services page
        return render_template("main/services.html", services=services_data)

    except ConnectionError as e:
        # Show a friendly error page if Supabase is unreachable
        return render_template('errors/db_error.html', message=str(e)), 503

    except Exception as e:
        # Catch any unexpected issue (optional safety)
        return render_template('errors/db_error.html', message=f"An unexpected error occurred: {e}"), 500
