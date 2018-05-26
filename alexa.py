from flask import render_template
from flask import current_app as capp
                                     
from flask_ask import Ask, statement, question, session
from flask_ask import request as ask_request
from omdb import OMDBClient

from config import app_config
from util import convert_decimal_to_percent, log_intent, convert_metanumber_to_percent
from models import db, RequestLog
from create_app import create_app

import string
import os


config_type = os.environ.get('FLASK_CONFIG', 'development')

app = create_app(app_config[config_type], db)

ask = Ask(app, "/")


@ask.launch
def startup():
    user_log = RequestLog.query.filter_by(user_id=session.user.userId).count()
    if user_log >= 1:
        return_msg = render_template('welcome_back')
        return question(return_msg)
    app.logger.info('app accessed')
    welcome_msg = render_template('welcome')
    welcome_msg_help = render_template('welcome_help')
    return question(welcome_msg).reprompt(welcome_msg_help)


@ask.on_session_started
def new_session():
    app.logger.info('new session started')


@ask.session_ended
def session_ended():
    app.logger.info('session ended')
    return "{}", 200


@ask.intent('MovieRatingIntent', convert={'site': str, 'title': str, 'year': str},
            default={'year': None, 'title': None, 'site': 'imdb'})
def get_movie_rating(site, title, year):
    app.logger.info('MovieRatingIntent accessed with arguments site={}, title={} and year={}'.format(site, title, year))
    client = OMDBClient(apikey=capp.config['API_KEY'])
    site = site.translate({ord(c): None for c in string.punctuation}).lower()
    req = {}
    if title is not None:
        req['t'] = title
    if year is not None:
        req['y'] = year
    if len(req) == 0:
        app.logger.error('no parameters found')
        return statement('Sorry, can you repeat your question, I did not',
                        'understand. try again')
    req['type'] = 'movie'
    res = client.request(**req).json()
    app.logger.info(res)
    response = {}
    for rating in res['Ratings']:
        if 'Internet' in rating['Source']:
            response['imdb'] = convert_decimal_to_percent(rating['Value'])
        if 'Rotten' in rating['Source']:
            response['rotten tomatoes'] = rating['Value']
        if 'Meta' in rating['Source']:
            response['metacritic'] = convert_metanumber_to_percent(rating['Value'])
    log_intent('MovieRatingIntent', parameters=None, user=session.user.userId)
    return statement(render_template('movie_rating_statement', title=res['Title'],
                                     score=response[site], site=site))


@ask.intent('SeriesRatingIntent', convert={'tv_title': str, 'year': str},
            default={'year': None, 'tv_title': None})
def get_series_rating(tv_title, year):
    app.logger.info('SeriesRatingIntent accessed with arguments tv_title={} and',
                    'year={}'.format(tv_title, year))
    client = OMDBClient(apikey=capp.config['API_KEY'])
    req = {}
    if tv_title is not None:
        req['t'] = tv_title
    if year is not None:
        req['y'] = year
    if len(req) == 0:
        app.logger.error('no parameters found')
        return question('Sorry, can you repeat your question, I did not',
                        'understand')
    req['type'] = 'series'
    res = client.request(**req).json()
    app.logger.info(res)
    response = {}
    for rating in res['Ratings']:
        if 'Internet' in rating['Source']:
            response['imdb'] = convert_decimal_to_percent(rating['Value'])
        else:
            return statement(render_template('unable to find rating'))
    app.logger.info(response)
    log_intent('SeriesRatingIntent', parameters=None, user=session.user.userId)
    if res['Title'] == 'Twin Peaks':
        return statement(render_template('series_rating_statement_twin_peaks', title=res['Title'],
                                         score=response['imdb']))
    return statement(render_template('series_rating_statement', title=res['Title'],
                                     score=response['imdb']))

@ask.intent('ActorMovieIntent', convert={'title': str},
            default={'title': None})
def get_movie_actors(title):
    client = OMDBClient(apikey=capp.config['API_KEY'])
    app.logger.info('ActorIntent accessed with arguments {}'.format(title))
    req = {}
    if title is not None:
        req['t'] = title
    if len(req) == 0:
        app.logger.error('no parameters found')
        return question('Sorry, can you repeat your question, I did not',
                        'understand')
    res = client.request(**req).json()
    app.logger.info(res)
    response = {}
    response['actors'] = res['Actors']
    app.logger.info(response)
    log_intent('ActorMovieIntent', parameters=None, user=session.user.userId)
    return statement(render_template('actor_movie_statement', title=res['Title'],
                                     actors=response['actors']))


@ask.intent('ActorSeriesIntent', convert={'title': str},
            default={'title': None})
def get_series_actors(title):
    client = OMDBClient(apikey=capp.config['API_KEY'])
    app.logger.info('ActorIntent accessed with arguments {}'.format(title))
    req = {}
    if title is not None:
        req['t'] = title
    if len(req) == 0:
        app.logger.error('no parameters found')
        return question('Sorry, can you repeat your question, I did not',
                        'understand')
    req['type'] = 'series'
    res = client.request(**req).json()
    app.logger.info(res)
    response = {}
    response['actors'] = res['Actors']
    app.logger.info(response)
    log_intent('ActorSeriesIntent', parameters=None, user=session.user.userId)
    return statement(render_template('actor_series_statement', title=res['Title'],
                                     actors=response['actors']))


@ask.intent('BoxIntent', convert={'title': str},
            default={'title': None})
def get_box_office(title):
    client = OMDBClient(apikey=capp.config['API_KEY'])
    app.logger.info('box office asked for {}'.format(title))
    req = {}
    if title is not None:
        req['t'] = title
    if len(req) == 0:
        app.logger.error('no parameters found')
        return question('Sorry, can you repeat your question, I did not',
                        'understand')
    res = client.request(**req).json()
    app.logger.info(res)
    response = {}
    response['box_office'] = res['BoxOffice']
    app.logger.info(response)
    log_intent('BoxIntent', parameters=None, user=session.user.userId)
    if response['box_office'] == 'N/A':
        return statement('I was unable to find the box office for the movie {}'.format(title))
    return statement(render_template('box_office', title=res['Title'],
                                     box_office=response['box_office']))


if __name__ == '__main__':
    app.run(port=5000)

