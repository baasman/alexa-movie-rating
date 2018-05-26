from flask import Flask


def create_app(config, db):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    return app
