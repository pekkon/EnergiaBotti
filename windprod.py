from general import *
from fingidapi import get_data_from_FG_API
from tweeter import create_tweet, tweet_image
from aws import get_records, update_records
from demand import get_demand
from entsoapi import get_price_data


# Triggered hourly to check new wind power records and posts daily/monthly tweets
def wind_tweets():
    windprodvalues, times = get_wind_capacity(24)
    print(times)
    maxwind_prev24 = max(windprodvalues)
    minwind_prev24 = min(windprodvalues)
    sumwind = sum(windprodvalues)

    windprod_prevhour = windprodvalues[-1]
    prevhour = get_time_string(times[-1])
    time_datetime = datetime.strptime(prevhour[:-6], "%d.%m.%Y %H:%M")

    record_timestamp, record = get_records()
    if record == None:
        print('Could not get wind prod records for', prevhour)
        return
    lasthour = f'Wind prod during hour {prevhour} was {windprod_prevhour} MWh. Record is {record} MWh during hour {record_timestamp}.'
    print(lasthour)

    nuclearprodvalues, nuctimes = get_data_from_FG_API(188, 1)
    url = create_wind_image_url(nuctimes, nuclearprodvalues)
    print(url)


    url = create_wind_image_url(times, windprodvalues)
    print(url)
    labels, prices = get_price_data(*get_times(24))
    #url = create_price_wind_image_url(labels, windprodvalues, prices)
    print(url)

    if int(windprod_prevhour) >= int(record):
        text = f"Uusi yhden tunnin tuulivoimatuotantoennätys! {windprod_prevhour} MWh tunnilla {prevhour}. Edellinen ennätys oli {record} MWh tunnilla {record_timestamp}. #tuulivoima"
        print(text)
        update_records(prevhour, windprod_prevhour)
        create_tweet(text)

    if True:#prevhour[-5:-3] == "23":
        day = prevhour[0:10]
        avgwind = sum(windprodvalues) / len(windprodvalues)
        demandvalues, times = get_demand(24)

        sumdemand = sum(demandvalues)

        text = f'Tuulivoiman yhden tunnin tuotanto oli {day} keskimäärin {int(round(avgwind, 0))} MWh. Päivän suurin yhden tunnin tuotanto oli {maxwind_prev24} MWh ja pienin {minwind_prev24} MWh.\n Tuuli-indeksi oli {round(sumwind / sumdemand * 100, 1)} % 🌬'
        print(text)
        url = create_wind_image_url(times, windprodvalues)
        print(url)
        if url != None:
            tweet_image(url, text)
        else:
            create_tweet(text)
        forecast(record_timestamp, record, 24)
    if True:#end_of_month(time_datetime):
        month = time_datetime.strftime('%B')
        numdays = time_datetime.day
        numhours = 24 * int(numdays)
        monthly_wind_tweet(numhours, month)


def monthly_wind_tweet(numhours, month):


    windprodvalues, times = get_wind_production(numhours)
    i = argmax(windprodvalues)
    localtime = get_time_string(times[i])
    localtime = datetime.strptime(localtime[:10], "%d.%m.%Y")
    maxwind = max(windprodvalues)
    minwind = min(windprodvalues)
    sumwind = sum(windprodvalues)
    avgwind = sum(windprodvalues) / len(windprodvalues)

    # Demand
    demandvalues, times = get_demand(numhours)

    sumdemand = sum(demandvalues)

    text = f'Tuulivoiman yhden tunnin tuotanto oli {month}ssa {localtime.year} keskimäärin {int(round(avgwind, 0))} MWh. Kuukauden suurin yhden tunnin tuotanto oli {maxwind} MWh ja pienin {minwind} MWh.\nTuuli-indeksi oli {round(sumwind / sumdemand * 100, 1)} % 🌬'
    print(text)
    url = create_wind_image_url(times, windprodvalues)
    print(url)
    if url != None:
        tweet_image(url, text)
    else:
        create_tweet(text)

def forecast(record_timestamp, record, hours):
    windprodvalues, times = get_forecast(hours)
    i = argmax(windprodvalues)
    localtime_max = get_time_string(times[i])
    maxwind = max(windprodvalues)

    if round(maxwind, 0) > record:
        text = f"Tänään tuulee! Fingridin tuulivoimatuotantoennusteen mukaan tuotantoa voi olla jopa {int(round(maxwind, 0))} MWh tunnilla {localtime_max}! Tällä hetkellä yhden tunnin tuulituotantoennätys on {record} MWh tunnilla {record_timestamp}. #tuulivoima"
        print(text)
        create_tweet(text)

def get_forecast(hours):
    return get_data_from_FG_API(245, hours)

def get_wind_production(hours=24):
    return get_data_from_FG_API(75, hours)

def get_wind_capacity(hours):
    return get_data_from_FG_API(268, hours)