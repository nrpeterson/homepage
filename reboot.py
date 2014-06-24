import datetime as dt
from homepage import db
from homepage.database import Post, Category
import pymysql as mysql
from markdown import markdown

print("Dropping.")
db.drop_all()
print("Creating.")
db.create_all()

cat = Category()
cat.name = "Announcements"
cat.id = 1
db.session.add(cat)
db.session.commit()

print("Adding announcements category.")
print("Processing posts:")
with open('news.sql', 'r') as f:
    for line in f:
        l = line.split('|')
        print(l)
        for i in range(len(l)):
            l[i] = l[i].replace('\\r','\r')
            l[i] = l[i].replace('\\n', '\n')
            l[i] = l[i].strip()
        p = Post()
        p.id = int(l[0])
        p.date = dt.datetime.strptime(l[1], '%Y-%m-%d')
        p.title = l[2]
        p.body = l[3]
        p.category_id = int(l[4])
        db.session.add(p)
        print("Finished post with id " + str(p.id))

db.session.commit()

for p in Post.query.filter(Post.title.like("%Code Jam%")).all():
    p.keywords.append('Google Code Jam')

db.session.commit()

