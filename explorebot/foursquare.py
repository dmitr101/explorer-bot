import json
import requests
import os
from dataclasses import dataclass
from explorebot.explorerequest import ExploreRequest

CLIENT_ID = os.environ.get('FS_CLIENT_ID', None)
CLIENT_SECRET = os.environ.get('FS_CLIENT_SECRET', None)

@dataclass
class Place:
    name: str
    address: str
    latitude: float
    longitude: float


class Response:
    def __init__(self, response_text):
        self.places = []
        self.error = None

        response_object = json.loads(response_text)
        if(response_object['meta']['code'] != 200):
            self.error = "Foursquare API error."
            return
        body = response_object['response']
        groups = body['groups']
        try:
            recommended = next(g for g in groups if g['name'] == 'recommended')
            if len(recommended['items']) == 0:
                raise StopIteration

            for item in recommended['items']:
                venue = item['venue']
                loc = venue['location']
                self.places.append(Place(
                    name=venue['name'], address=loc['address'], latitude=loc['lat'], longitude=loc['lng']))
        except StopIteration:
            self.error = "No recommended places around."


def make_request(explore_request: ExploreRequest) -> Response:
    url = 'https://api.foursquare.com/v2/venues/explore'
    params = dict(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        v='20180323',
        ll=f'{explore_request.location.latitude},{explore_request.location.longitude}',
        radius=explore_request.radius,
        query=explore_request.query,
        limit=3
    )
    response = requests.get(url=url, params=params)
    return Response(response.text)