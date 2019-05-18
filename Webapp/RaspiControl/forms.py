from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
from RaspiControl.models import User, Appliances
from RaspiControl import db


services = [("@txt.att.net", "AT&T"), ("@messaging.sprintpcs.com", "Sprint"), 
            ("@vtext.com", "Verizon",), ("@tmomail.net", "T-Mobile"), ("@mymetropcs.com", "Metro PCS"), 
            ("@myboostmobile.com", "Boost Mobile"), ("@sms.mycricket.com", "Cricket")]

class RegistrationForm(FlaskForm):
    username = StringField('Username:',
                           validators=[DataRequired(), Length(min=4, max=32)])
    email = StringField('Email:', validators=[DataRequired(), Email()])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password:',
                                    validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    phonenumber = StringField("Phone Number:", validators=[DataRequired(), Length(min=10, max=11)])
    provider = SelectField("Service Provider:", choices=services)
    submit = SubmitField('Sign Up')
    remember = BooleanField('Remember Me') # dummy variable
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_phonenumber(self, phonenumber):
        user = User.query.filter_by(phonenumber=phonenumber.data).first()
        if user:
            raise ValidationError("That phone number is already in use. Please choose a different one.")


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired(), Length(min=4, max=32)])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Change Username:')
    email = StringField('Change Email:', validators=[Email()])
    password = PasswordField('Change Password: *', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password: *',
                                    validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    phonenumber = StringField("Change Phone Number:", validators=[DataRequired(), Length(min=10, max=11)])
    provider = SelectField("Change Service Provider:", choices=services)
    submit = SubmitField('Confirm Changes')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

    def validate_phonenumber(self, phonenumber):
        if phonenumber.data != current_user.phonenumber:
            user = User.query.filter_by(phonenumber=phonenumber.data).first()
            if user:
                raise validationError("That phone number is already in use. Please choose a different one.")


class RequestResetEmailForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class RequestResetTextForm(FlaskForm):
    phonenumber = StringField('Phone Number:', validators=[DataRequired(), Length(min=10, max=11)])
    submit = SubmitField('Request Password Reset')

    def validate_phonenumber(self, email):
        user = User.query.filter_by(email=phonenumber.data).first()
        if user is None:
            raise ValidationError('There is no account with that phone number. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password:',
                                    validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    submit = SubmitField('Reset Password')

class ApplianceForm(FlaskForm):
    pass


