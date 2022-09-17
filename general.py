from datetime import datetime, timedelta
from pytz import timezone
import json, requests
from pandas import Timestamp


# Takes UTC timestamp and converts it into Finnish time
def get_time_string(utctime):
    utctime = datetime.strptime(utctime[:-5], "%Y-%m-%dT%H:%M:%S")
    localtime = datetime_from_utc_to_local(utctime)
    localtime = localtime.strftime("%d.%m.%Y %H") + ":00-" + localtime.strftime("%H:59")
    return localtime


def argmax(iterable):
    return max(enumerate(iterable), key=lambda x: x[1])[0]


def argmin(iterable):
    return min(enumerate(iterable), key=lambda x: x[1])[0]


def datetime_from_utc_to_local(utc_datetime):
    local_timestamp = datetime.now(timezone('Europe/Helsinki')).replace(tzinfo=None)
    utc_timestamp = datetime.now(timezone('utc')).replace(tzinfo=None)
    offset = local_timestamp - utc_timestamp + timedelta(hours=1)

    return utc_datetime + offset


# returns timestamps for current hour and x hours before or after
def get_times(hours=24):
    timenow = datetime.utcnow()
    currhour = timenow.strftime("%Y-%m-%dT%H:00:00Z")

    if hours > 0:
        firsthour = (timenow - timedelta(hours=hours)).strftime("%Y-%m-%dT%H") + ":00:00Z"
        return firsthour, currhour
    else:
        firsthour = (timenow + timedelta(hours=-hours)).strftime("%Y-%m-%dT%H") + ":00:00Z"
        return currhour, firsthour

def get_next_day_timestamps():
    timenow = datetime.utcnow()
    date = (timenow + timedelta(days=1)).strftime("%Y-%m-%d")
    start = Timestamp(date + " 00:00", tz='Europe/Helsinki')
    end = Timestamp(date + " 23:59", tz='Europe/Helsinki')
    return start, end

# Check if date is end of month
def end_of_month(dt):
    todays_month = dt.month
    tomorrows_month = (dt + timedelta(days=1)).month
    return True if tomorrows_month != todays_month else False


def create_price_wind_image_url(labels, winddata, pricedata):
    if min(pricedata) < 0:
        min_price_tick = min(pricedata)
    else:
        min_price_tick = 0
    local = labels
    config = {
        "type": "line",
        "pointStyle": "line",
        "data": {
            "labels": local,
            "datasets": [{
                "label": "Tuulivoimatuotanto",
                "yAxisID": "y1",
                "data": winddata,
                "fill": "false",
                "spanGaps": "false",
                "lineTension": 0.2,
                "pointRadius": 2,
                "borderColor": "#001CE5",
                "pointStyle": "circle",
                "backgroundColor": "#001CE5",
                "borderWidth": 2
            },
                {
                    "label": "Suomen aluehinta",
                    "yAxisID": "y2",
                    "data": pricedata,
                    "borderColor": "#000000",
                    "fill": "false",
                    "pointStyle": "line",
                    "pointRadius": 0
                }
            ]
        },
        "options": {
            "title": {
                "display": "true",
                "text": f"Suomen tuulivoimatuotanto ja aluehinta tunneittain {local[0][:10]} (hinta sis. ALV)"

            },
            "legend": {
                "position": "top",
                "labels": {
                    "pointStyle": "line",
                    "usePointStyle": True,

                },
                "display": True,

            },
            "scales": {
                "xAxes": [{
                    "type": "time",
                    "time": {
                        "parser": "DD.MM.YYYY HH:mm",
                        "isoWeek": "true",

                        "displayFormats": {
                            "day": "DD.MM.",
                            "hour": "HH:mm"
                        }
                    },
                    "ticks": {
                        "source": "auto",
                        "maxRotation": 0,
                        "autoSkipPadding": 5,
                        "major": {
                            "unit": "hour",
                            "displayFormats": {
                                "day": "DD.MM.",
                                "hour": "HH:mm"
                            }
                        }

                    },
                    "scaleLabel": {
                        "display": False,
                        "labelString": "Aika"
                    }
                }],

                "yAxes": [
                    {
                    "id": "y1",
                    "ticks": {
                        "min": 0,
                        "stepSize": 200
                    },
                    "scaleLabel": {
                        "display": "true",
                        "labelString": "MWh"
                        }
                    },
                    {
                    "id": "y2",
                        "ticks": {
                            "min": min_price_tick
                        },
                    "position": "right",
                    "gridLines": {
                        "drawOnChartArea": False
                    },
                    "scaleLabel": {
                        "display": "true",
                        "labelString": "snt/kWh"
                    }
                    }
                ]
            }

        }

    }
    params = {
        'chart': json.dumps(config),
        'width': 500,
        'height': 300,
        'backgroundColor': 'white',
    }

    quickchart_url = 'https://quickchart.io/chart/create'
    post_data = params

    response = requests.post(
        quickchart_url,
        json=post_data,
    )

    if (response.status_code != 200):
        print('Error:', response.text)
        return None
    else:
        chart_response = json.loads(response.text)
        url = chart_response['url']
        return url


