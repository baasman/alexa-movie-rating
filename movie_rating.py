from flask import Flask, render_template
from flask import current_app as capp
from flask_ask import Ask, statement, question 
from omdb import OMDBClient

from config import app_config

import string

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(app_config['development'])
app.config.from_pyfile('config.py')

ask = Ask(app, "/")


@ask.launch
def startup():
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
    client = OMDBClient(apikey=capp.config['API_KEY'])
    app.logger.info('rating asked for {} from {}'.format(title, site))
    site = site.translate({ord(c): None for c in string.punctuation}).lower()
    req = {}
    if title is not None:
        req['t'] = title
    if year is not None:
        req['y'] = year
    if len(req) == 0:
        app.logger.error('no parameters found')
        return question('Sorry, can you repeat your question, I did not',
                        'understand')
    req['type'] = 'movie'
    res = client.request(**req).json()
    app.logger.info(res)
    response = {}
    for rating in res['Ratings']:
        if 'Internet' in rating['Source']:
            response['imdb'] = rating['Value']
        if 'Rotten' in rating['Source']:
            response['rotten tomatoes'] = rating['Value']
        if 'Meta' in rating['Source']:
            response['metacritic'] = rating['Value']
    app.logger.info(response)
    return statement(render_template('movie_rating_statement', title=res['Title'],
                                     score=response[site], site=site))

@ask.intent('SeriesRatingIntent', convert={'tv_title': str, 'year': str},
            default={'year': None, 'tv_title': None})
def get_series_rating(tv_title, year):
    app.logger.info(tv_title, year)
    client = OMDBClient(apikey=capp.config['API_KEY'])
    app.logger.info('rating asked for {}'.format(tv_title))
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
            response['imdb'] = rating['Value']
        else:
            return statement(render_template('unable to find rating'))
    app.logger.info(response)
    return statement(render_template('series_rating_statement', title=res['Title'],
                                     score=response['imdb']))

@ask.intent('ActorIntent', convert={'title': str},
            default={'title': None})
def get_actors(title):
    client = OMDBClient(apikey=capp.config['API_KEY'])
    app.logger.info('rating asked for {} from {}'.format(title, site))
    req = {}
    if title is not None:
        req['t'] = title
    if len(req) == 0:
        app.logger.error('no parameters found')
        return question('Sorry, can you repeat your question, I did not',
                        'understand')
    res = client.request(**req).json()
    app.logger.info(res)
    response['actors'] = res['Actors']
    app.logger.info(response)
    return statement(render_template('actor_statement', title=res['Title'],
                                     actors=response['actors']))


@ask.intent('BoxIntent', convert={'title': str},
            default={'title': None})
def get_box_office(title):
    client = OMDBClient(apikey=capp.config['API_KEY'])
    app.logger.info('box office asked for {} from {}'.format(title, site))
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
    return statement(render_template('box_office', title=res['Title'],
                                     box_office=response['box_office']))
if __name__ == '__main__':
    app.run(port=5000)

