from flask import Blueprint, render_template, redirect, url_for, flash, session

views = Blueprint('views', __name__)

@views.route('/')
def home():
    # Check if the user is logged in
    if 'user_id' not in session:  # Check if 'user_id' is in the session
        flash("You must be logged in to view this page.", category='error')  # Optional: flash message
        return redirect(url_for('auth.login'))  # Redirect to the login page
    
    return render_template('home.html')
