from flask import jsonify, request, url_for, current_app
from . import api
from ..models import User, Post

@api.route('/users/<int:id>')
def get_user(id):
    user=User.query.get(id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'last_seen': user.last_seen
    })


@api.route('/user/<int:id>/posts/', methods=['GET'])
def get_user_posts(id):
    page=request.args.get('page', 1, type=int)
    pagination=Post.query.filter(Post.author_id==id).paginate(page=page, per_page=current_app.config['FLASKY_API_POST_PER_PAGE'], error_out=False)
    posts=pagination.items
    prev=None
    if pagination.has_prev:
        prev=url_for('api.get_user_posts', id=id, page=page-1)
    next=None
    if pagination.has_next:
        next=url_for('api.get_user_posts', id=id,page=page+1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev_url': prev,
        'next_url': next,
        'count': pagination.total
    })

@api.route('/user/<int:id>/timeline/', methods=['GET'])
def post_followed_user(id):
    page=request.args.get('page',1, type=int)
    pagination=Post.query.order_by(Post.timestamp.desc()).filter(Post.author_id==id).paginate(page=page, per_page=current_app.config['FLASKY_API_POST_PER_PAGE'], error_out=False)
    posts=pagination.items
    prev=None
    if pagination.has_prev:
        prev=url_for('api.post_followed_user', id=id, page=page-1)
    next=None
    if pagination.has_next:
        next=url_for('api.post_followed_user', id=id, page=page+1)
    return jsonify({
        'username': User.query.get(id).username,
        'prev_url': prev,
        'next_url': next,
        'posts': [post.to_json() for post in posts]
    })

@api.route('/test/')
def test():
    print('Headers ', request.headers.get('Authorization'))
    print('You are catched me.')
    return jsonify({
        'mes': 'You catch me'
    })