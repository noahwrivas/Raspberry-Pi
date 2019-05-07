from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
from raspicontrol.models import User, Appliances


class RegistrationForm(FlaskForm):
    username = StringField('Username:',
                           validators=[DataRequired(), Length(min=4, max=32)])
    email = StringField('Email:',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password:',
                                    validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
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


class LoginForm(FlaskForm):
    username = StringField('Username:',
                           validators=[DataRequired(), Length(min=4, max=32)])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ApplianceForm(FlaskForm):
    pass