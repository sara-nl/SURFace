import json
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from collections import OrderedDict
from Crypto.Cipher import Salsa20
from Crypto.Util.number import bytes_to_long
from . import config

nonce = config.nonce
key = config.key

# Constants:
NODE_LIST = config.NODE_LIST
GPU_NODE_LIST = config.GPU_NODE_LIST

# function that encrypts the node name passed as argument
# function expects argument to be structured as r##n##
# the reason newline and space is stripped from the nodename is to guarantee the same result of the encryption regardless
# of where it comes from
# bytes_to_long converts the encrypted bytecode into a long integer
def encryptNodeName(nameArg):
    nodeName = nameArg.strip('\n').strip(' ')
    rXX = nodeName[1:3]
    nXX = nodeName[4::]

    cipher = Salsa20.new(key=key, nonce=nonce)
    rXX = cipher.encrypt(rXX.encode())
    rXX = bytes_to_long(rXX)

    cipher = Salsa20.new(key=key, nonce=nonce)
    nXX = cipher.encrypt(nXX.encode())
    nXX = bytes_to_long(nXX)

    return ('r' + str(rXX) + 'n' + str(nXX))

# Function opens a file using the argument as filename, reads the contents into a list and returns it.
# Function includes logic to enable encryption of node names by reading the numbers from the nodenames and encrypting them separately
def loadNodeList(fileName):
    nodes = []
    with open(fileName) as f:
        for line in f:
            toAppend = line.strip('\n').strip(' ')
            # to enable on read encryption uncomment this line
            #toAppend = encryptNodeName(toAppend)
            nodes.append(toAppend)
    return nodes

# deprecated function that is no longer in use
def loadFile(fileName):
    counter = 0
    d = {}
    with open(fileName) as f:
        for line in f:
            d[counter] = line.strip('\n')
            counter += 1
    return d

# the string to num functions attempt to convert the argument to float or int respectively, if they fail the print an error message and then return
# these are being used to validate the inputs from compute nodes and gpu nodes respectively, if gpu is true then it converts to int these should be combined into one function
# once it has been normalized what 'no reading' looks like from nodes
def stringToNum(string, gpu):
    if(gpu):
        try:
            return int(string)
        except ValueError:
            print("Value error int on " + string)
    else:
        try:
            return float(string)
        except ValueError:
            print("Value error float on " + string)

    print("conversion error")

# function checks the if any indexes are missing and injects a no measurement value if that index does not exist
# if it does exist it makes sure that the value given is converted to a numeric instead of storing it as a string
# in case of gpu's it appends 0 else -1.0, however this needs to be normalized such as no measurement should always be represented the same way.
def convertAndPad(values, indexes, gpu):
    valueList = list()
    if (len(values) != len(indexes)):
        test = dict(values) #converting this to dictionary for easy lookups
        # this for loop specifically goes through the list of indexes, if that index does not exist in the dataset
        # then inserts a non measurement value into the metric, non measurement value needs to be normalized to a specific value
        for index in indexes:
            if(index not in test):
                if(gpu):
                    valueList.append(0)
                else:
                    valueList.append(-1.0)
            else:
                valueList.append(stringToNum(test[index], gpu))
    else:
        # note value in this case is a tuple (time, value) so when appending it has to be indexed in this way value[1]
        # note that this is different from the above code due to that code using a dictionary where the time has become the index
        # potentially could use dictionary for both parts of this loop to simplify the function.
        for value in values:
            valueList.append(stringToNum(value[1], gpu))

    return valueList


