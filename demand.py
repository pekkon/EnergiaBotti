from datetime import datetime
from tweeter import create_tweet
from aws import update_records, get_records
from fingridapi import get_data_from_FG_API
from general import get_time_string


def demand_tweets(debugging_mode=True):

    demandvalues, times = get_demand(3)
    demand_prevhour = demandvalues[-1]
    prevhour = get_time_string(times[-1])

    time_datetime = datetime.strptime(prevhour[:-6], "%d.%m.%Y %H:%M")
    currentyear = time_datetime.year

    record_timestamp, record = get_records(taulu='kulutus', avain=str(currentyear), debug=debugging_mode)
    if record == None:
        print('Could not get records for', prevhour)
        return
    lasthour = f'Demand during hour {prevhour} was {demand_prevhour} MWh. Record in {currentyear} is ' \
               f'{record} MWh during hour {record_timestamp}.'
    print(lasthour)

    if int(demand_prevhour) >= int(record):
        alltime_timestamp, alltime = get_records(taulu='kulutus', avain='record', debug=debugging_mode)

        if int(demand_prevhour) >= int(alltime):
            text = f"Uusi kaikkien aikojen kulutusennätys! {demand_prevhour} MWh tunnilla {prevhour}. " \
                   f"Edellinen ennätys oli {alltime} MWh tunnilla {alltime_timestamp}. #energia"
            update_records(prevhour, demand_prevhour, taulu='kulutus', avain='record', debug=debugging_mode)
        else:
            text = f"Uusi kuluvan vuoden kulutusennätys! {demand_prevhour} MWh tunnilla {prevhour}. " \
                   f"Edellinen ennätys oli {record} MWh tunnilla {record_timestamp}. #energia"
            update_records(prevhour, demand_prevhour, taulu='kulutus', avain=str(currentyear), debug=debugging_mode)

        print(text)
        create_tweet(text, debugging_mode)


def get_demand(hours):
    return get_data_from_FG_API(124, hours)
