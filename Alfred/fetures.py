from flask import Blueprint, render_template

fetures = Blueprint("fetures",__name__)

@fetures.route('/todolist', methods=['GET', 'POST'])
def add_task():
    return render_template('todolist.html')

@fetures.route('/lyrics')
def lyrics():
    return render_template('lyrics.html')

@fetures.route('/cooking')
def cooking():
    return render_template('cooking.html')