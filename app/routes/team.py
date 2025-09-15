from flask import Blueprint, render_template
from app.database import get_db_connection

# Create a Blueprint for team routes
team_bp = Blueprint('team', __name__)

@team_bp.route('/team')
def team():
    # Fetch all team members from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams;")
    team_data = cursor.fetchall()
    cursor.close()
    conn.close()

    # Render the team.html template with the fetched data
    return render_template('main/team.html', team_members=team_data)