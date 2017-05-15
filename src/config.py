import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(Config):
    DEBUG = False
    MESSENGER_PLATFORM_ACCESS_TOKEN='EAAbF2xEjWqEBAD2okDg6dzPKpePNpNwOMDsDrNcuAOT1GNiOGuqlZAsE5CjgODF8n6UlFbdUtXvJD1aUH84oqCQnNgdE35SL36NvSU5TCnfO4J4CcAXX9X7hZA0znjVfFSeZCJU1RdLUv3ZA3tZBOgEcClGJD2MOb9hDvYUZAkYgZDZD' #GroupThere

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    MESSENGER_PLATFORM_ACCESS_TOKEN='EAAbL0Ffr9PkBADy64t821NSnuMRQx8U1Tm0FAXgS5840g7bm2ryZAHVo4YP74O5mOuZCERJ5mXxaDi7aaFC8RjHM9B4a1YGaba3do6ZAkxX5ci9ncGIH8KuHx2UJoBzUdAuuCWamNJXSbbxGdxqJoUpPoCyGEBYjTx4RdczFwZDZD' #Zach and Friends


class TestingConfig(Config):
    TESTING = True
