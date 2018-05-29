#coding:utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hello haa'
    SQLALCHEMY_COMMIT_ON_TEARDOW = True
    FLASKY_MAIL_SUBJECT_PREFIX= u'[无言]'
    FLASKY_MAIL_SENDER = 'littleflasky@126.com'
    FLASKY_ADMIN = 'littleflasky@126.com'
    MAIL_SERVER = 'smtp.126.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'littleflasky@126.com'
    MAIL_PASSWORD = 'miky123'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    text_factory = str   #数据库中文数据
    UPLOADED_AVATAR_DEST = r'F:/CODE/website1/app/static/avatar/'
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024
    FLASKY_POSTS_PER_PAGE = 13
    FLASKY_FOLLOWERS_PER_PAGE = 20


    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
