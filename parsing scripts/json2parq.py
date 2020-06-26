import json
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import pyarrow as pa
from collections import OrderedDict
from itertools import zip_longest
import os.path
from Crypto.Cipher import Salsa20
from Crypto.Util.number import bytes_to_long

nonce = b'surfSARA'
key = b'Generocity Giant'

def loadNodeList(fileName):
    nodes = []
    with open(fileName) as f:
        for line in f:
#            line = line.strip('\n').strip(' ')
#            rXX = line[1:3]
#            nXX = line[4::]

#            cipher = Salsa20.new(key=key, nonce=nonce)
#            rXX = cipher.encrypt(rXX.encode())
#            rXX = bytes_to_long(rXX)

#            cipher = Salsa20.new(key=key, nonce=nonce)
#            nXX = cipher.encrypt(nXX.encode())
#            nXX = bytes_to_long(nXX)

#            newLine = ('r' + str(rXX) + 'n' + str(nXX))
#            nodes.append(newLine.strip('\n').strip(' '))
            nodes.append(line.strip('\n').strip(' '))
    return nodes

def loadFile(fileName):
    counter = 0
    d = {}
    with open(fileName) as f:
        for line in f:
            d[counter] = line.strip('\n')
            counter += 1
    return d

def stringToNum(string):
    try:
        print('in stringtonum1 converting: ' + string)
        return float(string)
    except ValueError:
        print("Value error float on " + string)

    print("conversion error")

#def convertAndPad(values, indexes):
#    valueList = list()
#    if (len(values) != len(indexes)):
#        test = dict(values) #converting this to dictionary for easy lookups
#        for index in indexes:
#            if(index not in test):
#                valueList.append(-1.0)
#            else:
#                valueList.append(stringToNum(test[index]))
#
#    else:
#        for value in values:
#            valueList.append(stringToNum(value[1]))
#
#    return valueList

def stringToNum2(string):
    try:
        return int(string)
    except ValueError:
        print("Value error int on " + string)

    print("conversion error")

def convertAndPad(values, indexes, gpu):
    valueList = list()
    if (len(values) != len(indexes)):
        test = dict(values) #converting this to dictionary for easy lookups
        for index in indexes:
            if(index not in test):
                if(gpu):
                    valueList.append(0)
                else:
                    print('appending -1.0')
                    valueList.append(-1.0)
            else:
                if(gpu):
                    valueList.append(stringToNum2(test[index]))
                else:
                    valueList.append(stringToNum(test[index]))

    else:
        for value in values:
            if(gpu):
                valueList.append(stringToNum2(value[1]))
            else:
                valueList.append(stringToNum(value[1]))

    return valueList


def splitJson(jsonObject, dict, indexes, nodeList):
    longkey = list()
    dict.clear()
    for result in jsonObject['data']['result']:
        if 'instance' in result['metric']: #check if result contains no metric
            k = result['metric']['instance']
            v = result['values']

            if not (k.startswith('r')):
                continue


            k = k.split('.', 1)[0] #shorten node name down to just the node name itself without the full path

 #           if not (k.startswith('r')): #skip nodes that aren't compute nodes
 #              continue

            #rXX = k[1:3]
            #nXX = k[4::]
            #cipher = Salsa20.new(key=key, nonce=nonce)
            #rXX = cipher.encrypt(rXX.encode())
            #rXX = bytes_to_long(rXX)
            #cipher = Salsa20.new(key=key, nonce=nonce)
            #nXX = cipher.encrypt(nXX.encode())
            #nXX = bytes_to_long(nXX)

            #k = ('r' + str(rXX) + 'n' + str(nXX)).strip('\n').strip(' ')
            valueTupleList = [i for i in v]
            values = convertAndPad(valueTupleList, indexes)
            dict[k] = values

def splitGPU(jsonObject, dict, indexes, queryName):
    prevNode = 'NONE'
    prePack = []
    minorNum = 0

    dict.clear()
    for result in jsonObject['data']['result']:
        if 'instance' in result['metric']: #check if result contains no metric
            k = result['metric']['instance'].split('.', 1)[0]
            v = result['values']
