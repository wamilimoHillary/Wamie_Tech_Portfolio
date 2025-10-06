from flask import Blueprint, render_template
from app.database import get_db_connection

# Create a Blueprint for project routes
project_bp = Blueprint('project', __name__)

@project_bp.route('/projects')
def projects():
    try:
        # Try fetching projects from Supabase
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects;")
        projects_data = cursor.fetchall()
        cursor.close()
        conn.close()

        # Render data if successful
        return render_template('main/projects.html', projects=projects_data)

    except ConnectionError as e:
        # Render friendly error page if Supabase not reachable
        return render_template('errors/db_error.html', message=str(e)), 503
