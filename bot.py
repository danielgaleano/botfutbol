from datetime import datetime, timedelta, timezone
import time
import os
import requests
import pprint
import random
import pytz
import tweepy

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
    current_server_time = get_current_datetime_on_api_server()

    # setting our API key for auth
    headers = {
        'User-Agent': 'python_requests',
        "X-RapidAPI-Key": os.environ["RAPIDAPI_KEY"]
    }

    # setting our query params
    params = {
        "iso_date": current_server_time.date().isoformat(),
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



