from flask import Blueprint, render_template , request,flash,redirect, url_for
import mysql.connector


mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='123321taha!',  
    database='user_data'
)

cursor = mydb.cursor()
fetures = Blueprint("fetures",__name__)


@fetures.route('/todolist', methods=['GET', 'POST'])
def task():
    if request.method == 'POST':
        task = request.form.get('task')
        if task:
            cursor.execute('INSERT INTO tasks (household_id, task_description, status) VALUES (%s, %s, %s)', 
               (None, task, "In Progress")) 
            mydb.commit()
            flash("Task Added", category='success')
    cursor.execute('SELECT id, task_description, status FROM tasks')
    tasks = cursor.fetchall() 
    return render_template('todolist.html', tasks=tasks)

@fetures.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    cursor.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
    mydb.commit()
    flash("Task Deleted", category='success')
    return redirect(url_for('fetures.task'))

@fetures.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    cursor.execute('UPDATE tasks SET status = %s WHERE id = %s', ('Finished', task_id))
    mydb.commit()
    flash("Task Marked as Finished", category='success')
    return redirect(url_for('fetures.task'))



    
@fetures.route('/lyrics')
def lyrics():
    return render_template('lyrics.html')

@fetures.route('/cooking', methods=['GET', 'POST'])
def cooking():
    if request.method == 'POST':
        food_name = request.form.get('food_name')
        recipe = request.form.get('recipe')
        cursor.execute('INSERT INTO food (foodname, recipes) VALUES (%s, %s)', (food_name, recipe))
        flash('Recipe added successfully!')
        mydb.commit()
        return redirect(url_for('fetures.cooking'))

    cursor.execute('SELECT * FROM food')
    recipes = cursor.fetchall() 
    return render_template('cooking.html', recipes=recipes)

        

@fetures.route('/cooking/delete/<int:food_id>', methods=['POST'])
def delete_cooking(food_id):
    cursor.execute('DELETE FROM food WHERE id = %s', (food_id,))
    mydb.commit()
    
    flash('Recipe deleted successfully!')
    return redirect(url_for('fetures.cooking'))
    
