import logging
import math
from flask import Blueprint, redirect, jsonify, session, render_template, request, url_for

from heap import db
from heap.models import User
from .decorators import login_required, login_required_redirect

logger = logging.getLogger(__name__)

ui_blueprint = Blueprint('ui', __name__)

@ui_blueprint.route('/')
def index_view():
    #pylint: disable=line-too-long
    return redirect('https://chrome.google.com/webstore/detail/heap/akihlilfonpbgdknmchpcfplohchpipa')

@ui_blueprint.route('/signup/', methods=['GET'])
def signup_view():
    return render_template('signup.html')

@ui_blueprint.route('/signup/', methods=['POST'])
def signup_post():
    user = User.query.filter(User.email == request.form.get('email')).first()
    if user:
        return jsonify({'error': user})
    user = User(email=request.form.get('email'), password=request.form.get('password'))
    db.session.add(user)
    db.session.commit()
    session['user'] = user.id
    return jsonify({'url': url_for('ui.feeds_view')})

@ui_blueprint.route('/signin/', methods=['GET'])
def signin_view():
    return render_template('signin.html')

@ui_blueprint.route('/signin/', methods=['POST'])
def signin_post():
    if User.verify(email=request.form.get('email'), password=request.form.get('password')):
        session['user'] = User.query.filter(User.email == request.form.get('email')).first().id
        return jsonify({'url': url_for('ui.items_view')})
    return jsonify({'error': True})

@ui_blueprint.route('/signout/', methods=['POST'])
def signout_post():
    session.pop('user', None)
    return jsonify({'url': url_for('ui.account_view')})

@ui_blueprint.route('/csrf/')
def csrf_view():
    return render_template('csrf.html')

@ui_blueprint.route('/settings/', methods=['GET'])
@login_required_redirect
def settings_view():
    user = User.query.get(session['user'])
    items = []
    for source in user.sources:
        items = items + source.items.all()
    message = messages.get(request.args.get('message'))
    data = {
        'user': user,
        'sources': user.sources,
        'item': items,
        'message': message
    }
    return render_template('settings.html', **data)

@ui_blueprint.route('/account/', methods=['GET'])
@login_required_redirect
def account_view():
    user = User.query.get(session['user'])
    message = messages.get(request.args.get('message'))
    return render_template('account.html', user=user, message=message)

@ui_blueprint.route('/account/', methods=['POST'])
@login_required
def account_post():
    user = User.query.get(session['user'])
    if request.form.get('email'):
        user.email = request.form.get('email')
    if request.form.get('password'):
        user.set_password(request.form.get('password'))
    db.session.commit()
    return jsonify({'success': True})

@ui_blueprint.route('/feeds/', methods=['GET'])
@login_required_redirect
def feeds_view():
    message = messages.get(request.args.get('message'))
    user = User.query.get(session['user'])
    return render_template('feeds.html', message=message, sources=user.sources)

@ui_blueprint.route('/items/', methods=['GET'])
@login_required_redirect
def items_view():
    message = messages.get(request.args.get('message'))
    user = User.query.get(session['user'])
    data = {'user': user, 'message': message, 'sources': user.sources}
    return render_template('items.html', **data)

@ui_blueprint.route('/list_items/', methods=['POST'])
@login_required_redirect
def list_items_view():
    page = int(request.form.get('page', 1)) - 1
    source_ids = request.form.getlist('sources[]')
    user = User.query.get(session['user'])
    items = []
    for source in user.sources:
        if str(source.id) in source_ids:
            items = items + [item.dictify() for item in source.items]
    return jsonify({
        'items': items[page*25:(page+1)*25],
        'total': math.ceil(len(items) / 25)
    })

#pylint: disable=line-too-long
messages = {
    'new': 'Hi! This is your dashboard. You can add and delete rss, Hacker News, and Reddit subscriptions here!',
    'empty': 'Wow! Looks like you\'ve gone through all your queued items! Great job! Why not add some more subscriptions?',
    'reddit_add': 'Great! You\'ve just added a reddit subscription!'
}
