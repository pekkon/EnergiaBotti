from src.windprod import wind_tweets
from src.demand import demand_tweets
from src.day_ahead import daily_price_graph
import json
import locale

locale.setlocale(locale.LC_ALL, 'fi_FI')


def lambda_handler(event, context):
    print("hello")
    # Set to false if ran on AWS
    debugging_mode = True
    #wind_tweets(debugging_mode)
    #demand_tweets(debugging_mode)
    #daily_price_graph(debugging_mode)


    return {
        'statusCode': 200,
        'body': json.dumps("Hi")
    }


#lambda_handler(None, None)

import pandas as pd
from entsoe import EntsoePandasClient
import os

token = os.environ['ENTSO_TOKEN']

client = EntsoePandasClient(api_key=token)
prices = []
areas = ['FI', 'SE_1', 'SE_3', 'NO_2', 'EE', 'DE_LU']

for area in areas:
    serie = client.query_day_ahead_prices(area, start=pd.Timestamp("2021-01-01 00:00", tz='Europe/Helsinki'),
                                          end=pd.Timestamp("2022-12-14 23:59", tz='Europe/Helsinki'))
    serie.index = serie.index.strftime("%d.%m.%Y %H:%M")
    prices.append(serie.reset_index(drop=True))
areas = ['FI', 'SE1', 'SE3', 'NO2', 'EE', 'DE']
df = pd.DataFrame(prices, columns=areas, index=serie.index)
df.to_excel('price_data.xlsx')
