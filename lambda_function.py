from demand import demand_tweets
from windprod import wind_tweets
from day_ahead import daily_price_graph
from general import *
import locale

locale.setlocale(locale.LC_ALL, 'fi_FI')


def lambda_handler(event, context):
    # Set to false if ran on AWS
    debugging_mode = True
    #wind_tweets(debugging_mode)
    #demand_tweets(debugging_mode)
    daily_price_graph(debugging_mode)

    return {
        'statusCode': 200,
        'body': json.dumps("Hi")
    }


lambda_handler(None, None)
