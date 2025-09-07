from flask import Blueprint, render_template
from app.database import get_db_connection

# Create a Blueprint for project routes
project_bp = Blueprint('project', __name__)

@project_bp.route('/projects')
def projects():
    # Fetch all projects from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects;")
    projects_data = cursor.fetchall()
    cursor.close()
    conn.close()

    # Render the projects.html template with the fetched data
    return render_template('main/projects.html', projects=projects_data)