def create_wind_image_url(labels, data, maxtick=None):
    if maxtick is None:
        maxtick = max(data)
        # Round to upper hundredth
        maxtick -= maxtick % -100
    local = []
    for label in labels:
        local.append(get_time_string(label)[:-6])
    config = {
        "type": "line",
        "data": {
            "labels": local,
            "datasets": [{
                "fill": "true",
                "label": "Tuulivoimatuotanto",
                "data": data,
                "spanGaps": "false",
                "lineTension": 0.2,
                "pointRadius": 2,
                "borderColor": "#001CE5",
                "pointStyle": "circle",
                "backgroundColor": "#001CE5",
                "borderWidth": 2
            }]
        },
        "options": {
            "title": {
                "display": "true",
                "text": f"Tuulivoimatuotanto tunneittain {local[0][:10]}",
                "position": "top",
                "fontSize": 12,
                "fontColor": "#0E101E",
                "fontStyle": "bold",
                "padding": 10,
                "lineHeight": 1.2
            },
            "legend": {
                "position": "right",
                "display": False

            },
            "scales": {
                "xAxes": [{
                    "type": "time",
                    "time": {
                        "parser": "DD.MM.YYYY HH:mm",
                        "isoWeek": "true",

                        "displayFormats": {
                            "day": "DD.MM.",
                            "hour": "HH:mm"
                        }
                    },
                    "ticks": {
                        "source": "auto",
                        "maxRotation": 0,
                        "autoSkipPadding": 5,
                        "fontColor": "#0E101E",
                        "fontStyle": "bold",
                        "fontSize": 10,
                        "padding": 8,
                        "major": {
                            "unit": "hour",
                            "displayFormats": {
                                "day": "DD.MM.",
                                "hour": "HH:mm"
                            }
                        },
                    },
                    "gridLines": {
                        "display": "true",
                        "color": "rgba(0, 0, 0, 0.05)",
                        "borderDash": [
                            0,
                            0
                        ],
                        "lineWidth": 1,
                        "drawBorder": "true",
                        "drawOnChartArea": "false",
                        "drawTicks": "true",
                        "tickMarkLength": 5,
                        "zeroLineWidth": 1,
                        "zeroLineColor": "rgba(0, 0, 0, 0.25)",
                        "zeroLineBorderDash": [
                            0,
                            0
                        ]
                    },
                    "scaleLabel": {
                        "display": False,
                        "labelString": "Aika"
                    }
                }],

                "yAxes": [
                    {
                    "id": "y1",
                    "ticks": {
                        "beginAtZero": "true",
                        "min": 0,
                        "max": maxtick,
                        "maxTicksLimit": 20,
                        "fontColor": "#0E101E",
                        "fontSize": 10,
                        "fontStyle": "bold",
                        "padding": 8,
                        "stepSize": 400
                    },
                    "gridLines": {
                        "display": "true",
                        "color": "rgba(0, 0, 0, 0.1)",
                        "borderDash": [
                            0,
                            0
                        ],
                        "lineWidth": 1,
                        "drawBorder": "true",
                        "drawOnChartArea": "true",
                        "drawTicks": "true",
                        "tickMarkLength": 5,
                        "zeroLineWidth": 1,
                        "zeroLineColor": "rgba(0, 0, 0, 0.25)",
                        "zeroLineBorderDash": [
                            0,
                            0
                        ]
                    },
                    "scaleLabel": {
                        "display": "true",
                        "labelString": "MWh"
                        }
                    }
                ]
            }
        }

    }
    params = {
        'chart': json.dumps(config),
        'width': 500,
        'height': 300,
        'backgroundColor': 'white',
    }

    quickchart_url = 'https://quickchart.io/chart/create'
    post_data = params

    response = requests.post(
        quickchart_url,
        json=post_data,
    )

    if (response.status_code != 200):
        print('Error:', response.text)
        return None
    else:
        chart_response = json.loads(response.text)
        url = chart_response['url']
        return url

