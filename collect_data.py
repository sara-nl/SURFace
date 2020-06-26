import os
import json
import numpy as np
import time
import threading
import queue
import sys
from datetime import datetime
from subprocess import Popen
from subprocess import PIPE

""" Constants """
DATA_PATH = "/project/kristian/" #<should be directory path>
QUERY_LIST = "querylist"
#this is the start of the curl query that is constructed in the buildQuery(query) function
CURL_START = "curl -s '145.101.32.28:9090/api/v1/query_range?query="
#this is the time interval of the collected datapoints
QUERY_RESOLUTION = "&step=15'"


#for each key value pair in dictionary append to queue
def fillQueue(dict):
    for key,val in dict.items():
        q.put(val)
    q.join()

#while queue has jobs perform jobs, this is thread safe
def worker():
    while True:
        item = q.get()
        if item is None:
            break
        runLoop(item)
        q.task_done()

#populate the list of workers
def generateWorkers():
    for i in range(num_worker_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

#depopulate the list of workers
def terminateWorkers():
    for i in range(num_worker_threads):
        q.put(None)
    for t in threads:
        t.join()

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
def buildQuery(query):
    #this accesses the address where prometheus is.
    #curlStart = "curl -s '145.101.32.28:9090/api/v1/query_range?query="
    queryMetric = query
    queryStart = "&start="
    queryEnd = "&end="
    #queryRes = "&step=15'"
    return CURL_START + queryMetric + queryStart + str(start) + queryEnd + str(end) + QUERY_RESOLUTION

def runLoop(queryName):
    print('query: ' + queryName)

    query = buildQuery(queryName)
    result = os.popen(query).read()
    jsonData = json.loads(result)

    #with open("/home/kristian/newquerytest/" + queryName, 'w') as outfile:
    #    json.dump(jsonData,outfile)

    os.mkdir(DATA_PATH + "logs/" + queryName)
    with open(DATA_PATH + "logs/" + queryName + "/" + queryName, 'w') as outfile:
        json.dump(jsonData, outfile)

#    if(queryName == 'nvidia_gpu_power_usage_milliwatts'):
#        with open("/home/kristian/" + queryName, 'w') as outfile:
#            json.dump(jsonData, outfile)


""" -------------------------------------------------------------------------------------------------------------- """

""" Get relevant time values """
#TODO::upgrade this to use UTC to avoid daylight savings problems
def getTime():
    now = datetime.now()
    return int(time.mktime(datetime.timetuple(datetime(now.year, now.month, now.day))))

def epoch_to_utc(epoch):
    '''Convert epoch timestamp to ISO UTC timestamp'''
    return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(float(epoch)))

""" -------------------------------------------------------------------------------------------------------------- """

""" Collect sacct information """
class Sacct():

    def __init__(self, start, end, values, states):
        self._start = start
        self._end = end
        self._format = values
        self._states = states
        self._sacct()

    def _sacct(self):
        '''Collect output from sacct'''
        sacct_command = '/usr/bin/sacct --allocations --allusers --format %s --noheader --parsable2 --state=%s --start=%s --end=%s' % (
                                                     ','.join(self._format), ','.join(self._states), self._start, self._end)
        if debug:
            print("Sacct Command:\n" + sacct_command)
        # use UTC timestamps as input and get epoch timestamps in output
        stdout, stderr = Popen(sacct_command, shell=True, stdout=PIPE, stderr=PIPE, env={'SLURM_TIME_FORMAT': '%s', 'TZ': 'UTC'}).communicate(input=None)
        if stderr:
            print(stderr, file=sys.stderr)
            sys.exit(1)
        self._sacct_output = stdout.decode().splitlines()

    def get_jobs(self):
        '''Parse sacct output and return iterator'''
        for line in self._sacct_output:
            if debug:
                print('DEBUG: sacct_output [%s]' % line)
            sacct_fields = line.split('|')
            if len(sacct_fields) != len(self._format):
                print('ERROR: sacct output does not match format', file=sys.stderr)
                sys.exit(1)
            yield line


def getAndSaveSacctData():
    sacct_values = ('jobid', 'gid', 'uid', 'partition', 'submit', 'start', 'end', 'elapsedraw',
                        'cputimeraw', 'ncpus', 'nnodes', 'nodelist',
                        'exitcode', 'state', 'timelimit')

    sacct_states = ('CANCELLED', 'COMPLETED', 'FAILED', 'NODE_FAIL', 'OUT_OF_MEMORY', 'PREEMPTED', 'TIMEOUT')

    test_sacct = Sacct(epoch_to_utc(start), epoch_to_utc(start + CONST_DAY), sacct_values, sacct_states)

    job_list = list()

    for line in test_sacct.get_jobs():
        job_list.append(line)

    with open(DATA_PATH + "sacct/sacct_" + str(start) + "-" + str(start + CONST_DAY), 'w') as outfile:
        for line in job_list:
            outfile.write(line + '\n')

    print("Sacct data collected")

""" -------------------------------------------------------------------------------------------------------------- """

""" Compress collected json data """
def tar():
    os.system("tar czf " + DATA_PATH + "archives/logs_" + str(start) + "_" + str(end) + ".tar.gz " + DATA_PATH + "logs/")
    print("tar successful")

""" post run cleanup """
# delete all collected json file post archiving them with tar
def cleanup():
    os.chdir(DATA_PATH + "logs/")
    os.system("rm -r *")
    os.chdir("../datascript/")
    print("Cleanup complete")

""" -------------------------------------------------------------------------------------------------------------- """

""" Setup """
# load queries into dictionary
q = queue.Queue()
threads = []
num_worker_threads = 1

# Getting start and end times using the getTime function
# then generate the indexes required for this day to be used in the conversion to parquet
midnight = getTime()
CONST_DAY = 86400

start = midnight - CONST_DAY * 1
end = start + CONST_DAY - 15


# Generates a list of range from start to end on a step of 15 to match with the collected data
indexes = np.arange(start, end + 15, 15).tolist()
debug = False

""" Generate workers and fill up the queue to start the data collection """
generateWorkers()
fillQueue(loadFile(QUERY_LIST))
terminateWorkers()
getAndSaveSacctData()

print("Data collection complete")

""" Compress then cleanup collected data """
tar()
cleanup()
