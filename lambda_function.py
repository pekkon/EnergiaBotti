from demand import demand_tweets
from windprod import wind_tweets
from general import *

import locale

locale.setlocale(locale.LC_ALL, 'fi_FI')


def lambda_handler(event, context):
    wind_tweets()
    #demand_tweets()

    return {
        'statusCode': 200,
        'body': json.dumps("Hi")
    }


lambda_handler(None, None)