from flask import render_template, url_for, flash, redirect
from flask_login import login_user, current_user, logout_user, login_required
from raspicontrol.forms import RegistrationForm, LoginForm
from raspicontrol.models import User
from raspicontrol import app

@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else render_template('home.html', title='Home')
        else:
            message = "Login Unsuccessful. Please check username and password"
        return render_template('login.html', title='Login', form=form, offer_register="offer_register", message=message)
    return render_template('login.html', title='Login', form=form, offer_register="offer_register")

@app.route("/home")
@login_required
def home():
    return render_template("home.html", title="Home")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    message = None
    if form.validate_on_submit():
        message = f'Account created for {form.username.data}!'
        # return redirect(url_for('login'))
        return render_template('login.html', title='Login', form=form, offer_register="offer_register", message=message, complete="complete")
    return render_template('register.html', title='Register', form=form, offer_login="offer_login")

@app.route("/forgot")
def forgot():
   return render_template("forgot.html", title="Forgot Pasword")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))