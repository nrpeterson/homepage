from math import ceil
import datetime
from flask import request, session, g, redirect, url_for, abort, \
        render_template, flash
from sqlalchemy import desc, not_
from homepage import app, db
from homepage.database import Post, Category, Keyword
from homepage.helpers import urlize, unurlize

@app.route('/')
def index():
    news = Post.query.filter(Post.category.has(Category.name == 'Announcements')).order_by(desc(Post.date)).limit(5).all()
    other = Post.query.filter(not_(Post.category.has(Category.name == 'Announcements'))).order_by(desc(Post.date)).limit(5).all()
    return render_template('index.html', news=news, other=other)

@app.route('/portfolio/')
def portfolio():
    return render_template('portfolio.html')

@app.route('/techskills/')
def techskills():
    return render_template('techskills.html')

@app.route('/blog/', defaults={'path': ''})
@app.route('/blog/<path:path>')
def blog(path):
    parts = path.rstrip('/').split('/')
    if len(parts) == 1:
        parts = []

    if len(parts) % 2 != 0:
        return redirect(url_for('blog'))
    
    elif len(parts) == 2 and parts[0] == 'post':
        p = Post.query.filter(Post.slug == parts[1]).first()
        return render_template('singlepost.html', entry=p)

    else:
        query = Post.query
        for i in range(0, len(parts), 2):
            field, val = parts[i], parts[i+1]
            if field == 'category':
                query = query.filter(Post.category.has(Category.name \
                        == unurlize(val)))
            elif field == 'keyword':
                query = query.filter(Post.keywords.contains(unurlize(val)))
            elif field == 'postid':
                query = query.filter(Post.id == val)

        num_pages = ceil(Post.query.count() / 4)

        if 'page' in request.args:
            cur_page = int(request.args['page'])
        else:
            cur_page = 1


        query = query.order_by(desc(Post.date))

        query = query.offset(3 * (cur_page-1)).limit(3)

        entries = query.all()

        return render_template('blog.html', entries=entries, 
                cur_page=cur_page, num_pages=num_pages)

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if not session.get('logged_in'):
        return redirect(url_for('login'), return_to='add_post')
    else:
        if request.method == 'POST':
            post = Post()
            post.title = request.form['title']
            post.body = request.form['body']
            post.category_id = request.form['category_id']
            for keyword in request.form['keywords'].split(','):
                post.keywords.append(keyword.strip())

            db.session.add(post)
            db.session.commit()
            flash('New entry was successfully posted!')
            return redirect(url_for('blog'))

        elif request.method == 'GET':
            categories = Category.query.order_by(Category.name).all()
            return render_template('add_post.html', categories = categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if 'username' not in request.form:
            flash("Please enter a username.")
            return redirect(url_for('login'))
        elif 'password' not in request.form:
            flash("Please enter a password.")
            return redirect(url_for('login'))
        else:
            gooduser = (request.form['username'] == app.config['USERNAME'])
            goodpass = (request.form['password'] == app.config['PASSWORD'])
            if gooduser and goodpass:
                session['logged_in'] = True
                flash("You have successfully logged in.")
                if 'return_to' in request.form:
                    url = url_for(request.form['return_to'])
                else:
                    url = url_for('index')
                return redirect(url)
            else:
                flash("Invalid credentials.")
                return redirect(url_for('login'))
                

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out')
    return redirect(url_for('index'))
