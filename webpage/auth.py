from flask import Blueprint, render_template, redirect, url_for, request
from flask.helpers import flash
from . import db
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        
        if user!=None:
            if check_password_hash(user.password, password):
                flash("Logged in", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Password doesn't exist.", category='error')
        else:
            flash("Username doesn't exist.", category='error')
    return render_template("login.html", user = current_user)


@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        fname = request.form.get("fName")
        lname = request.form.get("lName")
        email_found = User.query.filter_by(email=email).first()
        username_found = User.query.filter_by(username=username).first()
        
        if fname is None or lname is None:
            flash('Last Name and First Name fields are required')
        if email_found!=None:
            flash('Email is already in use.', category='error')
        elif username_found!=None:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 8:
            flash('Password is less than 8 chars long.', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password1,method='sha256'), fname=fname, lname = lname)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user = current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))
