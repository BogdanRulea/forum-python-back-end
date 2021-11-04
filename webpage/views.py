from operator import pos
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user,login_required
from werkzeug.utils import validate_arguments
from .models import Comment, Post, User, Like
from . import db
from datetime import datetime


views = Blueprint("views" , __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("homepage.html", user = current_user, posts = posts)

@views.route("/create-post", methods = ['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category = 'error')
        else:
            post = Post(text = text, author = current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
        
        return redirect(url_for('views.home'))
    return render_template("create_post.html", user = current_user)

@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    
    post = Post.query.filter_by(id = id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.username != post.user.username:
        flash("You can't delete this post.", category='error')
    else:
        for comment in post.comments:
            db.session.delete(comment)
        for like in post.likes:
            db.session.delete(like)

        db.session.delete(post)
        db.session.commit()
        flash("Post deleted!", category='success')
    
    return redirect(url_for('views.home'))

@views.route("/edit-post/<post_id>", methods = ["POST", "GET"])
@login_required
def edit_post(post_id):
    post = Post.query.filter_by(id = post_id).first()
    if request.method == "POST":

        if not post:
            flash("Post does not exist.", category='error')
        elif current_user.username != post.user.username:
            flash("You cannot edit this post.", category='error')
        else:
            text = request.form.get('text')
            post.text = text
            db.session.commit()
        return redirect(url_for('views.home'))

            
    return render_template("edit_post.html", user = current_user, post=post)


@views.route('/posts/<username>')
@login_required
def posts(username):
    user = User.query.filter_by(username = username).first()
    posts = user.posts

    return render_template('posts.html', user=current_user, posts = posts, username = username)


@views.route('/create-comment/<post_id>', methods = ['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id = post_id)
        if post:
            comment = Comment(text = text, author = current_user.id, post_id = post_id)
            
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')
    
    return redirect(url_for('views.home'))


@views.route('/delete-comment/<comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id = comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have the permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
    
    return redirect(url_for('views.home'))

@views.route('/edit-comment/<postId>/<commentId>', methods  = ["POST", "GET"])
@login_required
def edit_com(postId, commentId):
    post = Post.query.filter_by(id = postId).first()
    comment = Comment.query.filter_by(post_id = postId, id = commentId).first()
    user = User.query.filter_by(id = post.author).first()
    if request.method == "POST":
        if not post:
            flash("Post does not exist", category='error')
        elif not comment:
            flash("Comment does not exist.", category='error')
        elif comment.author != current_user.id:
            flash("You cannot edit this comment.", category='error')
        else:
            text = request.form.get('text')
            comment.text = text
            db.session.commit()
        return redirect(url_for('views.home'))
    
    return render_template('edit_comment.html',user = current_user, comment = comment, post = post, username = user.username)


@views.route("/like-post/<post_id>", methods = ["POST"])
@login_required
def like(post_id):

    post = Post.query.filter_by(id = post_id).first()
    like = Like.query.filter_by(author = current_user.id, post_id = post_id).first()

    if not post:
        return jsonify({'error' : 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author = current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
    
    return jsonify({"likes" : len(post.likes), "liked" : current_user.id in map(lambda x: x.author, post.likes)})

@views.route('/profile/<userName>')
@login_required
def profile(userName):

    user = User.query.filter_by(username = userName).first()

    if not user:
        flash('User does not exist.', category='error')
    else:
        return render_template('user_profile.html', user = user)
    
    return redirect(url_for('views.home'))

