from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
from RaspiControl.models import User, Appliances
from RaspiControl import db

# Allowed service providers with email to text functionality
services = [("@txt.att.net", "AT&T"), ("@messaging.sprintpcs.com", "Sprint"), 
            ("@vtext.com", "Verizon",), ("@tmomail.net", "T-Mobile"), ("@mymetropcs.com", "Metro PCS"), 
            ("@myboostmobile.com", "Boost Mobile"), ("@sms.mycricket.com", "Cricket")]

class RegistrationForm(FlaskForm):
    """ Registration Data Form """
    username = StringField('Username:',
                           validators=[DataRequired(), Length(min=4, max=32)])
    email = StringField('Email:', validators=[DataRequired(), Email()])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password:',
                                    validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    phonenumber = IntegerField('Phone Number:', validators=[DataRequired(), 
                                                            NumberRange(min=1111111111, 
                                                                        max=99999999999, 
                                                                        message='Must be a valid phone number.')])    
    provider = SelectField("Service Provider:", choices=services)
    submit = SubmitField('Sign Up')
    # remember = BooleanField('Remember Me') # dummy variable
    
    def validate_username(self, username):
        """ Check if Username Already Exists in Database """
        user = User.query.filter_by(username=username.data.upper()).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """ Check if Email Already Exists in Database"""
        user = User.query.filter_by(email=email.data.upper()).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_phonenumber(self, phonenumber):
        """ Check if Phone Number Already Exists in Database """
        user = User.query.filter_by(phonenumber=phonenumber.data).first()
        if user:
            raise ValidationError("That phone number is already in use. Please choose a different one.")


class LoginForm(FlaskForm):
    """ Login Form """
    username = StringField('Username:', validators=[DataRequired(), Length(min=4, max=32)])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    """ Update Account Form """
    username = StringField('Change Username:', validators=[DataRequired(), Length(min=4, max=32)])
    email = StringField('Change Email:', validators=[Email()])
    old_password = PasswordField('Old Password:', validators=[DataRequired(), Length(min=6, max=60)])
    new_password = PasswordField('New Password:', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password:',
                                    validators=[DataRequired(), EqualTo('new_password', message="Passwords must match")])
    phonenumber = IntegerField('Change Phone Number:', validators=[DataRequired(), 
                                                                    NumberRange(min=1111111111, max=99999999999, 
                                                                                message='Must be a valid US phone number.')])    
    provider = SelectField("Change Service Provider:", choices=services)
    submit = SubmitField('Submit Changes')

    def validate_username(self, username):
        """ Check if Username Already Exists in Database """
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data.upper()).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """ Check if Email Already Exists in Database """
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data.upper()).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

    def validate_phonenumber(self, phonenumber):
        """ Check if Phone Number Already Exists in Database """
        if phonenumber.data != current_user.phonenumber:
            user = User.query.filter_by(phonenumber=phonenumber.data).first()
            if user:
                raise validationError("That phone number is already in use. Please choose a different one.")


class RequestResetEmailForm(FlaskForm):
    """ Request Password Form """
    email = StringField('Email:', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        """ Ensure Email is in Use """
        user = User.query.filter_by(email=email.data.upper()).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    """ Reset Password Form """
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password:',
                                    validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    submit = SubmitField('Reset Password')

class DeleteAccountForm(FlaskForm):
    """ Update Account Form """
    confirm_password = PasswordField('Confirm Password:', validators=[DataRequired(), Length(min=6, max=60)])
    submit = SubmitField('Delete Account')


class ApplianceForm(FlaskForm):
    pass


