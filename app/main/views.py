#coding:utf-8
import os
from flask import render_template, session, redirect, url_for, \
    flash, request, current_app, abort, make_response
from datetime import datetime
from ..email import send_email
from . import main
from .forms import EditProfileFrom, EditProfileAdminForm, PostForm, CommentForm
from .. import db
from ..models import User, Role, Post, Comment
from flask_login import login_user, logout_user, login_required, current_user
from ..decorators import admin_required, permission_required
from ..models import Permission
from PIL import Image


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts,
                           show_followed=show_followed, pagination=pagination)

@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp



@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return 'admin'

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderator_only():
    return 'moderator'

@main.route('/user/<int:id>')
@login_required
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)

@main.route('/edit-profile/', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileFrom()
    if request.method == 'POST':
        current_user.gender = form.gender.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data

        im = form.upload_avatar.data
        if not im:
            pass
        else:
            postfix = im.filename.split('.')[-1]
            filename = '%s_avatar.%s' %(current_user.id, postfix)
            IMAGES = 'jpg jpe jpeg png gif svg bmp'.split()
            if postfix not in IMAGES:
                flash(u'只能上传图片文件')
                return redirect(url_for('.edit_profile', id=current_user))
            url = os.path.join(
                current_app.config['UPLOADED_AVATAR_DEST'], filename)
            #头像方形剪裁
            im = Image.open(im)
            x = im.size[0]
            y = im.size[1]
            x1 = x / 2 - 400
            x2 = x / 2 + 400
            y1 = y / 2 - 400
            y2 = y / 2 + 400
            if x1 < 0 and x < y:
                x1 = 0
                x2 = x
                y1 = y / 2 - x / 2
                y2 = y / 2 + x / 2
            if y1 < 0 and x > y:
                y1 = 0
                y2 = y
                x1 = x / 2 - y / 2
                y2 = x / 2 + y / 2
            box = (x1, y1, x2, y2)
            im.crop(box).save(url)
            current_user.avatar_url = filename
            current_user.avatar_default = False
        db.session.add(current_user)
        flash(u"你的资料已经更新。")
        return redirect(url_for('.user', id=current_user.id))
    form.gender.data = current_user.gender
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit-profile.html', form=form, user=current_user)

@main.route('/edit_profile/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if request.method == 'POST':
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.gender = form.gender.data
        user.location = form.location.data
        user.about_me = form.about_me.data

        im = form.upload_avatar.data
        if im is None:
            pass
        else:
            postfix = im.filename.split('.')[-1]
            filename = '%s_avatar.%s' %(user.id, postfix)
            IMAGES = 'jpg jpe jpeg png gif svg bmp'.split()
            if postfix not in IMAGES:
                flash(u'只能上传图片文件')
                return redirect(url_for('.edit_profile',id=user.id))
            url = os.path.join(
                current_app.config['UPLOADED_AVATAR_DEST'], filename)
            #头像方形剪裁
            im = Image.open(im)
            x = im.size[0]
            y = im.size[1]
            x1 = x / 2 - 400
            x2 = x / 2 + 400
            y1 = y / 2 - 400
            y2 = y / 2 + 400
            if x1 < 0 and x < y:
                x1 = 0
                x2 = x
                y1 = y / 2 - x / 2
                y2 = y / 2 + x / 2
            if y1 < 0 and x > y:
                y1 = 0
                y2 = y
                x1 = x / 2 - y / 2
                y2 = x / 2 + y / 2
            box = (x1, y1, x2, y2)
            im.crop(box).save(url)
            user.avatar_url = filename
            user.avatar_default = False
        db.session.add(user)
        flash(u'资料已经更新')
        return redirect(url_for('.user', id=user.id))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.gender.data = user.gender
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit-profile.html', form=form, user=user)


@main.route('/individual-homepage/<int:id>', methods=['GET', 'POST'])
@login_required
def individual_homepage(id):
    user = User.query.filter_by(id=id).first_or_404()
    if current_user.id != user.id and not current_user.is_administrator():
        abort(403)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('individual-homepage.html', user=user, posts=posts)

@main.route('/individual-homepage/')
@login_required
def individual_nohomepage():
    pass


@main.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(title=form.title.data, summary=form.summary.data,
                    body=form.body.data, private=form.private.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.individual_homepage',
                                id=current_user.id))
    form.private = False
    return render_template('write.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    if post.private is True and current_user.id != post.author.id:
        abort(403)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash(u'评论已经发表')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
               current_app.config['FLASKY_POSTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', post=post, comments=comments,
                           pagination=pagination, form=form)

@main.route('/delete-post/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    if post.author.id == current_user.id:
        db.session.delete(post)
        flash(u'文章已经删除')
    else:
        abort(403)
    return redirect(url_for('.individual_homepage',
                            id=current_user.id))

@main.route('/admin-delete-post/<int:id>')
@login_required
@admin_required
def admin_delete_post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    db.session.delete(post)
    flash(u'文章已经删除')
    return redirect(url_for('.index'))

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
        not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.summary=form.summary.data
        post.body=form.body.data
        post.private=form.private.data
        db.session.add(post)
        flash(u'文章修改成功')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.summary.data = post.summary
    form.body.data = post.body
    form.private.data = post.private
    return render_template('edit-post.html', form=form, post=post)

@main.route('/follow/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash(u'关注的用户不存在')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'您已经关注过此用户了')
        return redirect(url_for('.index'))
    current_user.follow(user)
    flash(u'关注%s成功' %user.username)
    return redirect(url_for('.user', id=id))

@main.route('/unfollow/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash(u'用户不存在')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(u'你已经关注过此用户了')
        return redirect(url_for('.user', id=id))
    current_user.unfollow(user)
    flash(u'取消关注成功%s' % user.username)
    return redirect(url_for('.user', id=id))

@main.route('/followers/<int:id>')
def followers(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash(u'用户不存在')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, endpoint='.followers',
                           title=u"被关注",
                           pagination=pagination, follows=follows)

@main.route('/followed-by/<int:id>')
def followed_by(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title=u"关注",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments, pagination=pagination,
                           page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disable = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disable = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))