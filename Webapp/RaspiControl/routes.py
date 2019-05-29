from flask import render_template, url_for, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from RaspiControl.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                RequestResetEmailForm, ResetPasswordForm, services,
                                DeleteAccountForm)
from RaspiControl.models import User, Appliances
from RaspiControl.communication import CommunicationSending
from RaspiControl import app, bcrypt, db
import re

@app.route("/")
def default():
    """ Create database if none is detected """
    try:
        _ = User.query.all()
    except:
        db.create_all()
    return redirect(url_for("login"))

@app.route("/login", defaults={"message" : ""}, methods=["GET", "POST"])
@app.route("/login/<message>", methods=["GET", "POST"])
def login(message):
    """ Login Page """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.upper()).first()
        print(form.password.data)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            message = "Login Unsuccessful. Please check username and password."
        return render_template('login.html', title='Login', form=form, offer_register=True, offer_forgot=True, message=message)
    if message:
        return render_template('login.html', title='Login', form=form, offer_register=True, offer_forgot=True, message=message)
    return render_template('login.html', title='Login', form=form, offer_register=True, offer_forgot=True)

@app.route("/home")
@login_required
def home():
    """ Home Page """
    return render_template("home.html", title="Home", offer_logout_account=True)

@app.route("/register", methods=['GET', 'POST'])
def register():
    """ Register Page  """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data.upper(), display_username=form.username.data, 
                    email=form.email.data.upper(), display_email=form.email.data, password=hashed_password, 
                    phonenumber=form.phonenumber.data, provider=form.provider.data)
        db.session.add(user)
        db.session.commit()
        message = f'Account created for {form.username.data}'
        return redirect(url_for('login', message=message))
    return render_template('register.html', title='Register', form=form, offer_login=True, offer_forgot=True)

@app.route("/account/display", methods=["GET", "POST"])
@login_required
def account():
    """ Account Info Page """
    provider = dict(services).get(current_user.provider)
    return render_template("account_info.html", title="Account", provider=provider, offer_logout_home=True)

@app.route("/account/update", defaults={"selected" : None}, methods=["GET", "POST"])
@app.route("/account/update/<selected>", methods=["GET", "POST"])
@login_required
def update_account(selected):
    """ Update Account Page """
    form = UpdateAccountForm()
    print("Top: ", form.errors)
    if request.method == "POST": # load in values when submiting a post request to satisify data requirment
        if selected == "Username":
            form.new_password.data = form.confirm_password.data
            form.old_password.data = current_user.password            
            form.email.data = current_user.email
            form.phonenumber.data = current_user.phonenumber
            form.provider.data = current_user.provider
        elif selected == "Email":
            form.new_password.data = form.confirm_password.data
            form.old_password.data = current_user.password
            form.username.data = current_user.username
            form.phonenumber.data = current_user.phonenumber
            form.provider.data = current_user.provider
        elif selected == "Password":
            form.username.data = current_user.username
            form.email.data = current_user.email
            form.phonenumber.data = current_user.phonenumber
            form.provider.data = current_user.provider
        elif selected == "Phonenumber":
            form.new_password.data = form.confirm_password.data
            form.old_password.data = current_user.password
            form.username.data = current_user.username
            form.email.data = current_user.email
            form.provider.data = current_user.provider
        elif selected == "Provider":
            form.new_password.data = form.confirm_password.data
            form.old_password.data = current_user.password
            form.username.data = current_user.username
            form.phonenumber.data = current_user.phonenumber
            form.email.data = current_user.email
    if form.validate_on_submit():
        print("\nSubmit\n")
        print(form.confirm_password.data)
        if bcrypt.check_password_hash(current_user.password, form.confirm_password.data):
            print("Check")
            if selected == "Username":
                print("Username")
                current_user.username = form.username.data.upper()
                current_user.display_username = form.username.data
            elif selected == "Email":
                current_user.email = form.email.data.upper()
                current_user.display_email = form.email.data
            elif selected == "Phonenumber":
                current_user.phonenumber = form.phonenumber.data
            elif selected == "Provider":
                current_user.provider = form.provider.data
        elif selected == "Password":
            if bcrypt.check_password_hash(current_user.password, form.old_password.data):
                hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
                current_user.password = hashed_password
        else:
            message = "Incorrect Password"
            print(form.confirm_password.data)
            print("Bottom: ", form.errors)
            return render_template("update_account.html", title="Account", selected=selected, message=message, form=form, offer_logout_home=True)
        db.session.commit()
        message = f'{selected} updated for {current_user.display_username}'
        logout_user()
        return redirect(url_for('login', message=message))
    print(f"user:\t{form.username.data}\npass:\t{form.new_password.data}\nemail:\t{form.email.data}\nphonenumber:\t{form.phonenumber.data}\nprovider:\t{form.provider.data}")
    print(form.confirm_password.data)
    print("Bottom: ", form.errors)
    return render_template("update_account.html", title="Account", selected=selected, form=form, offer_logout_home=True)

@login_required
@app.route("/account/delete", methods=["GET", "POST"])
def delete_account():
    """ Delete Account Page """
    form = DeleteAccountForm()
    if form.validate_on_submit() and bcrypt.check_password_hash(current_user.password, form.confirm_password.data):
        user = User.query.filter_by(username=current_user.username).first()
        message = f"Account for {current_user.display_username} has been deleted"
        logout_user()
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("login", message=message))
    return render_template("update_account.html", title="Account", selected="Delete", form=form, offer_logout_home=True)

@app.route("/forgot", defaults={"message" : ""}, methods=["GET", "POST"])
@app.route("/forgot/<message>", methods=["GET", "POST"])
def forgot(message):
    """ Forgot Password Page """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.upper()).first()
        CommunicationSending(contact=form.email.data, subject="Reset Password", user=user).send_reset_token()
        message = "An email has been sent to reset your password."
        return redirect(url_for("login", message=message))
    if message:
        return render_template("forgot.html", title="Forgot Password", form=form, offer_login=True, offer_register=True, message=message)
    return render_template("forgot.html", title="Forgot Pasword", form=form, offer_login=True, offer_register=True)

@app.route("/request/<token>", methods=["GET", "POST"])
def reset_token(token):
    """ Verify Reset Token, Reset Password Page """
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
        message = f'Password has been updated for {user.display_username}'
        return redirect(url_for('login', message=message))
    return render_template("reset_token.html", title="Reset Pasword", form=form, offer_login=True, offer_register=True)

@app.route("/logout")
def logout():
    """ Logout Current User """
    logout_user()
    return redirect(url_for('login'))