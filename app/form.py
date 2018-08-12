from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from app.models import User
from flask_babel import lazy_gettext as _l

# login form#


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField('Sign In')


# Register form#
class RegisterForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired()])
    submit = SubmitField(_l('Register'))

    # username = StringField('Username', validators=[DataRequired()])
    # email = StringField('Email', validators=[DataRequired(), Email()])
    # password = PasswordField('Password', validators=[DataRequired()])
    # password2 = PasswordField(
    #     'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    # submit = SubmitField('Register')


def validate_user(self, username):
    user = User.query.filter_by(name=username.data).first()
    if user is not None:
        raise ValidationError('Please use a different username.')


def validate_email(self, email):
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


#  submit posts form#


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=400)])
    submit = SubmitField('Submit')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Reset Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')