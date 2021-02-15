import tweepy
import requests
from twitchAPI import Twitch
import json
from time import sleep
import datetime as dt

CONSUMER_KEY = "CONSUMER_KEY"
CONSUMER_SECRET = "CONSUMER_SECRET"
ACCESS_TOKEN = "ACCESS_TOKEN"
ACCESS_TOKEN_SECRET = "ACCESS_TOKEN_SECRET"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m' 
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

TWITCH_APP_ID = "TWITCH_APP_ID"
TWITCH_APP_SECRET = "TWITCH_APP_SECRET"

twitch = Twitch(TWITCH_APP_ID, TWITCH_APP_SECRET)
twitch.authenticate_app([])

TWITCH_STREAM_API_ENDPOINT_V5 = "https://api.twitch.tv/kraken/streams/{}"

API_HEADERS = {
    'Client-ID' : TWITCH_APP_ID,
    'Accept' : 'application/vnd.twitchtv.v5+json',
}

with open("streamers.json", encoding='raw_unicode_escape') as json_file:
    content_json = json.loads(
        json_file.read().encode('raw_unicode_escape').decode())

data = {}
data['streamers'] = {}

def checkUser(user): #returns true if online, false if not
    userid = twitch.get_users(logins=[user])['data'][0]['id']
    url = TWITCH_STREAM_API_ENDPOINT_V5.format(userid)
    try:
        req = requests.Session().get(url, headers=API_HEADERS)
        jsondata = req.json()
        if 'stream' in jsondata:
            if jsondata['stream'] is not None:
                CURRENT_TIMESTAMP = dt.datetime.utcnow().isoformat(timespec='seconds') + 'Z'


                data['streamers'][twitch_name] = {}
                data['streamers'][twitch_name]['created_at'] = jsondata['stream']['created_at']
                data['streamers'][twitch_name]['last_updated'] = CURRENT_TIMESTAMP

                with open('created_at.json', 'w') as f:
                    json.dump(data, f, indent=4)


                with open('created_at.json', 'r') as created_at:
                    created_at_content = json.loads(created_at.read().encode('raw_unicode_escape').decode())

                    CREATED_AT_TIMESTAMP = created_at_content['streamers'][twitch_name]['created_at']


                    T1 = dt.datetime.strptime(CREATED_AT_TIMESTAMP, "%Y-%m-%dT%H:%M:%SZ")
                    T2 = dt.datetime.strptime(CURRENT_TIMESTAMP, "%Y-%m-%dT%H:%M:%SZ")

                    difference = T2-T1

                    if(difference.seconds >= 300):
                        print(bcolors.WARNING + twitch_name + "'s difference was greater than 340 seconds, did not tweet." + bcolors.ENDC)

                        data['streamers'][twitch_name]['tweeted'] = "Yes"

                        with open('created_at.json', 'w') as f:
                            json.dump(data, f, indent=4)
                    else:

                        api.update_status(status = jsondata['stream']['channel']['display_name'] + " went live!"
                        + "\nStreaming: " + jsondata['stream']['channel']['status']
                        + "\nhttps://twitch.tv/" + twitch_name + "\n")
                        
                        data['streamers'][twitch_name]['tweeted'] = "Tweeting"
                        data['streamers'][twitch_name]['title'] = jsondata['stream']['channel']['status']

                        print(difference)
                        print(jsondata['stream']['channel']['status'])

                        with open('created_at.json', 'w') as f:
                            json.dump(data, f, indent=4)

                return bcolors.OKCYAN + jsondata['stream']['channel']['display_name'] + " is live! " + jsondata['stream']['created_at'] + bcolors.ENDC
            else:
                    return bcolors.FAIL + twitch_name + " is not currently live." + bcolors.ENDC

    except Exception as e:
        print("Error checking user: ", e)
        return False

while True:
    for twitch_name in content_json["twitch_name"]:
        print(checkUser(twitch_name))
    print(bcolors.OKGREEN + "\nFinsished a checkUser cycle, will wait 5 seconds until a new cycle will start.\n" + bcolors.ENDC)
    sleep(5)