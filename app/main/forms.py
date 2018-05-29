#coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, \
    BooleanField, FileField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User
from flask_pagedown.fields import PageDownField


class EditProfileFrom(FlaskForm):
    upload_avatar = FileField(u'从本地上传图片作为头像')
    gender = SelectField(u'性别',
                         choices=[(u'男', u'男'), (u'女', u'女'), (u'保密', u'保密')])
    location = StringField(u'居住地')
    about_me = TextAreaField(u'个人介绍')
    submit = SubmitField(u'提交')


class EditProfileAdminForm(FlaskForm):
    upload_avatar = FileField(u'从本地上传图片作为头像')
    email = StringField(u'邮件', validators=[Required(), Length(1, 64), Email()])
    username = StringField(u"用户名", validators=[
        Required(), Length(1, 128), Regexp(u'^[a-zA-Z0-9\u4e00-\u9fa5]*$', 0,
                                           u'只能使用中文，英文，数字作为用户名')])
    confirmed = BooleanField(u'账户确认')
    role = SelectField(u'角色', coerce=int)
    gender = StringField(u'性别')
    location = StringField(u'居住地', validators=[Length(0, 64)])
    about_me = TextAreaField(u'个人介绍')
    submit = SubmitField(u'保存')
    
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已经被注册')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经被注册')

class PostForm(FlaskForm):
    title = TextAreaField(u'标题')
    summary = TextAreaField(u'摘要(在摘要卡片中显示)')
    body = PageDownField(u'正文', validators=[Required()])
    private = BooleanField(u'设为私密')

    submit = SubmitField(u'保存')

class CommentForm(FlaskForm):
    body = TextAreaField('', validators=[Required()])
    submit = SubmitField(u'发表')