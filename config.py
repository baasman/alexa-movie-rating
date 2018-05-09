class Config(object):
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True

app_config = {
    'development': DevelopmentConfig,
}
