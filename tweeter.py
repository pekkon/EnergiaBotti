import os
import tweepy
import requests, urllib.parse


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

    watermark_full_logo = "https://i.imgur.com/AkhVDAM.png"
    watermark_profile = "https://i.imgur.com/Kd4P3y2.png"

    url_watermark = f"https://quickchart.io/watermark?mainImageUrl={urllib.parse.quote_plus(url)}" \
                    f"&markImageUrl={urllib.parse.quote_plus(watermark_profile)}" \
                    f"&markRatio=0.07&position=topRight&opacity=1&margin=0"
    print("URL for ", message[:10])
    print(url_watermark)
    request = requests.get(url_watermark, stream=True)

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
