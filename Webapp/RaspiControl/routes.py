from flask import render_template, url_for, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from RaspiControl.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                RequestResetEmailForm, ResetPasswordForm)
from RaspiControl.models import User, Appliances
from RaspiControl.communication import CommunicationSending
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
        return render_template('login.html', title='Login', form=form, offer_register=True, offer_forgot=True, message=message)
    if message:
        return render_template('login.html', title='Login', form=form, offer_register=True, offer_forgot=True, message=message)
    return render_template('login.html', title='Login', form=form, offer_register=True, offer_forgot=True)

@app.route("/home")
@login_required
def home():
    return render_template("home.html", title="Home", offer_logout_account=True)

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
    return render_template('register.html', title='Register', form=form, offer_login=True, offer_forgot=True)

@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account", offer_logout_home=True)

@app.route("/account/update/<selected>")
@app.route("/account/update", defaults={"selected" : ""})
@login_required
def update_account(selected):
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.username.data != "":
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password, 
                        phonenumber=form.phonenumber.data, provider=form.provider.data)
            db.session.add(user)
            db.session.commit()
            message = f'Account created for {form.username.data}'
        return redirect(url_for('login', message=message))
    return render_template("account.html", title="Account", form=form, offer_logout_home=True)

@app.route("/forgot", defaults={"message" : ""}, methods=["GET", "POST"])
@app.route("/forgot/<message>", methods=["GET", "POST"])
def forgot(message):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        CommunicationSending(contact=form.email.data, subject="Reset Password", user=user).send_reset_token()
        message = "An email has been sent to reset your password."
        return redirect(url_for("login", message=message))
    if message:
        return render_template("forgot.html", title="Forgot Password", form=form, offer_login=True, offer_register=True, message=message)
    return render_template("forgot.html", title="Forgot Pasword", form=form, offer_login=True, offer_register=True)

@app.route("/request/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        message = "This is an invalid or expired token"
        return redirect(url_for("forgot", message=message))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        message = f'Password has been updated for {user.username}'
        return redirect(url_for('login', message=message))
    return render_template("reset_token.html", title="Reset Pasword", form=form, offer_login=True, offer_register=True)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))