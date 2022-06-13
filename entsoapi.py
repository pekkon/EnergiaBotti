import pandas as pd
from entsoe import EntsoePandasClient
import os


def get_price_data(start_ts, end_ts):
    token = os.environ['ENTSO_TOKEN']

    client = EntsoePandasClient(api_key=token)
    start = pd.Timestamp(start_ts, tz='Europe/Helsinki')
    end = pd.Timestamp(end_ts, tz='Europe/Helsinki')
    country_code = 'FI'
    # methods that return Pandas Series
    df = client.query_day_ahead_prices(country_code, start=start, end=end)
    df.index = df.index.strftime("%d.%m.%Y %H:%M")
    return df.index.values.tolist(), df.values.tolist()
