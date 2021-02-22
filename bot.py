""" An example of a Twitter Bot

It gets predictions from Football Prediction API and tweets
the prediction about a random soccer match on a Twitter account.

"""

from datetime import datetime, timezone
import time
import os
import random
import traceback
import requests
import pytz
import tweepy
import emoji

INTERVAL = 60 * 60 * 1  # tweet every 1 hour


api_tz = pytz.timezone("Europe/London")

local_tz = pytz.timezone("America/Asuncion")


def get_current_datetime_on_api_server():
    """Get the current datetime on the api server.

    :return: datetime on the api server.
    :rtype: datetime.datetime
    """

    api_time = datetime.now(tz=timezone.utc).astimezone(api_tz)
    return api_time


def to_local_datetime(start_date):
    """Get the current local datetime.

    :param start_date: a datetime to convert to local timezone.
    :return: Local datetime
    :rtype: datetime.datetime
    """

    date_t = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
    return api_tz.localize(date_t).astimezone(local_tz)


def get_prediction():
    """Get a random prediction from the API.

    :return: A dictionary with the prediction data
    :rtype: dict
    """

    prediction_data = None

    # setting our API key for auth
    headers = {
        'User-Agent': 'python_requests',
        "X-RapidAPI-Key": os.environ["RAPIDAPI_KEY"]
    }

    # setting our query params
    params = {
        "federation": "CONMEBOL",
        "market": "classic"
    }

    try:
        url = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions"
        response = requests.request("GET", url, headers=headers, params=params)

        if response.ok:
            data = response.json().get('data')

            # Filter expired events
            active_events = [event for event in data if not event.get('is_expired')]

            # Select event
            selected = random.choice(active_events)

            # Get event details
            p_id = selected.get('id')
            d_url = f"https://football-prediction-api.p.rapidapi.com/api/v2/predictions/{p_id}"
            response_detail = requests.request("GET", d_url, headers=headers)

            if response_detail.ok:
                prediction_data = response_detail.json().get('data').pop()

    except requests.exceptions.RequestException as request_error:
        traceback.print_exc()
        print(request_error)

    return prediction_data


def configure_twitter_access():
    """Configure Twitter access and authentication

    :return: Twitter API wrapper
    :rtype: tweepy.api
    """

    consumer_key = os.getenv("TW_CONSUMER_KEY")
    consumer_secret = os.getenv("TW_CONSUMER_SECRET")
    access_token = os.getenv("TW_ACCESS_TOKEN")
    access_token_secret = os.getenv("TW_ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    tw_api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    return tw_api


def format_tweet(data):
    """Format the text to publish on Twitter.

    :param data: A dictionary with the prediction data.
    :return: Formated text to tweet
    :rtype: string
    """

    competition = data.get('competition_cluster')
    competition_name = data.get('competition_name')
    home_team = data.get('home_team')
    away_team = data.get('away_team')
    draw = 'Empate'

    prediction = data.get('prediction_per_market').get('classic').get('prediction')

    possibilities = {
        '1': f'{home_team}',
        '1X': f'{home_team} o {draw}',
        'X': f'{draw}',
        '2': f'{away_team}',
        'X2': f'{away_team} o {draw}',
        '12': f'{home_team} o {away_team}'
    }

    p_emoji = ':point_right:'
    if len(prediction) > 1:
        p_emoji = ':person_shrugging:'


    ptext = possibilities.get(prediction)

    tweet = f"""
        {competition} {competition_name}: 
        :stadium: {home_team} - {away_team}
        {p_emoji} Pronóstico: {ptext}

    """

    return emoji.emojize(tweet, use_aliases=True)


def publish_tweet(tw_api):
    """Publish text on Twitter Bot Account

    :param tw_api: the Twitter API wrapper to publish the tweet.
    """

    raw_prediction = get_prediction()

    if raw_prediction:
        text = format_tweet(raw_prediction)
        try:
            tw_api.update_status(text)
        except tweepy.TweepError as tweepy_error:
            traceback.print_exc()
            print(tweepy_error)


if __name__ == "__main__":
    api = configure_twitter_access()
    while True:
        publish_tweet(api)
        time.sleep(INTERVAL)
