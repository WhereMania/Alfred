from flask import Flask,render_template, request, redirect, url_for, session
import os
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'KEY'



    from .views import views
    from .auth import auth
    from .fetures import fetures

    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(fetures, url_prefix='/')
    
    return app

   