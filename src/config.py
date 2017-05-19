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
    MESSENGER_PLATFORM_ACCESS_TOKEN=os.environ.get('MESSENGER_PLATFORM_ACCESS_TOKEN') #Zach and Friends


class TestingConfig(Config):
    TESTING = True
