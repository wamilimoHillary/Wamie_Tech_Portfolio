from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from functools import wraps
from app.database import get_db_connection
from app.utils.helpers import login_required

# Initialize Blueprint
admin = Blueprint('admin', __name__)

# Route for admin dashboard (secured with login_required decorator)
@admin.route('/admin_dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    user_count = count_users()  # Get the count of users
    project_count = count_projects()  # Get the count of all projects
    team_count = count_teams()  # Get the count of all teams
    services_count = count_services()  # Get the count of all services
    return render_template('admin/admin_dashboard.html', user_count=user_count, project_count=project_count, team_count=team_count, services_count=services_count)

# Helper function to get all users and counts the, etc., from users table
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def count_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

def count_projects():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM projects")
    project_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return project_count

def count_teams():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM teams")
    team_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return team_count

def count_services():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM services")
    service_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return service_count

# Route to manage users
@admin.route('/admin_users', methods=['GET'])
@login_required
def manage_users():
    search_query = request.args.get('search', '').strip()

    try:
        if search_query:
            # Search for users matching the query (by name or email)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username LIKE %s OR email LIKE %s", 
                           (f"%{search_query}%", f"%{search_query}%"))
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            flash(f"Search results for '{search_query}'", "info")
        else:
            # If no search query, fetch all users
            users = get_users()

    except Exception as e:
        flash(f"An error occurred while fetching users: {str(e)}", "danger")
        users = []

    return render_template('admin/manage_users.html', users=users)

# Route to update user
@admin.route('/update_user', methods=['POST'])
@login_required
def update_user():
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    status = request.form.get('status')

    try:
        # Update the user record in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET username = %s, email = %s, phone = %s, is_active = %s WHERE id = %s
        """, (username, email, phone, status, user_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash("User information updated successfully.", "success")
    except Exception as e:
        flash(f"An error occurred while updating the user information: {str(e)}", "danger")

    return redirect(url_for('admin.manage_users'))

# Route to delete user
@admin.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    user_id = request.form.get('user_id')
    if user_id:
        try:
            # Delete the user from the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
            flash("User deleted successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
    else:
        flash("Invalid user ID.", "error")
    return redirect(url_for('admin.manage_users'))

# Route to manage projects
@admin.route('/admin_projects', methods=['GET'])
@login_required
def manage_projects():
    search_query = request.args.get('search', '').strip()

    try:
        if search_query:
            # Search for projects matching the query (by name or status)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE project_name LIKE %s OR project_status LIKE %s", 
                           (f"%{search_query}%", f"%{search_query}%"))
            projects = cursor.fetchall()
            cursor.close()
            conn.close()
            flash(f"Search results for '{search_query}'", "info")
        else:
            # If no search query, fetch all projects
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects")
            projects = cursor.fetchall()
            cursor.close()
            conn.close()

    except Exception as e:
        flash(f"An error occurred while fetching projects: {str(e)}", "danger")
        projects = []

    return render_template('admin/manage_projects.html', projects=projects)

# Route to add project
@admin.route('/add_project', methods=['POST'])
@login_required
def add_project():
    project_name = request.form['project_name']
    project_description = request.form['project_description']
    project_status = request.form['project_status']
    project_link = request.form['project_link']

    try:
        # Insert the new project into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO projects (project_name, project_description, project_status, project_link, date_created)
            VALUES (%s, %s, %s, %s, NOW())
        """, (project_name, project_description, project_status, project_link))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Project added successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")

    return redirect(url_for('admin.manage_projects'))

