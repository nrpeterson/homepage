from math import ceil
from flask import render_template, request
from sqlalchemy import desc
from app import app, db
from app.database import Post, Category, Keyword
from app.helpers import urlize, unurlize

@app.route('/')
def index():
    stories = Post.query.order_by(desc(Post.date)).limit(5).all()
    return render_template('index.html', stories=stories)

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
        return render_template('blog.html', posts=[p])

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

        posts = query.all()

        return render_template('blog.html', posts=posts, 
                cur_page=cur_page, num_pages=num_pages)
