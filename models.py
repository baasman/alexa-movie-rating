from flask_sqlalchemy import SQLAlchemy

from config import app_config
from create_app import create_app

import datetime
import os


db = SQLAlchemy()


class RequestLog(db.Model):

    __tablename__ = 'request_log'

    id = db.Column(db.Integer, primary_key=True)
    intent_type = db.Column(db.String)
    parameters = db.Column(db.String)
    datetime = db.Column(db.DateTime,
            default=datetime.datetime.utcnow)
    user_id = db.Column(db.String)

    def __repr__(self):
        return '<Request({}, {}, {}, {}>'.format(self.intent_type,
                self.parameters, self.datetime, self.user_id)


def setup_db(app, db):
    with app.app_context():
        db.reflect()
        db.drop_all()
        db.create_all()

    
if __name__ == '__main__':
    config_type = os.environ.get('FLASK_CONFIG', 'development')
    app = create_app(app_config[config_type], db)
    setup_db(app, db)

    # insert example
    # log = RequestLog(intent_type='movies', parameters='movie=Titanic',
            # user_id='test ID')
    # with app.app_context():
        # db.session.add(log)
        # db.session.commit()


    # import pdb; pdb.set_trace()
