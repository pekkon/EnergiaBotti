from general import *
from fingidapi import get_data_from_FG_API
from tweeter import create_tweet, tweet_image
from aws import get_records, update_records
from demand import get_demand
from entsoapi import get_price_data
import os, csv


# Triggered hourly to check new wind power records and posts daily/monthly tweets
def wind_tweets(debugging_mode = True):

    windprodvalues, times = get_wind_production(24)
    capacityvalues, capatimes = get_wind_capacity(24)

    maxwind_prev24 = max(windprodvalues)
    minwind_prev24 = min(windprodvalues)
    sumwind = sum(windprodvalues)

    windprod_prevhour = windprodvalues[-1]
    prevhour = get_time_string(times[-1])
    time_datetime = datetime.strptime(prevhour[:-6], "%d.%m.%Y %H:%M")

    record_timestamp, record = get_records(debug=debugging_mode)
    if record == None:
        print('Could not get wind prod records for', prevhour)
        return
    # For debugging
    lasthour = f'Wind prod during hour {prevhour} was {windprod_prevhour} MWh. Record is {record} MWh during hour {record_timestamp}.'
    print(lasthour)
    # Nuclear production testing
    nuclearprodvalues, nuctimes = get_data_from_FG_API(188, 2)
    maxcapacity = max(capacityvalues)
    # Rounding for upper hundredth
    #maxcapacity -= maxcapacity % -100
    url = create_wind_image_url(times, windprodvalues, maxcapacity)
    print(url)
    tweet_image(url, "asd")
    # Price & Wind test
    #labels, prices = get_price_data(*get_times(24))
    #url = create_price_wind_image_url(labels, windprodvalues, prices)
    #print(url)
    if int(windprod_prevhour) >= int(record):
        text = f"Uusi yhden tunnin tuulivoimatuotantoennätys! {windprod_prevhour} MWh tunnilla {prevhour}. " \
               f"Edellinen ennätys oli {record} MWh tunnilla {record_timestamp}. #tuulivoima"
        print(text)
        update_records(prevhour, windprod_prevhour, debug=debugging_mode)
        create_tweet(text, debug=debugging_mode)

    # Check if previous hour was the last one and create daily tweet
    if prevhour[-5:-3] == "23":
        day = prevhour[0:10]
        avgwind = sum(windprodvalues) / len(windprodvalues)
        # Wind capacity


        sumcapacity = sum(capacityvalues)
        maxcapacity = max(capacityvalues)
        # Rounding for upper hundredth
        maxcapacity -= maxcapacity % -200

        # Demand
        demandvalues, times = get_demand(24)
        sumdemand = sum(demandvalues)

        text = f'Tuulivoiman yhden tunnin tuotanto oli {day} keskimäärin {int(round(avgwind, 0))} MWh. Päivän suurin ' \
               f'yhden tunnin tuotanto oli {maxwind_prev24} MWh ja pienin {minwind_prev24} MWh.\nTuotanto kattoi ' \
               f'{round(sumwind/sumdemand*100, 1)} % kulutuksesta ja sen käyttöaste oli {round(sumwind/sumcapacity*100, 1)} %'
        print(text)
        url = create_wind_image_url(times, windprodvalues, maxcapacity)
        print(url)
        if url != None:
            tweet_image(url, text, debug=debugging_mode)
        else:
            create_tweet(text, debug=debugging_mode)
        forecast(record_timestamp, record, 24, debug=debugging_mode)

    # Check if it's the end of month and create monthly tweet
    if end_of_month(time_datetime):
        month = time_datetime.strftime('%B')
        numdays = time_datetime.day
        numhours = 24 * int(numdays)
        monthly_wind_tweet(numhours, month, debug=debugging_mode)


"""
Monthly wind power tweet
TODO: Currently not working, need to change image generator or reduce amount of data points (480 max)
"""


def monthly_wind_tweet(numhours, month, debug=True):
    windprodvalues, times = get_wind_production(numhours)
    i = argmax(windprodvalues)
    localtime = get_time_string(times[i])
    localtime = datetime.strptime(localtime[:10], "%d.%m.%Y")
    maxwind = max(windprodvalues)
    minwind = min(windprodvalues)
    sumwind = sum(windprodvalues)
    avgwind = sum(windprodvalues) / len(windprodvalues)

    # Wind capacity
    capacityvalues, capatimes = get_wind_capacity(24)
    sumcapacity = sum(capacityvalues)

    # Demand
    demandvalues, times = get_demand(numhours)
    sumdemand = sum(demandvalues)

    text = f'Tuulivoiman yhden tunnin tuotanto oli {month}ssa {localtime.year} keskimäärin {int(round(avgwind, 0))} MWh.' \
           f' Kuukauden suurin yhden tunnin tuotanto oli {maxwind} MWh ja pienin {minwind} MWh.\nTuotanto kattoi ' \
           f'{round(sumwind/sumdemand*100, 1)} % kulutuksesta ja sen käyttöaste oli {round(sumwind/sumcapacity*100, 1)} %'
    print(text)
    url = create_wind_image_url(times[::4], windprodvalues[::4])
    print(url)
    if url != None:
        tweet_image(url, text, debug=debug)
    else:
        create_tweet(text, debug=debug)


"""
Weekly wind power tweet
"""


def get_weekly_wind_production():
    start_time, end_time = get_times(24*7)

    headers = {'x-api-key': os.environ['FGAPIKEY']}
    params = {'start_time': start_time, 'end_time': end_time}

    r = requests.get(f'http://api.fingrid.fi/v1/variable/75/events/csv', params=params, headers=headers, verify=False)
    content = r.content.decode('utf-8')


    cr = csv.reader(content.splitlines(), delimiter=",")
    mylist = list(cr)
    values = []
    times = []
    for row in mylist[1:]:
        values.append(int(row[2]))
        times.append(row[0])

    return values, times


"""
Reads Fingrid's wind power forecast for possible future records
"""


def forecast(record_timestamp, record, hours, debug=True):
    windprodvalues, times = get_forecast(hours)
    i = argmax(windprodvalues)
    localtime_max = get_time_string(times[i])
    maxwind = max(windprodvalues)

    if round(maxwind, 0) > record:
        text = f"Tänään tuulee! Fingridin tuulivoimatuotantoennusteen mukaan tuotantoa voi olla jopa {int(round(maxwind, 0))} MWh tunnilla {localtime_max}! Tällä hetkellä yhden tunnin tuulituotantoennätys on {record} MWh tunnilla {record_timestamp}. #tuulivoima"
        print(text)
        create_tweet(text, debug=debug)


"""
Helper functions for Fingrid's API
"""


def get_forecast(hours):
    return get_data_from_FG_API(245, hours)


def get_wind_production(hours=24):
    return get_data_from_FG_API(75, hours)


def get_wind_capacity(hours):
    return get_data_from_FG_API(268, hours)
