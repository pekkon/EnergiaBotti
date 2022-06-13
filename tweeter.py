import os
import tweepy
import requests


def twitter_api():
    auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])

    auth.set_access_token(os.environ['ACCESS_KEY'],
                          os.environ['ACCESS_SECRET'])

    api = tweepy.API(auth)

    try:
        api.verify_credentials()
        print("Auth successful")
    except:
        print("Error during authentication")

    return api


def tweet_image(url, message, debug=True):
    api = twitter_api()
    filename = 'tmp/temp.png'
    request = requests.get(url, stream=True)
    print(url)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)
        if not debug:
            api.update_with_media(filename, status=message)
        os.remove(filename)
        return "Tweeted"
    else:
        print("Unable to download image")
        return None


def create_tweet(text, debug=True):

    api = twitter_api()
    if not debug:
        api.update_status(text)
    return "Tweeted"