'''
Structure of json file
data
    result[ #result is an array of subtrees each of which contains the metric and values branch
        metric[
            instance # this stores the full node name r##n##.lisa.surfsara.nl
            minor number # this stores the iteration for that specific node, e.g. in nvidia metrics '0' is the first gpu and '3' is the fourth gpu
            #few other ones that are not as relevant but may be worth exploring
        ]
        values[
            (timestamp, measurement)    #in the array of values the data is stored like this.
        ]
        .
        .
        .
        .
    ]
'''
# reads the json input and splits it indo nodes and metrics respectively, then returns a dictionary containing all the nodes and their values respectively.
# includes a comment block used for encryption of node names during parsing
# with the data being a nested datastructure to reach the metrics and node information you need to dig into it
# TODO::Handle special cpu cases where we are getting results per cpu, needs to be designed to handle that somehow
def splitJson(jsonObject, dict, indexes, queryName):
    dict.clear()
    for result in jsonObject['data']['result']:
        if 'instance' in result['metric']: #check if result contains no metric
            k = result['metric']['instance']
            v = result['values']

            # will skip all non compute nodes, this means no administration node, software node, login node or fileserver is included in the metrics
            if not (k.startswith('r')):
                continue

            # node names come as a full address on lisa to make the dataset easier to read we prune the node down to just r##n##
            k = k.split('.', 1)[0]

            # to enable on parse encryption of node names uncomment this line
            # k = encryptNodeName(k)

            valueTupleList = [i for i in v]
            values = convertAndPad(valueTupleList, indexes, False) # because there is no gpu present in this split this passes false
            dict[k] = values

# same intro as splitJson, however this code is only valid for metrics in nvidia so the potential to merge the functions and handle nvidia using helper functions
# may be a much better solution.
# difference is this function handles nvidia metrics specifically because they come in 4 results for each node.
# it compares the currently read node to the previously read node, once there is a mismatch it calls packToInt64 which returns a list that is added
# to the dictionary, instead of reading node names this function could be modified to read minor number and watch for it to reset to 0, 
# so every time minor number hits zero it would package the values.
def splitGPU(jsonObject, dict, indexes, queryName):
    prevNode = 'NONE'
    prePack = []
    minorNum = 0

    dict.clear()
    for result in jsonObject['data']['result']:
        if 'instance' in result['metric']: #check if result contains no metric
            k = result['metric']['instance'].split('.', 1)[0]
            v = result['values']

            if not (k.startswith('r')):
                continue

            if(prevNode == 'NONE'):
                prevNode = k
            
            # if the previous node is not equal to the current node then the integer packaging needs to be done and the lists cleared
            # could also simplify this by just checking the minor number and if the minor number in the newly read tree is = 0 then
            # you have to package the values before loading in the new node.
            elif(prevNode != k):
                dict[k] = packToInt64(prePack)
                prePack = []
                prevNode = k

            minorNum += 1

            valueTupleList = [i for i in v]
            values = convertAndPad(valueTupleList, indexes, True)

            # if nvidia gpu power is found then the queryName should be modified to 
            # be nvidia_gpu_power_watts so that we can claim correctness in naming since at the moment
            # it is milliwatts while the data represented is in watts due to this modification
            # this modification and the memory one are here to make sure the data fits into 64 bit values when packaged
            # another way would be to modify the queries to prometheus to include the calculations to do this calculation so that it is unnecessary here
            #modified the branches to simplify the code
            if (queryName.startswith('nvidia_gpu_power')):
                values = [int(x / 1000) for x in values]
                # newValues = [int(x / 1000) for x in values]
                # prePack.append(newValues)

            elif (queryName.startswith('nvidia_gpu_memory')):
                values = [int(x / 1048576) for x in values]
                # newValues = [int(x / 1048576) for x in values]
                # prePack.append(newValues)
            
            # if neither of the previous ones is true then it the function just appends the value unchanged
            prePack.append(values)

    # checks if prepack contains information from one final node, if there isn't it returns else it 
    # runs the pack to int once more
    if(len(prePack) == 0):
        return

    dict[k] = packToInt64(prePack)
    prePack = []

