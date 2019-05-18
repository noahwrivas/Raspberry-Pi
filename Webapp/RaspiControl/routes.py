from flask import render_template, url_for, flash, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from RaspiControl.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                RequestResetForm, ResetPasswordForm)
from RaspiControl.models import User, Appliances
from RaspiControl import app, bcrypt, db

@app.route("/")
def default():
    try:
        _ = User.query.all()
    except:
        db.create_all()
    return redirect(url_for("login"))

@app.route("/login", defaults={"message" : ""}, methods=["GET", "POST"])
@app.route("/login/<message>", methods=["GET", "POST"])
def login(message):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print(form.remember.data)
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
    return render_template("home.html", title="Home", offer_logout_account="offer_logout_account")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, 
                    phonenumber=form.phonenumber.data, provider=form.provider.data)
        db.session.add(user)
        db.session.commit()
        message = f'Account created for {form.username.data}'
        return redirect(url_for('login', message=message))
        # return render_template('login.html', title='Login', form=form, offer_register="offer_register", message=message, complete="complete")
    return render_template('register.html', title='Register', form=form, offer_login="offer_login")

@app.route("/forgot", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('logout'))
    form = RequestResetForm()
    return render_template("reset_request.html", title="Reset Pasword", form=form)

@app.route("/forgot/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('logout'))
    user = User.verify_reset_token(token)
    if user is None:
        message = "This is an invalid or expired token"
        return redirect(url_for("forgot"))
    form = ResetPasswordForm()
    return render_template("forgot.html", title="Reset Pasword", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/account")
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        pass
    return render_template("account.html", title="Account", form=form, offer_logout_home="True")
