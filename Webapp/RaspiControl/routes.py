from flask import render_template, url_for, flash, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from raspicontrol.forms import RegistrationForm, LoginForm
from raspicontrol.models import User, Appliances
from raspicontrol import app, bcrypt, db

# @app.route("/", defaults={"message" : ""})
# @app.route("/")
@app.route("/login", defaults={"message" : ""}, methods=["GET", "POST"])
@app.route("/login/<message>", methods=["GET", "POST"])
def login(message):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            message = "Login Unsuccessful. Please check username and password."
        return render_template('login.html', title='Login', form=form, offer_register="offer_register", message=message)
    if message:
        return render_template('login.html', title='Login', form=form, offer_register="offer_register", message=message)
    return render_template('login.html', title='Login', form=form, offer_register="offer_register")

@app.route("/home")
@login_required
def home():
    return render_template("home.html", title="Home", offer_logout="offer_logout")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        message = f'Account created for {form.username.data}!'
        return redirect(url_for('login', message=message))
        # return render_template('login.html', title='Login', form=form, offer_register="offer_register", message=message, complete="complete")
    return render_template('register.html', title='Register', form=form, offer_login="offer_login")

@app.route("/forgot")
def forgot():
   return render_template("forgot.html", title="Forgot Pasword")

@app.route("/logout")
def logout():
    logout_user()
    # if session.get('was_once_logged_in'):
    #     # prevent flashing automatically logged out message
    #     del session['was_once_logged_in']
    return redirect(url_for('login'))

@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account")
