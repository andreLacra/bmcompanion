from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from . import views
import re
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user


# Check If Username is valid
def is_valid_username(usernameInput):
    # Check length of username
    if len(usernameInput) < 4 or len(usernameInput) > 20:
        return False

    # Check if the username starts with a letter
    if not usernameInput[0].isalpha():
        return False

    # Check if the username contains only letters, numbers, and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', usernameInput):
        return False

    return True

# Check if password is valid
def is_valid_password(passwordInput):
    # Check the length of the password
    if len(passwordInput) < 8:
        return False

    # Check if the password contains at least one uppercase letter, one lowercase letter, and one digit
    if not re.search(r'[A-Z]', passwordInput) or not re.search(r'[a-z]', passwordInput) or not re.search(r'\d', passwordInput):
        return False

    return True



# FLASK -----

loggedIn = False
userLogged = None

auth = Blueprint('auth', __name__)


@auth.route('/signout')
@login_required
def signout():
    global loggedIn, userLogged
    session.pop("user_id", None)
    logout_user()
    loggedIn = False
    userLogged = None
    return redirect(url_for('auth.signin'))


@auth.route('/', methods=['GET','POST'])
def signin():
    message = None
    global loggedIn, userLogged

    if(loggedIn == True):
        return redirect(url_for('views.dashboard'))

    if(request.method == 'POST'):
        input_email = request.form.get('input-email')    
        input_password = request.form.get('input-password')

        user = User.query.filter_by(email=input_email).first()
        if((input_email != None) and (input_password != None)):
            if (user):
                if check_password_hash(user.password, input_password):
                    login_user(user, remember=True)
                    loggedIn = True
                    userLogged = f'{str(user.firstname)} {str(user.lastname)}'
                    print("=======\n" + userLogged)
                    session["user_id"] = user.firstname
                    return redirect(url_for('views.dashboard'))
                else:
                    message = 'Invalid Password. Please Try Again.'
            else:
                message = 'Invalid Email. Please Try Again.'

    return render_template('signin1.html', message=message)


@auth.route('/sign-up', methods=['GET','POST'])
def signup():
    message = None

    global loggedIn

    if(loggedIn == True):
        return redirect(url_for('views.dashboard'))

    if(request.method == 'POST'):

        # input_username = request.form.get('input-username')   
        input_firstname = request.form.get('input-firstname')   
        input_lastname = request.form.get('input-lastname')   
        input_email = request.form.get('input-email')    
        input_password = request.form.get('input-password')
        input_reenter_password = request.form.get('input-reenter-password')   

        user = User.query.filter_by(email=input_email).first()

        if((input_firstname != None) 
            and (input_lastname != None) and (input_email != None) 
            and (input_password != None) and (input_reenter_password != None)):

            if(user):
                message = 'This email is already exist. Please try again.'
            # elif ((is_valid_username(input_username) == False)):
            #     message = 'Invalid Username. Please try Again.'
            elif ((is_valid_password(input_password) == False)):
                message = 'Password appeared to be weak. Please try again.'
            elif ((input_password != input_reenter_password)):
                message = "Password don't match. Please try Again."
            else:
                new_user = User(firstname=input_firstname, 
                                lastname=input_lastname,
                                email=input_email,
                                password=generate_password_hash(input_password, method='sha256'))
                db.session.add(new_user)
                db.session.commit()

                return redirect(url_for('auth.signin'))
    
    return render_template('signup1.html', message=message)