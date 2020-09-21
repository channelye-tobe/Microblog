from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from flask_babel import gettext as _
from app import app, db, lm, babel
from .forms import LoginForm, RegisterForm, EditForm, PostForm, SearchForm
from .models import User, Post
from datetime import datetime
from .emails import follower_notification
from langdetect import detect
from .translate import microsoft_translate

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        language = detect(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data,
                timestamp=datetime.utcnow(),
                author=g.user,
                language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is live now!'))
        return redirect(url_for('index'))
    posts = g.user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    return render_template('index.html',
        title='Home',
        posts=posts,
        form=form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        user = User.query.filter_by(email=form.email.data, password=form.password.data).first()
        if user:
          remember_me =False
          if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remenber_me', None)
            login_user(user, remember = remember_me)
          flash(_('Login succeed!'))
          return redirect(request.args.get('next') or url_for('index'))
        else:
            flash(_('Login fail! Please login in again.'))
            return redirect(url_for('login'))
    return render_template('login.html',
        title='Sign In',
        form=form)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        nickname = email.split('@')[0]
        nickname = User.make_valid_nickname(nickname)
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=email, password=password)
        user.followed.append(user)
        db.session.add(user)
        db.session.commit()
        flash(_('Register succeed! Please login.'))
        return redirect(url_for('login'))
    return render_template('register.html',
            form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if  user == None:
        flash(_('User %(nickname)s not found.', nickname=nickname))
        return redirect(url_for('index'))
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    return render_template('user.html',
        user=user,
        posts=posts)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname=form.nickname.data
        g.user.about_me=form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash(_('Changes are saved successfully.'))
    else:
        form.nickname.data=g.user.nickname
        form.about_me.data=g.user.about_me
    return render_template('edit.html',form=form)

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash(_('User %(nickname)s not found.', nickname=nickname))
        return redirect(url_for('index'))
    if user == g.user:
        flash(_('You can\'t follow yourself!'))
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash(_('You already follow %(nickname)s .', nickname=nickname))
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash(_('You are now following %(nickname)s .', nickname=nickname))
    follower_notification(g.user, user)
    return redirect(url_for('user', nickname=nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash(_('User %(nickname)s not found.', nickname=nickname))
        return redirect(url_for('index'))
    if user == g.user:
        flash(_('You can\'t unfollow yourself!'))
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash(_('You are not following %(nickname)s .', nickname=nickname))
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash(_('You have stopped following %(nickname)s .', nickname=nickname))
    return redirect(url_for('user', nickname=nickname))

@app.route('/delete_post/<post_id>')
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post == None:
        return redirect(request.referrer or url_for('index'))
    user = post.author
    if not user.id == g.user.id:
        flash(_('Sorry! You can\t delete this post!'))
        return redirect(request.referrer or url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash(_('Delete the post successfully!'))
    return redirect(request.referrer or url_for('index'))

@app.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts_per_page = request.args.get('posts_per_page', app.config['POSTS_PER_PAGE'], type=int)
    posts, total = Post.search(g.search_form.search.data, page, posts_per_page)
    next_url = url_for('search', search=g.search_form.search.data, page=page+1, posts_per_page=posts_per_page) if total > page * posts_per_page else None
    prev_url = url_for('search', search=g.search_form.search.data, page=page-1, posts_per_page=posts_per_page) if page > 1 else None
    return render_template(
        'search.html',
        title='Search',
        posts=posts,
        next_url=next_url,
        prev_url=prev_url)

@app.route('/translate', methods=['POST'])
@login_required
def translate():
    print('working')
    return jsonify({
        'text': microsoft_translate(
            request.form['text'],
            request.form['dest_lang'])
        })

@app.route('/test')
def test():
    return render_template('test.html', Markup=Markup)

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale=get_locale()
    print(g.locale)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())
