from flask import Blueprint, render_template
from app.database import get_db_connection

# Create a Blueprint for testimonial routes
testimonial_bp = Blueprint('testimonial', __name__)

@testimonial_bp.route('/testimonials')
def testimonials():
    # Fetch all testimonials from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients_testimonial;")
    testimonials_data = cursor.fetchall()
    cursor.close()
    conn.close()

    # Render the testimonials.html template with the fetched data
    return render_template('main/testimonials.html', testimonials=testimonials_data)