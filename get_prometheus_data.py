import os
import json
import numpy as np
import time
import sys
from datetime import datetime, date
import config
import requests

#parse file for queries
def loadFile(fileName):
    counter = 0
    d = {}
    with open(fileName) as f:
        for line in f:
            d[counter] = line.strip('\n')
            counter = counter + 1
    return d


#build curl query
def buildQuery(queryMetric, queryStart, queryEnd, queryRes):
    return 'http://{0}:{1}/api/v1/query_range?query={2}&start={3}&end={4}&step={5}'.format(config.PROMETHEUS_SERVER, config.PROMETHEUS_PORT, queryMetric, queryStart, queryEnd, int(queryRes))


""" Get relevant time values """
#TODO::upgrade this to use UTC to avoid daylight savings problems
def getTime():
    now = datetime.now()
    return int(time.mktime(datetime.timetuple(datetime(now.year, now.month, now.day))))


def epoch_to_utc(epoch):
    '''Convert epoch timestamp to ISO UTC timestamp'''
    return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(float(epoch)))


# Getting start and end times using the getTime function
# then generate the indexes required for this day to be used in the conversion to parquet
# we start the query at midnight **today**
queryEnd = getTime() - config.RESOLUTION
queryStart = queryEnd - config.CONST_DAY + config.RESOLUTION
# queryMetrics = "|".join(loadFile(config.QUERY_LIST).values())
queryMetrics = [l for l in loadFile(config.QUERY_LIST).values()][0]
print(queryMetrics)
query = buildQuery(queryMetrics, queryStart, queryEnd, config.RESOLUTION)
print("Running query {}".format(query))
response = requests.get(query).json()
print(response)
print("Data collection complete")
