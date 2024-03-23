from flask import jsonify, request,g, url_for
from . import api
from ..models import Comment, db

@api.route('/comment/<int:id>')
def get_comment(id):
    comment=Comment.query.get_or_404(id)
    return jsonify(comment.to_json())
    

@api.route('/post/comments/<int:id>')
def get_post_comments(id):
    comments=Comment.query.filter_by(post_id=id).all()
    return jsonify({
        'comments': [comment.body_html for comment in comments]
    })

@api.route('/post/<int:id>/comment', methods=['POST'])
def new_comment(id):
    new_comment=Comment.from_json(request.json)
    new_comment.author=g.current_user
    new_comment.post_id=id
    db.session.add(new_comment)
    db.session.commit()
    return jsonify(new_comment.to_json()), 201, {'Location': url_for('api.get_comment', id=new_comment.id)}