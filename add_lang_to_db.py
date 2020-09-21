#!flask/bin/python

from app import db
from app.models import Post
from langdetect import detect

def main():
    for post in Post.query.all():
        language = detect(post.body)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post.language=language
        db.session.add(post)
        db.session.commit()

if __name__ == '__main__' : main()
