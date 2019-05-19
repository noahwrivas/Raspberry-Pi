from flask import render_template, url_for, flash, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
# from flask_mail import Message
from RaspiControl.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                RequestResetEmailForm, RequestResetTextForm, ResetPasswordForm)
from RaspiControl.models import User, Appliances
from RaspiControl.communication import send_notification
from RaspiControl import app, bcrypt, db#, mail
# import os

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
        # return render_template('login.html', title='Login', form=form, offer_register="offer_register", message=message, complete="complete")
    return render_template('register.html', title='Register', form=form, offer_login=True, offer_forgot=True)

@app.route("/account")
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        pass
    return render_template("account.html", title="Account", form=form, offer_logout_home=True)

def send_reset_token(user, method):
    token = user.get_reset_token()
    message = f"""To reset your password, visit the following link:
    \
    {url_for('reset_token', token=token, _external=True)}
    \
    If you did not make this request then you should consider changing your information for your own protection.
    """
    if method == "email":
        send_notification(contact=user.email, method="email", subject="Password Reset Request", message=message)
        # msg = Message(subject="Password Reset Request", sender=os.environ.get("RASPICONTROL_EMAIL"), recipients=[user.email])
    else:
        send_notification(contact=user.phonenumber, method="email", subject="Password Reset Request", message=message, provider=user.provider)

        # msg = Message(subject="Password Reset Request", sender=os.environ.get("RASPICONTROL_EMAIL"), recipients=[f"{user.phonenumber}{user.provider}"])
    # msg.body = f"""To reset your password, visit the following link:
    
    # {url_for('reset_token', token=token, _external=True)}
    
    # If you did not make this request then you should consider changing your information for your own protection.
    # """
    # mail.send(msg)

@app.route("/forgot", defaults={"message" : ""})
@app.route("/forgot/<message>")
def forgot(message):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if message:
        return render_template("forgot.html", title="Forgot Password", offer_login=True, offer_register=True, message=message)
    return render_template("forgot.html", title="Forgot Password", offer_login=True, offer_register=True)

@app.route("/request-email", methods=["GET", "POST"])
def reset_request_email():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_token(user, "email")
        message = "An email has been sent to reset your password."
        return redirect(url_for("login", message=message))
    return render_template("reset_request_email.html", title="Reset Pasword", form=form, offer_login=True, offer_register=True)

@app.route("/request-text", methods=["GET", "POST"])
def reset_request_text():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetTextForm()
    if form.validate_on_submit():
        message = "A text has been sent to reset your password."
        return redirect(url_for("login", message=message))
    return render_template("reset_request_text.html", title="Reset Pasword", form=form, offer_login=True, offer_register=True)

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
        message = f'Password has been updated for {form.username.data}'
        return redirect(url_for('login', message=message))
    return render_template("reset_request.html", title="Reset Pasword", form=form, offer_login=True, offer_register=True)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))