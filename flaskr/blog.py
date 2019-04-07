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
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
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
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username '
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        [id,]
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    if g.user is not None and post is not None:
        if check_author and post['author_id'] != g.user['id']:
            abort(403)

    return post


@bp.route('/<int:id>', methods=['GET'])
def look(id):
    post = get_post(id, check_author=False)
    return render_template('blog/look.html', post=post)


@bp.route('/<int:id>/upvote',methods=['POST'])
@login_required
def upvote(id):
    post = get_post(id)

    stuff = get_db().execute('SELECT pos '
                             ' FROM decision p JOIN user u ON p.user_id = u.id'
                             ' WHERE p.user_id = ? ', (g.user['id'])
                             ).fetchone()
    stuff2 = get_db().execute('SELECT neg '
                              ' FROM decision p JOIN user u ON p.user_id = u.id'
                              ' WHERE p.user_id = ? ', (g.user['id'])
                              ).fetchone()
    if " " + str(post.id) + " " in stuff:
        get_db().execute('UPDATE post SET votes = votes - 1')
        var = stuff.index(" " + str(post.id) + " ")
        stuff = stuff[0:var] + stuff[var + len(" " + str(post.id) + " "):]
        get_db().execute('UPDATE pos = ? '
                         ' FROM decision p JOIN user u ON p.user_id = u.id'
                         ' WHERE p.user_id = ? ', (stuff, g.user['id'])
                         )
        return redirect('blog.look', id)
    elif " " + str(post.id) + " " in stuff2:
        get_db().execute('UPDATE post SET votes = votes + 1')
        var = stuff2.index(" " + str(post.id) + " ")
        stuff2 = stuff2[0:var] + stuff2[var + len(" " + str(post.id) + " "):]
        get_db().execute('UPDATE neg = ? '
                         ' FROM decision p JOIN user u ON p.user_id = u.id'
                         ' WHERE p.user_id = ?', (stuff2, g.user['id'])
                         )
    get_db().execute('UPDATE post SET votes = votes + 1')
    get_db().execute('UPDATE pos = ? '
                     ' FROM decision p JOIN user u ON p.user_id = u.id'
                     ' WHERE p.user_id = ?', (stuff+" "+id+" ", g.user['id'])
                     )

    return redirect('blog.look', id)

@bp.route('/<int:id>/downvote',methods=['POST'])
@login_required
def downvote(id):
    post = get_post(id)

    stuff = get_db().execute('SELECT pos '
                             ' FROM decision p JOIN user u ON p.user_id = u.id'
                             ' WHERE p.user_id = ? ', (g.user['id'])
                             ).fetchone()
    stuff2 = get_db().execute('SELECT neg '
                              ' FROM decision p JOIN user u ON p.user_id = u.id'
                              ' WHERE p.user_id = ? ', (g.user['id'])
                              ).fetchone()
    if " " + str(post.id) + " " in stuff2:
        get_db().execute('UPDATE post SET votes = votes - 1')
        var = stuff2.index(" " + str(post.id) + " ")
        stuff2 = stuff2[0:var] + stuff2[var + len(" " + str(post.id) + " "):]
        get_db().execute('UPDATE pos = ? '
                         ' FROM decision p JOIN user u ON p.user_id = u.id'
                         ' WHERE p.user_id = ? ', (stuff2, g.user['id'])
                         )
        return redirect('blog.look', id)
    elif " " + str(post.id) + " " in stuff:
        get_db().execute('UPDATE post SET votes = votes + 1')
        var = stuff.index(" " + str(post.id) + " ")
        stuff = stuff[0:var] + stuff[var + len(" " + str(post.id) + " "):]
        get_db().execute('UPDATE neg = ? '
                         ' FROM decision p JOIN user u ON p.user_id = u.id'
                         ' WHERE p.user_id = ?', (stuff, g.user['id'])
                         )
    get_db().execute('UPDATE post SET votes = votes + 1')
    get_db().execute('UPDATE pos = ? '
                     ' FROM decision p JOIN user u ON p.user_id = u.id'
                     ' WHERE p.user_id = ?', (stuff2+" "+id+" ", g.user['id'])
                     )

    return redirect('blog.look', id)


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
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