# packs the values from a list of lists into a 64 bit value
# expects this format prePackaged[[value],[value],[value],[value]] where each value is a 16bit number or less
# this function then uses bitwise or '|' and shifting '<<' to pack them into a 64 bit value
# and creates a new list called postPack[] that consists of all the lists inside prePackaged combined into one
def packToInt64(prePackaged):
    postPack = []
    for n in range(len(prePackaged[0])):
        c = 0
        for j in range(len(prePackaged)):
            if(j > 3):
                break
            c = c | (prePackaged[j][n] << 16 * j)
        postPack.append(c)

    ''' Consider
        if(max(postPack).bit_length() > 64):
            print warnings
    '''
    if(max(postPack).bit_length() > 64):
        print('Max value larger than 64 bits')
        print(max(postPack))
        print('len of j: ' + str(len(prePackaged)))
    #if(max(postPack) > 0xFFFFFFFFFFFFFFFF):

    return postPack

# opening function to the script, takes as an argument the jsonObject containing the query result
# the name of the query and the list of indexes for the day that is being parsed
# the index list will have to be generated elsewhere, it's  from midnight to midnigt - 15sec, with 15 second intervals so 5760 values.
def pandasParq(jsonObject, queryName, indexes):
    dict = {}
    #the reason for loading in the nodelists for gpu nodes and then all nodes
    #is to validate if any nodes are missing in the dataset, however since nodelists in the future will not be static this requires redesign
    #one issue with parquet is that if there is a difference between two files e.g. column wise etc then you have to merge the parquet datasets
    #however when trying to merge such large datasets i ran into issues with memory, finding a reliable source of nodelists outside of having to manually update
    #would be an amazing solution
    nodeList = loadNodeList(NODE_LIST)
    nodeList.sort()
    gpuNodeList = loadNodeList(GPU_NODE_LIST)
    gpuNodeList.sort()
    gpu = False

    if(queryName.startswith('nvidia')):
        gpu = True

    #different split functions if you have gpu or non cpu metric, would like to merge those and create sub functions that they call with.
    if(gpu):
        splitGPU(jsonObject, dict, indexes, queryName)
    else:
        splitJson(jsonObject, dict, indexes, queryName)

    # validation code - might be best to separate this into a separate function
    # this checks the dict against the nodelist
    # if the node is not in the dictionary it calls convertAndPad with an empty list, indexes and true/false depending on what is needed.
    # convertAndPad then generates a list filled with 0 or -1.0 depending on gpu or not, becomes simpler if we make sure all non readings are the same
    if(gpu):
        for node in gpuNodeList:
            if not node in dict and len(dict) > 0:
                values = convertAndPad([], indexes, True)
                dict[node] = values
    else:
        for node in nodeList:
            if not node in dict and len(dict) > 0:
                values = convertAndPad([], indexes, False)
                dict[node] = values

    # ordering the columns of the dictionary after validation and adding missing nodes ensures that all parquet files are the same.
    # note this does not reorder the values in the dataset only ensures that the columns are always in the same order.
    oDict = OrderedDict(sorted(dict.items()))

    #checks if the program indeed got results from the provided metric. this is a validation check to make sure data was
    #returned from this query
    if indexes and len(dict) > 0:
        #maybe can use the nodelist when creating the dataframes instead of the dicts, then loop over the dict and set the values to the
	    #correct frame
        df = pd.DataFrame(data=oDict, index=indexes, dtype=object, copy=False)
        writeParquet(df, queryName)

#saves to parquet dataset from the dataframe and using the queryName for the folder to save it to
def writeParquet(df, queryName):
    df.index.name = 'time'
    df = df.astype('Int64')

    table = pa.Table.from_pandas(df, preserve_index=True)

    #the write to dataset will generate the parquet file as part of the dataset in the existing folder, in case of no dataset being located
    #at the root_path it write_to_dataset will start it
    #this could be worth a redesign to open the existing dataset if it is there and appending the new data to the dataset
    #TODO::adjust queryname for gpu memory since it is modified to be Megabytes and gpu power since it is watts not milliwatts
    pq.write_to_dataset(table, root_path="/project/kristian/lisa.parquet/" + queryName, flavor="spark")