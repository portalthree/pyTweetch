import tweepy
import requests
from twitchAPI import Twitch
import ujson as json
from time import sleep
import datetime as dt
import pymongo

CONSUMER_KEY = "CONSUMER_KEY"
CONSUMER_SECRET = "CONSUMER_SECRET"
ACCESS_TOKEN = "ACCESS_TOKEN"
ACCESS_TOKEN_SECRET = "ACCESS_TOKEN_SECRET" 

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
    content_json = json.loads(json_file.read().encode('raw_unicode_escape').decode())

data = {}
data['streamers'] = {}
    
def checkUser(user):
    userid = twitch.get_users(logins=[user])['data'][0]['id']
    url = TWITCH_STREAM_API_ENDPOINT_V5.format(userid)
    try:
        req = requests.Session().get(url, headers=API_HEADERS)
        jsondata = req.json()
        if('stream' in jsondata):
            if(jsondata['stream'] is not None):
                CURRENT_TIMESTAMP = dt.datetime.utcnow().isoformat(timespec='seconds') + 'Z'

                data['streamers'][twitch_name] = {}
                data['streamers'][twitch_name]['created_at'] = jsondata['stream']['created_at']
                data['streamers'][twitch_name]['last_updated'] = CURRENT_TIMESTAMP
                data['streamers'][twitch_name]['title'] = jsondata['stream']['channel']['status']
                data['streamers'][twitch_name]['viewcount'] = jsondata['stream']['viewers']
                data['streamers'][twitch_name]['game'] = jsondata['stream']['game']
                data['streamers'][twitch_name]['followers'] = jsondata['stream']['channel']['followers']
                data['streamers'][twitch_name]['streamid'] = jsondata['stream']['_id']
                data['streamers'][twitch_name]['channelid'] = jsondata['stream']['channel']['_id']
                data['streamers'][twitch_name]['name'] = jsondata['stream']['channel']['display_name']
                #TODO: UPTIME 

                with open('created_at.json', 'w') as f:
                    json.dump(data, f, indent=4)

                with open('created_at.json', 'r') as created_at:
                    created_at_content = json.loads(created_at.read().encode('raw_unicode_escape').decode())

                    CREATED_AT_TIMESTAMP = created_at_content['streamers'][twitch_name]['created_at']

                    T1 = dt.datetime.strptime(CREATED_AT_TIMESTAMP, "%Y-%m-%dT%H:%M:%SZ")
                    T2 = dt.datetime.strptime(CURRENT_TIMESTAMP, "%Y-%m-%dT%H:%M:%SZ")

                    difference = T2-T1

                    if(difference.seconds >= 300):
                        print(twitch_name + "'s difference is greater than 300 seconds, already tweeted.")
                    else:
                        with open('created_at.json', encoding='utf-8', errors='ignore') as created_at:
                            created_at_content = json.loads(created_at.read().encode('raw_unicode_escape').decode())

                            api.update_status(status = jsondata['stream']['channel']['display_name'] + " went live!"
                            + "\nStreaming: " + jsondata['stream']['channel']['status']
                            + "\nhttps://twitch.tv/" + twitch_name + "\n")
                                
                            with open('created_at.json', encoding='utf-8', errors='ignore') as f:
                                data['streamers'][twitch_name]['title'] = jsondata['stream']['channel']['status']
                                json.dump(data, f, indent=4)

                            print(difference)
                            print(jsondata['stream']['channel']['status'])

                    return jsondata['stream']['channel']['display_name'] + " is live! " + jsondata['stream']['created_at']
            else:
                return twitch_name + " is not live."
    except Exception as e:
        print("Error checking user: ", e)
        return False
    
while True:
    try:
        for twitch_name in content_json["twitch_name"]:
            print(checkUser(twitch_name))
    except Exception as e:
        print("Error checking user: ", e)
        print("Waiting 60s and restarting the bot.")
        sleep(60)
    
    print("Finsished a checkUser cycle, will wait 3 seconds until a new cycle will start.\n")
    sleep(3)
