from models import RequestLog, db

from flask import current_app as capp


def convert_decimal_to_percent(string_decimal):
    string_decimal = string_decimal.replace('/10', '').replace('.', '')
    string_decimal = '{}%'.format(string_decimal)
    return string_decimal


def convert_metanumber_to_percent(string_decimal):
    string_decimal = string_decimal.replace('/100', '')
    string_decimal = '{}%'.format(string_decimal)
    return string_decimal


def log_intent(intent_type, parameters, user):
    log = RequestLog(intent_type=intent_type, parameters=parameters,
            user_id=user)
    try:
        db.session.add(log)
        db.session.commit()
    except:
        capp.logger.exception("Unable to commit transaction to db")
