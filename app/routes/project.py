from flask import Blueprint, render_template
from app.database import get_db_connection

project_bp = Blueprint('project', __name__)

@project_bp.route('/projects')
def projects():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all projects
        cursor.execute("""
            SELECT project_id, project_name, project_description, project_status, project_link, date_created, project_type 
            FROM projects
            ORDER BY date_created DESC;
        """)
        projects_data = cursor.fetchall()

        # Fetch distinct project types for dynamic filters
        cursor.execute("SELECT DISTINCT project_type FROM projects;")
        project_types = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return render_template(
            'main/projects.html',
            projects=projects_data,
            project_types=project_types
        )

    except Exception as e:
        return render_template('errors/db_error.html', message=str(e)), 503
