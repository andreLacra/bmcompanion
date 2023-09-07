from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy(session_options={"autoflush": False})
DB_NAME = "matchingbusiness.db"
DB_NAME_MYSQL = "matchingbusiness"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'bUs33M4tch1ng*&^'
    # app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    # app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:Andyzxc4@localhost/{DB_NAME_MYSQL}"
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://kpbkzjmq6gq90n32:bpohbsypqrpm3y20@uzb4o9e2oe257glt.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/ra8syicuxt9p3bqe"
    db.init_app(app)


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Company 

    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
    else:
        print("============\nDatabase Already Created")


    login_manager = LoginManager()
    login_manager.login_view = 'auth.signin'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

# def create_database(app):
#     if not path.exists('website/' + DB_NAME):
#         db.create_all(app=app)
#         print('Created Database for Users!')



