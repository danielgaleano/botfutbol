from datetime import datetime, timedelta, timezone
import time
import os
import requests
import pprint
import random
import pytz
import tweepy
import traceback

INTERVAL = 60 * 60 * 1  # tweet every 1 hour


api_tz = pytz.timezone("Europe/London")

local_tz = pytz.timezone("America/Asuncion")


def get_current_datetime_on_api_server():
    london_time = datetime.now(tz=timezone.utc).astimezone(api_tz)
    return london_time


def to_local_datetime(start_date):
    dt = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
    return api_tz.localize(dt).astimezone(local_tz)


def get_prediction():
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

    url = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions"
    response = requests.request("GET", url, headers=headers, params=params)

    if response.ok:
        data = response.json().get('data')

        # Filter expired events
        active_events = [event for event in data if not event.get('is_expired')]

        # Select event
        selected = random.choice(active_events)

        # Get event details
        prediction_id = selected.get('id')
        detail_url = f"https://football-prediction-api.p.rapidapi.com/api/v2/predictions/{prediction_id}"
        response_detail = requests.request("GET", detail_url, headers=headers)

        if response_detail.ok:
            prediction_data = response_detail.json().get('data').pop()

    return prediction_data


def configure_twitter_access():
    consumer_key = os.getenv("TW_CONSUMER_KEY")
    consumer_secret = os.getenv("TW_CONSUMER_SECRET")
    access_token = os.getenv("TW_ACCESS_TOKEN")
    access_token_secret = os.getenv("TW_ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
    return api

def format_tweet(data):
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

    ptext = possibilities.get(prediction)

    tweet = f"""
        {competition} {competition_name}: 
        {home_team} - {away_team}
        Pronóstico: {ptext}

    """

    return tweet


def tweet(api):
    raw_prediction = get_prediction()

    if raw_prediction:
        text = format_tweet(raw_prediction)
        api.update_status(text)


if __name__ == "__main__":
    api = configure_twitter_access()
    while True:
        try:
            tweet(api)
        except Exception as e:
            traceback.print_exc()
            print(e)

        time.sleep(INTERVAL)

