from entsoapi import get_price_data
from general import get_next_day_timestamps, create_price_image_url, create_price_demand_image_url
from fingridapi import get_data_from_FG_API_with_start_end
from tweeter import create_tweet, tweet_image

def daily_price_graph(debugging_mode=True):
    start, end = get_next_day_timestamps()
    labels, prices = get_price_data(start, end)
    prices = [round(i * 0.1 * 1.24, 2) for i in prices]
    start_str = start.strftime("%Y-%m-%dT%H") + ":00:00+03:00"
    end_str = end.strftime("%Y-%m-%dT%H") + ":59:00+03:00"
    demand, demand_labels = get_demand_forecast(start_str, end_str)
    demand = list(demand_hourly_avg(demand))
    print(demand)
    url = create_price_demand_image_url(labels, prices, demand)
    print(url)
    avg_price = round(sum(prices) / len(prices), 2)
    max_price = round(max(prices), 2)
    min_price = round(min(prices), 2)
    avg_demand = round(sum(demand) / len(demand), 0)
    max_demand = round(max(demand), 0)
    min_demand = round(min(demand), 0)
    text = f"Sähkön spot-hinnat ja kulutusennuste Suomessa {labels[0][:10]}\n" \
           f"Keskihinta: {avg_price} snt/kWh       Keskikulutus: {avg_demand} MWh/h\n" \
           f"Maksimihinta: {max_price} snt/kWh      Maksimikulutus: {max_demand} MWh/h\n" \
           f"Minimihinta: {min_price} snt/kWh      Minimikulutus: {min_demand} MWh/h\n"
    print(text)
    if url != None:
        tweet_image(url, text, debug=debugging_mode)


def get_demand_forecast(start, end):
    return get_data_from_FG_API_with_start_end(165, start, end)


def demand_hourly_avg(data):
    datasum = cnt = 0
    for num in data:
        datasum += num
        cnt += 1
        if cnt == 12:
            yield datasum / 12
            datasum = cnt = 0
    if cnt:
        yield datasum / cnt


# [5.5, 15.5, 25.5]