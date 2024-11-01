from flask import Blueprint,render_template,request,flash,url_for,redirect , session
from flask_bcrypt import Bcrypt
import re
import mysql.connector


mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='123321taha!',  
    database='user_data'
)


cursor = mydb.cursor()

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def is_valid_email(email):
    return bool(re.match(email_regex, email))

def is_valid_username(username):
    return len(username) > 6

def is_valid_password(password):
    password_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    return bool(password_regex.match(password))

def get_hashed_password(plain_text_password):
    return bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

def check_password(plain_text_password, hashed_password):
    return bcrypt.check_password_hash(hashed_password, plain_text_password)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            if check_password(password, account[2]):
                session['user_id'] = account[0]  # Store user ID in session
                session['username'] = account[1]  # Store username in session
                flash('Logged in successfully!', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Invalid password.', category='error')
        else:
            flash('Username does not exist.', category='error')
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()  # Clear the session
    flash("You have been logged out.", category='success')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        can_register = True

        if not is_valid_username(username):
            flash("Username must be 6 characters or more.", category='error')
            can_register = False

        if not is_valid_email(email):
            flash("Invalid email format.", category='error')
            can_register = False

        if not is_valid_password(password1):
            flash("Password must be stronger(!@#A-Z&8)", category='error')
            can_register = False 

        if password1 != password2:
            flash("Passwords do not match.", category='error')
            can_register = False
        
        if not can_register:
            return render_template('register.html')

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            flash("Username already exists. Please choose a different username.", category='error')
            return render_template('register.html')

        hashed_password = get_hashed_password(password1)
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, hashed_password))
        mydb.commit()

        flash("Registration successful!", category='success')



    
    return render_template('register.html')