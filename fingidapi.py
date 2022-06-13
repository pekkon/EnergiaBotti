import csv, os, requests
from general import get_times

"""
Reads csv-file given by Fingrid's open data API and converts it to list of timestamps and values
"""
def get_data_from_FG_API(variableid, hours=24):
    start_time, end_time = get_times(hours)
    print(start_time, end_time)
    headers = {'x-api-key': os.environ['FGAPIKEY']}
    params = {'start_time': start_time, 'end_time': end_time}

    r = requests.get(f'http://api.fingrid.fi/v1/variable/{variableid}/events/csv', params=params, headers=headers, verify=False)
    content = r.content.decode('utf-8')

    cr = csv.reader(content.splitlines(), delimiter=",")
    rows = list(cr)
    values = []
    times = []
    # Skip header row
    for row in rows[1:]:
        values.append(float(row[2]))
        times.append(row[0])

    return values, times
