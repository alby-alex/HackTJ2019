from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, writer, author_id, votes'
        ' FROM post p '
        ' ORDER BY votes DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, writer, votes)'
                ' VALUES (?, ?, ?, ?, 0)',
                (title, body, g.user['id'], g.user['username'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, writer, votes '
        ' FROM post p'
        ' WHERE p.id = ?',
        [id, ]
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    if g.user is not None and post is not None:
        if check_author and post['author_id'] != g.user['id']:
            abort(403)

    return post
@bp.route('/<int:id>/comment', methods = ['GET', 'POST'])
@login_required
def comment(id):
    if request.method=='POST':
        writer = g.user['username']
        body = request.form['body']
        if body is None:
            flash("body of comment cannot be null")
        get_db().execute(
            'INSERT INTO comment (writer, body, id)'
            ' VALUES (?, ?, ?)',
            (writer, body, id)
        )
        get_db().commit()
        return redirect(url_for('blog.look', id=id))

    return render_template('blog/comment.html', post = get_post(id, check_author=False))


@bp.route('/<int:id>', methods=['GET'])
def look(id):
    post = get_post(id, check_author=False)
    db = get_db()
    comments = db.execute(
        'SELECT body, writer, created'
        ' FROM comment p '
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/look.html', post=post, comment= comments)


@bp.route('/<int:id>/upvote', methods=['GET', 'POST'])
@login_required
def upvote(id):
    post = get_post(id, check_author=False)
    get_db().execute('UPDATE post SET votes = ? WHERE id = ?', ((post['votes'] + 1), id)
                     )
    get_db().commit()
    return redirect(url_for('blog.look', id=id))


@bp.route('/<int:id>/downvote', methods=['GET', 'POST'])
@login_required
def downvote(id):
    post = get_post(id, check_author=False)
    get_db().execute('UPDATE post SET votes = ? WHERE id = ?', ((post['votes'] - 1), id)
                     )
    get_db().commit()

    return redirect(url_for('blog.look', id=id))


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.look', id=id))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