# Route to update project
@admin.route('/update_project', methods=['POST'])
@login_required
def update_project():
    project_id = request.form.get('project_id')
    project_name = request.form.get('project_name')
    project_description = request.form.get('project_description')
    project_status = request.form.get('project_status')
    project_link = request.form.get('project_link')

    try:
        # Update the project record in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE projects
            SET project_name = %s, project_description = %s, project_status = %s, project_link = %s
            WHERE project_id = %s
        """, (project_name, project_description, project_status, project_link, project_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Project updated successfully.", "success")
    except Exception as e:
        flash(f"An error occurred while updating the project: {str(e)}", "danger")

    return redirect(url_for('admin.manage_projects'))

# Route to delete project
@admin.route('/delete_project', methods=['POST'])
@login_required
def delete_project():
    project_id = request.form.get('project_id')
    if project_id:
        try:
            # Delete the project from the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE project_id = %s", (project_id,))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Project deleted successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
    else:
        flash("Invalid project ID.", "error")
    return redirect(url_for('admin.manage_projects'))

# Route to manage teams
@admin.route('/admin_teams', methods=['GET'])
@login_required
def manage_teams():
    search_query = request.args.get('search', '').strip()

    try:
        if search_query:
            # Search for teams matching the query (by name or role)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teams WHERE team_member_name LIKE %s OR role_played LIKE %s", 
                           (f"%{search_query}%", f"%{search_query}%"))
            teams = cursor.fetchall()
            cursor.close()
            conn.close()
            flash(f"Search results for '{search_query}'", "info")
        else:
            # If no search query, fetch all teams
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teams")
            teams = cursor.fetchall()
            cursor.close()
            conn.close()

    except Exception as e:
        flash(f"An error occurred while fetching teams: {str(e)}", "danger")
        teams = []

    return render_template('admin/manage_teams.html', teams=teams)


from werkzeug.utils import secure_filename
import os

# Define the folder where uploaded images will be stored
UPLOAD_FOLDER = 'static/images'  # Ensure this folder exists in your project
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin.route('/add_team', methods=['POST'])
@login_required
def add_team():
    team_member_name = request.form['team_member_name']
    professionalism = request.form['professionalism']
    role_played = request.form['role_played']
    
    # Check if the post request has the file part
    if 'image_url' not in request.files:
        flash("No file part in the request", "error")
        return redirect(url_for('admin.manage_teams'))
    
    file = request.files['image_url']
    
    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        flash("No selected file", "error")
        return redirect(url_for('admin.manage_teams'))
    
    # If the file is valid
    if file and allowed_file(file.filename):
        # Secure the filename to avoid malicious input
        filename = secure_filename(file.filename)
        
        # Save the file to the upload folder
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Store the relative path in the database (e.g., 'images/filename.ext')
        image_url = f"images/{filename}"
        
        try:
            # Insert the new team member into the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO teams (team_member_name, professionalism, role_played, image_url, date_added)
                VALUES (%s, %s, %s, %s, NOW())
            """, (team_member_name, professionalism, role_played, image_url))
            conn.commit()
            cursor.close()
            conn.close()
            
            flash("Team member added successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
    else:
        flash("Invalid file type. Allowed types are: png, jpg, jpeg, gif", "error")
    
    return redirect(url_for('admin.manage_teams'))

#UPDATE TEAM
from flask import request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

# Define the folder where uploaded images will be stored
UPLOAD_FOLDER = 'static/images'

# Create the directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin.route('/update_team', methods=['POST'])
@login_required
def update_team():
    team_id = request.form.get('team_id')
    team_member_name = request.form.get('team_member_name')
    professionalism = request.form.get('professionalism')
    role_played = request.form.get('role_played')
    image_file = request.files.get('image_url')  # Get the uploaded file

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the current image URL from the database
        cursor.execute("SELECT image_url FROM teams WHERE team_id = %s", (team_id,))
        current_image_url = cursor.fetchone()[0]

        # Handle the image upload
        if image_file and image_file.filename:  # Check if a new image is uploaded
            if allowed_file(image_file.filename):
                # Secure the filename to avoid malicious input
                filename = secure_filename(image_file.filename)

                # Save the file to the upload folder
                full_file_path = os.path.join(UPLOAD_FOLDER, filename)
                image_file.save(full_file_path)

                # Update the image URL in the database (use forward slashes)
                new_image_url = f"images/{filename}"
            else:
                flash("Invalid file type. Allowed types are: png, jpg, jpeg, gif", "error")
                return redirect(url_for('admin.manage_teams'))
        else:
            # If no file is uploaded, keep the current image URL
            new_image_url = current_image_url

        # Update the team member record in the database
        cursor.execute("""
            UPDATE teams
            SET team_member_name = %s, professionalism = %s, role_played = %s, image_url = %s
            WHERE team_id = %s
        """, (team_member_name, professionalism, role_played, new_image_url, team_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Team member updated successfully.", "success")
    except Exception as e:
        flash(f"An error occurred while updating the team member: {str(e)}", "danger")

    return redirect(url_for('admin.manage_teams'))

@admin.route('/delete_team', methods=['POST'])
@login_required
def delete_team():
    team_id = request.form.get('team_id')
    if team_id:
        try:
            # Delete the team member from the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM teams WHERE team_id = %s", (team_id,))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Team member deleted successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
    else:
        flash("Invalid team ID.", "error")
    return redirect(url_for('admin.manage_teams'))



# Route to manage services
@admin.route('/admin_services', methods=['GET'])
@login_required
def manage_services():
    search_query = request.args.get('search', '').strip()

    try:
        if search_query:
            # Search for services matching the query (by name or price)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM services WHERE service_name LIKE %s OR price LIKE %s", 
                           (f"%{search_query}%", f"%{search_query}%"))
            services = cursor.fetchall()
            cursor.close()
            conn.close()
            flash(f"Search results for '{search_query}'", "info")
        else:
            # If no search query, fetch all services
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM services")
            services = cursor.fetchall()
            cursor.close()
            conn.close()

    except Exception as e:
        flash(f"An error occurred while fetching services: {str(e)}", "danger")
        services = []

    return render_template('admin/manage_services.html', services=services)


@admin.route('/add_service', methods=['POST'])
@login_required
def add_service():
    service_name = request.form['service_name']
    description = request.form['service_description']
    price = request.form['service_price']

    try:
        # Insert the new service into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO services (service_name, description, price)
            VALUES (%s, %s, %s)
        """, (service_name, description, price))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Service added successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")

    return redirect(url_for('admin.manage_services'))

@admin.route('/update_service', methods=['POST'])
@login_required
def update_service():
    service_id = request.form.get('service_id')
    service_name = request.form.get('service_name')
    description = request.form.get('service_description')
    price = request.form.get('service_price')

    try:
        # Update the service record in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE services
            SET service_name = %s, description = %s, price = %s
            WHERE service_id = %s
        """, (service_name, description, price, service_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Service updated successfully.", "success")
    except Exception as e:
        flash(f"An error occurred while updating the service: {str(e)}", "danger")

    return redirect(url_for('admin.manage_services'))


@admin.route('/delete_service', methods=['POST'])
@login_required
def delete_service():
    service_id = request.form.get('service_id')
    if service_id:
        try:
            # Delete the service from the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM services WHERE service_id = %s", (service_id,))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Service deleted successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
    else:
        flash("Invalid service ID.", "error")
    return redirect(url_for('admin.manage_services'))

# Route to manage testimonials
@admin.route('/admin_testimonials', methods=['GET'])
@login_required
def manage_testimonials():
    search_query = request.args.get('search', '').strip()

    try:
        if search_query:
            # Search for testimonials matching the query (by client name or project)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients_testimonial WHERE client_name LIKE %s OR project_worked_on LIKE %s", 
                           (f"%{search_query}%", f"%{search_query}%"))
            testimonials = cursor.fetchall()
            cursor.close()
            conn.close()
            flash(f"Search results for '{search_query}'", "info")
        else:
            # If no search query, fetch all testimonials
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients_testimonial")
            testimonials = cursor.fetchall()
            cursor.close()
            conn.close()

    except Exception as e:
        flash(f"An error occurred while fetching testimonials: {str(e)}", "danger")
        testimonials = []

    return render_template('admin/manage_testimonials.html', testimonials=testimonials)

# Route to delete testimonial
@admin.route('/delete_testimonial', methods=['POST'])
@login_required
def delete_testimonial():
    testimonial_id = request.form.get('testimonial_id')
    if testimonial_id:
        try:
            # Delete the testimonial from the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients_testimonial WHERE testimonial_id = %s", (testimonial_id,))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Testimonial deleted successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
    else:
        flash("Invalid testimonial ID.", "error")
    return redirect(url_for('admin.manage_testimonials'))

