#coding:utf-8
import os
from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm, ModifyPasswordForm, ModifyEmailForm, \
    PasswordResetForm, PasswordResetRequestForm
from ..email import send_email




@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'用户名或密码不对')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u"您已经登出")
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        token = user.generate_confirmation_token()
        send_email(user.email, u"确认你的账户", 'auth/email/confirm', user=user, token=token)
        flash(u"账户确认邮件已经发送到您的邮箱，请及时确认。")
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(u"您已经确认您的账户，谢谢！^-^")
    else:
        flash(u"确认链接已经失效......")
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
                and not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, u"确认你的账户",
               'auth/email/confirm', user=current_user, token=token)
    flash(u'一封信的确认邮件已经发送到您的邮箱！(*^_^*)')
    return redirect(url_for('main.index'))

@auth.route('/modify-password', methods=['GET', 'POST'])
@login_required
def modify_password():
    form = ModifyPasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash(u'密码修改成功！')
            return redirect(url_for('main.index'))
        else:
            flash(u'原密码错误！')
    return render_template('auth/modify_password.html', form=form)

@auth.route('/reset', methods=['GET','POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(form.email.data, u'重置密码', 'auth/email/reset_password',
                       user=user, token=token, next=request.args.get('next'))
            flash(u'重置密码邮件已经发送至您的邮箱！')
            return redirect(url_for('.login'))
        else:
            flash(u'此邮箱未注册')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash(u'密码已经重置成功！')
            return redirect(url_for('.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/modify-email', methods=['GET', 'POST'])
@login_required
def modify_email_request():
    form = ModifyEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_modify_token(new_email)
            send_email(new_email, u'确认你的新邮箱',
                       'auth/email/modify_email',
                       user=current_user, token=token)
            flash(u'一封新邮箱确认邮件已经发送到您的新邮箱')
            return redirect(url_for('main.index'))
        else:
            flash(u'邮箱或密码输入错误')
    return render_template("auth/modify_email.html", form=form)

@auth.route('/modify-email/<token>')
@login_required
def modify_email(token):
    if current_user.modify_email(token):
        flash(u'邮箱已经更换')
    else:
        flash(u'邮箱更换失败')
    return redirect(url_for('main.index'))
