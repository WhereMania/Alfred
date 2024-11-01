from flask import Blueprint, render_template, request, redirect, url_for, flash , session
import mysql.connector
from flask_socketio import emit
from datetime import datetime


# Initialize the Blueprint
household = Blueprint('household', __name__)

# MySQL connection
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='123321taha!',
    database='user_data'
)
cursor = mydb.cursor()

@household.route('/household', methods=['GET', 'POST'])
def manage_household():
    if request.method == 'POST':
        household_name = request.form.get('household_name')
        # Create a new household
        cursor.execute('INSERT INTO households (name) VALUES (%s)', (household_name,))
        mydb.commit()
        flash("Household created!", category='success')
        return redirect(url_for('household.manage_household'))

    # Fetch existing households
    cursor.execute('SELECT * FROM households')
    households = cursor.fetchall()

    # Fetch members for each household
    household_members = {}
    for household in households:
        household_id = household[0]
        cursor.execute('SELECT user_id, username FROM household_members JOIN users ON household_members.user_id = users.id WHERE household_id = %s', (household_id,))
        members = cursor.fetchall()
        household_members[household_id] = members  # Map members to the household ID

    # Fetch tasks for each household
    household_tasks = {}
    for household in households:
        household_id = household[0]
        cursor.execute('SELECT * FROM tasks WHERE household_id = %s', (household_id,))
        tasks = cursor.fetchall()
        household_tasks[household_id] = tasks  # Map tasks to the household ID

    return render_template(
        'household.html', 
        households=households, 
        household_members=household_members,
        household_tasks=household_tasks  # Pass tasks to the template
    )
@household.route('/household/add_member/<int:household_id>', methods=['POST'])
def add_member(household_id):
    user_id = request.form.get('user_id')
    # Add a member to the household
    cursor.execute('INSERT INTO household_members (household_id, user_id) VALUES (%s, %s)', (household_id, user_id))
    mydb.commit()
    flash("Member added to household!", category='success')
    return redirect(url_for('household.manage_household'))

@household.route('/household/remove_member/<int:household_id>/<int:user_id>', methods=['POST'])
def remove_member(household_id, user_id):
    # Remove the member from the household
    cursor.execute('DELETE FROM household_members WHERE household_id = %s AND user_id = %s', (household_id, user_id))
    mydb.commit()
    flash("Member removed successfully!", category='success')
    return redirect(url_for('household.manage_household'))

@household.route('/assign_task', methods=['POST'])
def assign_task():
    household_id = request.form.get('household_id')
    task_description = request.form.get('task_description')
    assigned_user_id = request.form.get('assigned_user_id')

    # Insert the task
    cursor.execute(
        'INSERT INTO tasks (household_id, assigned_user_id, task_description) VALUES (%s, %s, %s)',
        (household_id, assigned_user_id, task_description)
    )
    task_id = cursor.lastrowid  # Get the last inserted task id
    mydb.commit()

    # Insert a notification for the assigned user
    cursor.execute(
        'INSERT INTO notifications (user_id, task_id, message) VALUES (%s, %s, %s)',
        (assigned_user_id, task_id, 'You have been assigned a new task.')
    )
    mydb.commit()

    # Flash message for successful assignment
    flash("Task assigned and user notified!", category='success')

    # Fetch updated list of tasks
    cursor.execute('SELECT * FROM tasks WHERE household_id = %s', (household_id,))
    tasks = cursor.fetchall()

    # Now pass the updated tasks to the manage_household template
    return redirect(url_for('household.manage_household', tasks=tasks))
 

# Fetch tasks for the user
@household.route('/todolist', methods=['GET', 'POST'])
def task():
    user_id = ...  # Get the current user's ID from the session
    household_id = request.args.get('household_id')  # Optionally pass household ID to filter by household

    if request.method == 'POST':
        task_description = request.form.get('task')
        assigned_user_id = request.form.get('assigned_user_id')
        if task_description:
            cursor.execute(
                'INSERT INTO tasks (household_id, assigned_user_id, task_description, status) VALUES (%s, %s, %s, %s)',
                (household_id, assigned_user_id, task_description, "In Progress")
            )
            mydb.commit()
            flash("Task Added", category='success')

    # Fetch tasks assigned to the current user or within the specified household
    if household_id:
        cursor.execute('SELECT id, task_description, status, assigned_user_id FROM tasks WHERE household_id = %s', (household_id,))
    else:
        cursor.execute('SELECT id, task_description, status, assigned_user_id FROM tasks WHERE assigned_user_id = %s', (user_id,))
    
    tasks = cursor.fetchall()

    # Fetch the assigned user’s name for each task if needed
    task_list = []
    for task in tasks:
        task_id, description, status, assigned_user_id = task
        cursor.execute('SELECT username FROM users WHERE id = %s', (assigned_user_id,))
        assigned_user = cursor.fetchone()
        task_list.append({
            "id": task_id,
            "description": description,
            "status": status,
            "assigned_user": assigned_user[0] if assigned_user else "Unassigned"
        })

    return render_template('todolist.html', tasks=task_list)

# You may also want to add a route for fetching notifications@household.route('/notifications', methods=['GET'])
@household.route('/notifications', methods=['GET'])
def notifications():
    # Retrieve user_id from the session
    user_id = session.get('user_id')

    # Check if user_id is present
    if user_id is None:
        flash("You must be logged in to view notifications.", category='error')
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in

    # Fetch user notifications with task details
    cursor.execute('''
        SELECT notifications.id AS notification_id,
               notifications.message AS notification_message,
               tasks.task_description AS task_description,
               tasks.household_id AS household_id,
               notifications.is_read AS is_read
        FROM notifications
        JOIN tasks ON notifications.task_id = tasks.id
        WHERE notifications.user_id = %s
    ''', (user_id,))
    user_notifications = cursor.fetchall()

    return render_template('notifications.html', notifications=user_notifications)

@household.route('/mark_notification_read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    # Update the notification to set is_read to true
    cursor.execute(
        'UPDATE notifications SET is_read = 1 WHERE id = %s', (notification_id,)
    )
    mydb.commit()

    flash("Notification marked as read!", category='success')
    return redirect(url_for('household.notifications'))


# Delete household and cascade to remove tasks and members
@household.route('/household/delete/<int:household_id>', methods=['POST'])
def delete_household(household_id):
    cursor.execute('DELETE FROM tasks WHERE household_id = %s', (household_id,))
    cursor.execute('DELETE FROM household_members WHERE household_id = %s', (household_id,))
    cursor.execute('DELETE FROM households WHERE id = %s', (household_id,))
    mydb.commit()
    flash("Household deleted successfully!", category='success')
    return redirect(url_for('household.manage_household'))

# Delete a specific task
@household.route('/task/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    cursor.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
    mydb.commit()
    flash("Task deleted successfully.", category='success')
    return redirect(url_for('household.task'))


@household.route('/remove_assignment/<int:task_id>', methods=['POST'])
def remove_assignment(task_id):
    # Remove the task assignment
    cursor.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
    mydb.commit()
    flash("Task assignment removed successfully!", category='success')
    return redirect(url_for('household.manage_household'))
