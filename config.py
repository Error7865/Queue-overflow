import os
basedir=os.path.abspath(os.path.dirname(__file__))


class Config():
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER='smtp.googlemail.com'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX='[Flasky]'
    FLASKY_MAIL_SENDER='Flasky Admin <error@gmail.com>'
    FLASKY_ADMIN=os.environ.get('FLASKY_ADMIN') or 'error@gmail.com'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_RECORD_QUERIES=True
    
    FLASKY_POSTS_PER_PAGE=20
    FLASKY_FOLLOWERS_PER_PAGE=20
    FLASKY_COMMENTS_PER_PAGE=10
    FLASKY_API_POST_PER_PAGE=10
    FLASKY_SLOW_DB_QUERY_TIME=0.5

    SSL_REDIRECT=False

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
    'sqlite://'
    WTF_CSRF_ENABLED=False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls,app):
        Config.init_app(app)

        # email error to the administrators 
        import logging
        from logging.handlers import SMTPHandler
        credentials=None
        secure=None
        if getattr(cls, 'MIL_USERNAME', None) is not None:
            credentials=(cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure()

        mail_handler=SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX+' Application Error ',
            credentials=credentials,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
            
class HerokuConfig(ProductionConfig):
    SSL_REDIRECT=True if os.environ.get('DYNO') else False
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr 
        import logging
        from logging import StreamHandler
        file_handler=StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        

class DockerConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to start 
        import logging
        from logging import StreamHandler
        file_handler=StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

class UnixConfig(PendingDeprecationWarning):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog 
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler=SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

config = {
'development': DevelopmentConfig,
'testing': TestingConfig,
'production': ProductionConfig,
'default': DevelopmentConfig,
'docker':   DockerConfig
}