import os
import json
import numpy as np
import json2parq

def loadQueries():
    queries = []
    with open('querylist_nvidia') as f:
        for metric in f:
            queries.append(metric.strip('\n').strip(' '))
    return queries

def unpackTar(path):
    counter = 0
    for file in os.listdir(path):
        indexes = None
        #test = file.split('.')[0]
        #print (test)

        if (file.endswith(".tar.gz")):
            if(counter < 2):
                print('skipped ' + os.path.join(path,file))
                counter += 1
                continue

            print("Accessing: " + os.path.join(path, file))
            split = file.split('_')
            start = int(split[1])
            end = start + 86400
            indexes = np.arange(start, end, 15).tolist()
#            os.system('tar -C /project/kristian/archives/temp -xzf ' + path + file)
            readMetricDirs('/project/kristian/archives/temp/project/kristian/logs/', indexes)
            return
            os.system('rm -r /project/kristian/archives/temp/*')
#            print("cleanup of " + os.path.join(path, file) + " complete")
            counter += 1
        if(counter > 92):
            break

def readMetricDirs(path, indexes):
    queries = loadQueries()
    for directory in os.listdir(path):
        for file in os.listdir(path + directory):
            if file not in queries:
#                print(file + ' not in queries')
                continue
            jsonpath = path + directory + '/' + file
            with open(jsonpath) as h:
                jsonData = json.loads(h.read())
                json2parq.pandasParq(jsonData, directory, indexes)

unpackTar("/project/kristian/archives/")

#readMetricDirs('/project/kristian/archives/temp/project/kristian/logs/')
