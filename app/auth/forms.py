#coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class RegistrationForm(FlaskForm):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    username = StringField(u"用户名", validators=[
        Required(), Length(1, 128), Regexp(u'^[a-zA-Z0-9\u4e00-\u9fa5]*$', 0,
                                           u'只能使用中文，英文，数字作为用户名')])
    password = PasswordField(u"密码", validators=[
        Required(), EqualTo('password2', message=u'两次输入密码不同')])
    password2 = PasswordField(u"确认密码", validators=[Required()])
    submit = SubmitField(u"注册")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u"邮箱已经被注册")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u"用户名已经被使用")


class LoginForm(FlaskForm):
    email = StringField(u"邮箱", validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u"密码", validators=[Required()])
    remember_me = BooleanField(u"记住我")
    submit = SubmitField(u"登录")


class ModifyPasswordForm(FlaskForm):
    old_password = PasswordField(u'旧密码', validators=[Required()])
    password = PasswordField(u"新密码", validators=[
        Required(), EqualTo('password2', message=u'两次输入密码不同')])
    password2 = PasswordField(u"确认新密码", validators=[Required()])
    submit = SubmitField(u'确认修改')


class PasswordResetRequestForm(FlaskForm):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    summit = SubmitField(u'确认')


class PasswordResetForm(FlaskForm):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u'新密码', validators=[Required(), EqualTo('password2', message=u'两次密码输入不一样')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'确认')


class ModifyEmailForm(FlaskForm):
    email = StringField(u'新邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[Required()])
    submit = SubmitField(u'确认修改')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u"邮箱已经被注册")


