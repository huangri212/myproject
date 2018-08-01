from flask_wtf import FlaskForm
from flask import render_template, flash, redirect
from wtforms import StringField, BooleanField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms import validators
from app.models import User


# login form#
class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


# Register form#
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    # username = StringField('Username', validators=[DataRequired()])
    # email = StringField('Email', validators=[DataRequired(), Email()])
    # password = PasswordField('Password', validators=[DataRequired()])
    # password2 = PasswordField(
    #     'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    # submit = SubmitField('Register')

    @staticmethod
    def validate_user(username):
        user = User.query.filter_by(name=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    @staticmethod
    def validate_email(email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


# Profile update form #


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(name=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
            else:
                raise ValidationError('this user is not exist')
