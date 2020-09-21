from flask import request
from flask_wtf import Form
from flask_babel import gettext as _
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from .models import User

def email_exist(form, field):
    user = User.query.filter_by(email=field.data).first()
    if user: raise ValidationError(_('This e-mail address already exists.'))

class LoginForm(Form):
    email = StringField('email', validators=[DataRequired(message=_('E-mail is required.')), Length(1, 60), Email(message=_('You must enter an E-mail address.'))])
    password = PasswordField('password', validators=[DataRequired(message=_('Password is required.'))])
    remember_me = BooleanField('remember_me', default=False)

class RegisterForm(Form):
    email = StringField('email', validators=[DataRequired(message=_('E-mail is required.')), Length(1, 60), Email(message=_('You must enter an E-mail address.')), email_exist])
    password = PasswordField('password', validators=[DataRequired(message=_('Password is required.'))])
    password2 = PasswordField('confirm password', validators=[DataRequired(message=_('Confirm password is required.')), EqualTo('password', message=_('Passwords are not matched.'))])

class EditForm(Form):
    nickname = StringField('nickname', validators=[Length(min=0, max=64)])
    about_me =  TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append(_('This nickname has invalid characters. Please use letters, numbers, dots and underscores only.'))
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user:
            self.nickname.errors.append(_('This nickname is already in use. Please choose another one.'))
            return False
        return True

class PostForm(Form):
    post = StringField('post', validators=[DataRequired()])

class SearchForm(Form):
    search = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
