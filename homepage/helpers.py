from flask import url_for, Markup
from homepage import app

def urlize(text):
    return text.lower().replace(' ','_')

def unurlize(text):
    return text.replace('_', ' ').title()

@app.context_processor
def utility_processor():
    def kwlist(post):
        basestr = '<a href="' + url_for('blog') + 'keyword/{}">{}</a>'
        kwlist = [basestr.format(urlize(kw), kw) for kw in post.keywords]
        return Markup(', '.join(kwlist))
    return dict(kwlist=kwlist)