def create_price_demand_image_url(labels, pricedata, demand, maxtick=None):
    if maxtick is None:
        maxtick = max(pricedata)
        # Round to upper tenth
        maxtick -= maxtick % -10
    demand_max_tick = max(demand)
    demand_max_tick -= demand_max_tick % - 200

    config = {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": [{
                "fill": "true",
                "label": "Sähkön hinta",
                "data": pricedata,
                "spanGaps": "false",
                "lineTension": 0.2,
                "pointRadius": 0,
                "borderColor": "#000000",
                "pointStyle": "circle",
                "backgroundColor": "#000000",
                "steppedLine": True,
                "borderWidth": 3,
                "yAxisID": "y1"
            },
            {
                "label": "Suomen kulutusennuste",
                "yAxisID": "y2",
                "data": demand,
                "borderColor": "#001CE5",
                "backgroundColor": "#001CE5",
                "lineTension": 0.2,
                "fill": "false",
                "pointStyle": "circle",
                "borderWidth": 2,
                "pointRadius": 2
            }
            ]
        },
        "options": {
            "title": {
                "display": "true",
                "text": f"Suomen sähkön hinnat ja kulutusennuste tunneittain {labels[0][:10]}",
                "position": "top",
                "fontSize": 12,
                "fontColor": "#000000",
                "fontStyle": "bold",
                "padding": 10,
                "lineHeight": 1.2
            },
            "legend": {
                "position": "top",
                "display": True,
                "fontSize": 8

            },
            "scales": {
                "xAxes": [{
                    "type": "time",
                    "time": {
                        "parser": "DD.MM.YYYY HH:mm",
                        "isoWeek": "true",

                        "displayFormats": {
                            "day": "DD.MM.",
                            "hour": "HH:mm"
                        }
                    },
                    "ticks": {
                        "source": "auto",
                        "maxRotation": 0,
                        "autoSkipPadding": 5,
                        "fontColor": "#0E101E",
                        "fontStyle": "bold",
                        "fontSize": 10,
                        "padding": 8,
                        "major": {
                            "unit": "hour",
                            "displayFormats": {
                                "day": "DD.MM.",
                                "hour": "HH:mm"
                            }
                        },
                    },
                    "gridLines": {
                        "display": "true",
                        "color": "rgba(0, 0, 0, 0.05)",
                        "borderDash": [
                            0,
                            0
                        ],
                        "lineWidth": 1,
                        "drawBorder": "true",
                        "drawOnChartArea": "false",
                        "drawTicks": "true",
                        "tickMarkLength": 5,
                        "zeroLineWidth": 1,
                        "zeroLineColor": "rgba(0, 0, 0, 0.25)",
                        "zeroLineBorderDash": [
                            0,
                            0
                        ]
                    },
                    "scaleLabel": {
                        "display": False,
                        "labelString": "Aika"
                    }
                }],

                "yAxes": [
                    {
                    "id": "y1",
                    "ticks": {
                        "beginAtZero": "true",
                        "min": 0,
                        "max": maxtick,
                        "maxTicksLimit": 20,
                        "fontColor": "#000000",
                        "fontSize": 10,
                        "fontStyle": "bold",
                        "padding": 8,
                        "stepSize": 5
                    },
                    "gridLines": {
                        "display": "true",
                        "color": "rgba(0, 0, 0, 0.1)",
                        "borderDash": [
                            0,
                            0
                        ],
                        "lineWidth": 1,
                        "drawBorder": "true",
                        "drawOnChartArea": "true",
                        "drawTicks": "true",
                        "tickMarkLength": 5,
                        "zeroLineWidth": 1,
                        "zeroLineColor": "rgba(0, 0, 0, 0.25)",
                        "zeroLineBorderDash": [
                            0,
                            0
                        ]
                    },
                    "scaleLabel": {
                        "display": "true",
                        "labelString": "snt/kWh (sis. ALV)"
                        }
                    },
                    {
                        "id": "y2",
                        "position": "right",
                        "gridLines": {
                            "drawOnChartArea": False
                        },
                        "scaleLabel": {
                            "display": "true",
                            "labelString": "MWh/h"
                        }
                    }

                ]
            }
        }
    }
    params = {
        'chart': json.dumps(config),
        'width': 500,
        'height': 300,
        'backgroundColor': 'white',
    }

    quickchart_url = 'https://quickchart.io/chart/create'
    post_data = params

    response = requests.post(
        quickchart_url,
        json=post_data,
    )

    if (response.status_code != 200):
        print('Error:', response.text)
        return None
    else:
        chart_response = json.loads(response.text)
        url = chart_response['url']
        return url

