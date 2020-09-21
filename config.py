import os

CSRF_ENABLED = True
SECRET_KEY = 'lu95281712'

basedir=os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

POSTS_PER_PAGE = 3

ELASTICSEARCH_URL = 'localhost:9200'

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'channelye.tobe@gmail.com'
MAIL_PASSWORD = 'Cola@95281712'

ADMINS = ['channelye.tobe@gmail.com']

LANGUAGES = {
    'en': 'English',
    'zh': 'Chinese',
    'ja': 'Japanese'}

BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'UTC'

TRANSLATOR_TEXT_ENDPOINT = 'https://api.cognitive.microsofttranslator.com/'
TRANSLATOR_TEXT_SUBSCRIPTION_KEY = '8f9f7fc421b34efbb084a6f017ffa536'
TRANSLATOR_TEXT_SUBSCRIPTION_REGION = 'japaneast'
