import re
from unicodedata import normalize
import datetime
from flask import url_for
from sqlalchemy.ext.associationproxy import association_proxy
from homepage import app, db

post_keywords = db.Table('post_keywords', 
        db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id')),
        db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

def find_or_create_kw(kw):
    keyword = Keyword.query.filter(Keyword.name==kw).first()
    if not keyword:
        keyword = Keyword(name=kw)
    return keyword

def slugify(text, delim='-'):
    _punct_re = re.compile(r'[\t :!"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
    result = []
    text = text.replace('\'','')
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word)
        if word:
            result.append(word)
    return delim.join(result)

def context_slugify(context):
    text = context.current_parameters['date'].strftime('%Y-%m-%d')
    text += '-' + slugify(context.current_parameters['title'])
    return text

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    slug = db.Column(db.String(80), default=context_slugify)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
            backref=db.backref('posts', lazy='dynamic'))

    kw = db.relationship('Keyword', secondary=post_keywords,
            cascade="all,delete", backref = db.backref('posts', lazy='dynamic'))

    keywords = association_proxy('kw', 'name',
            creator = find_or_create_kw)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))

class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