#            print(result['metric']['minor_number'])

            if not (k.startswith('r')):
                continue

            if(prevNode == 'NONE'):
                prevNode = k
            elif(prevNode != k):
                postPack = []
                for n in range(len(prePack[0])):
                    c = 0
                    for j in range(len(prePack)):
                        #packing values into c to create combined list
                        if(j > 3):
                            break
                        c = c | (prePack[j][n] << 16 * j)
                    postPack.append(c)

                if(max(postPack) > 0xFFFFFFFFFFFFFFFF):
                    print('Max value larger than 64 bits')
                    print(max(postPack))
                    print('node: ' + k)
                    print('len of j: ' + str(len(prePack)))

                prePack = []
                dict[k] = postPack
                prevNode = k
                minorNum = int(result['metric']['minor_number'])

#            print('Node: ' + k)

            if(minorNum != int(result['metric']['minor_number'])):
                print('mismatch on node ' + k)
                print('minornum = ' + str(minorNum))
                print('minor_number = ' + str(result['metric']['minor_number']))
#                minorNum += 1
#                continue

            minorNum += 1

            valueTupleList = [i for i in v]
            values = convertAndPad(valueTupleList, indexes, True)

            if (queryName.startswith('nvidia_gpu_power')):
                #print('Node ' + k)
                #print('MinorNum = ' + str(minorNum))
                newValues = [int(x / 1000) for x in values]
                prePack.append(newValues)

            elif (queryName.startswith('nvidia_gpu_memory')):
                newValues = [int(x / 1048576) for x in values]
                prePack.append(newValues)

            else:
                prePack.append(values)

    postPack = []
#    print('Final bit')
#    print(len(prePack))
#    print(len(prePack[0]))
    if(len(prePack) == 0):
        return
    for n in range(len(prePack[0])):
        c = 0
        for j in range(len(prePack)):
            #packing values into c to create combined list
            if(j > 3):
                break
            c = c | (prePack[j][n] << 16 * j)
        postPack.append(c)

        if(max(postPack) > 0xFFFFFFFFFFFFFFFF):
            print('Max value larger than 64 bits')
            print(max(postPack))
            print('node: ' + k)
            print('len of j: ' + str(len(prePack)))

    prePack = []
    dict[k] = postPack



def pandasParq(jsonObject, queryName, indexes):
    dict = {}
    nodeList = loadNodeList('nodeList')
    nodeList.sort()
    gpuNodeList = loadNodeList('gpuNodeList')
    gpuNodeList.sort()

    if(queryName.startswith('nvidia')):
        splitGPU(jsonObject, dict, indexes, queryName)
    else:
        splitJson(jsonObject, dict, indexes, nodeList)

#    print(queryName)
    if( queryName.startswith('nvidia') ):
        for node in gpuNodeList:
            if not node in dict and len(dict) > 0:
                values = convertAndPad([], indexes, True)
                dict[node] = values
    else:
        for node in nodeList:
            if not node in dict and len(dict) > 0:
                values = convertAndPad([], indexes, False)
                dict[node] = values

    oDict = OrderedDict(sorted(dict.items()))

    if indexes and len(dict) > 0:
        testlist = dict.values()
        #maybe can use the nodelist when creating the dataframes instead of the dicts, then loop over the dict and set the values to the
	#correct frame
        df = pd.DataFrame(data=oDict, index=indexes, dtype=object, copy=False)
        df.index.name = 'time'
        df = df.astype('Int64')

        #print(df)

        table = pa.Table.from_pandas(df, preserve_index=True)

#        pq.write_to_dataset(table, root_path="/home/kristian/lisa.nvidia/" + queryName, flavor="spark")
        #pq.write_to_dataset(table, root_path="/project/kristian/lisa.parquet/" + queryName, flavor="spark")

