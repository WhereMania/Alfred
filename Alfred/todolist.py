from flask import Blueprint, render_template

todolist = Blueprint("todolist",__name__)

@todolist.route('/todolist', methods=['GET', 'POST'])
def add_task():

    return render_template('todolist.html')