def create_price_image_url(labels, pricedata, maxtick=None):
    if maxtick is None:
        maxtick = max(pricedata)
        # Round to upper tenth
        maxtick -= maxtick % -10

    config = {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": [{
                "fill": "true",
                "label": "Sähkön hinta",
                "data": pricedata,
                "spanGaps": "false",
                "lineTension": 0.2,
                "pointRadius": 0,
                "borderColor": "#000000",
                "pointStyle": "circle",
                "backgroundColor": "#000000",
                "steppedLine": True,
                "borderWidth": 2,
                "yAxisID": "y1"
            }
            ]
        },
        "options": {
            "title": {
                "display": "true",
                "text": f"Sähkön spot-hinnat Suomessa tunneittain {labels[0][:10]} (sis. ALV)",
                "position": "top",
                "fontSize": 12,
                "fontColor": "#000000",
                "fontStyle": "bold",
                "padding": 10,
                "lineHeight": 1.2
            },
            "legend": {
                "position": "top",
                "display": False

            },
            "scales": {
                "xAxes": [{
                    "type": "time",
                    "time": {
                        "parser": "DD.MM.YYYY HH:mm",
                        "isoWeek": "true",

                        "displayFormats": {
                            "day": "DD.MM.",
                            "hour": "HH:mm"
                        }
                    },
                    "ticks": {
                        "source": "auto",
                        "maxRotation": 0,
                        "autoSkipPadding": 5,
                        "fontColor": "#0E101E",
                        "fontStyle": "bold",
                        "fontSize": 10,
                        "padding": 8,
                        "major": {
                            "unit": "hour",
                            "displayFormats": {
                                "day": "DD.MM.",
                                "hour": "HH:mm"
                            }
                        },
                    },
                    "gridLines": {
                        "display": "true",
                        "color": "rgba(0, 0, 0, 0.05)",
                        "borderDash": [
                            0,
                            0
                        ],
                        "lineWidth": 1,
                        "drawBorder": "true",
                        "drawOnChartArea": "false",
                        "drawTicks": "true",
                        "tickMarkLength": 5,
                        "zeroLineWidth": 1,
                        "zeroLineColor": "rgba(0, 0, 0, 0.25)",
                        "zeroLineBorderDash": [
                            0,
                            0
                        ]
                    },
                    "scaleLabel": {
                        "display": False,
                        "labelString": "Aika"
                    }
                }],

                "yAxes": [
                    {
                    "id": "y1",
                    "ticks": {
                        "beginAtZero": "true",
                        "min": 0,
                        "max": maxtick,
                        "maxTicksLimit": 20,
                        "fontColor": "#000000",
                        "fontSize": 10,
                        "fontStyle": "bold",
                        "padding": 8,
                        "stepSize": 5
                    },
                    "gridLines": {
                        "display": "true",
                        "color": "rgba(0, 0, 0, 0.1)",
                        "borderDash": [
                            0,
                            0
                        ],
                        "lineWidth": 1,
                        "drawBorder": "true",
                        "drawOnChartArea": "true",
                        "drawTicks": "true",
                        "tickMarkLength": 5,
                        "zeroLineWidth": 1,
                        "zeroLineColor": "rgba(0, 0, 0, 0.25)",
                        "zeroLineBorderDash": [
                            0,
                            0
                        ]
                    },
                    "scaleLabel": {
                        "display": "true",
                        "labelString": "snt/kWh"
                        }
                    }
                ]
            }
        }
    }
    params = {
        'chart': json.dumps(config),
        'width': 500,
        'height': 300,
        'backgroundColor': 'white',
    }

    quickchart_url = 'https://quickchart.io/chart/create'
    post_data = params

    response = requests.post(
        quickchart_url,
        json=post_data,
    )

    if (response.status_code != 200):
        print('Error:', response.text)
        return None
    else:
        chart_response = json.loads(response.text)
        url = chart_response['url']
        return url
