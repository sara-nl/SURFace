""" Constants """
DATA_PATH = "/project/location/" #<should be directory path> | this is where data is saved
QUERY_LIST = "querylist" #metric input - this file needs to be in the same folder as this and the run script #TODO: fix & detach this
PROMETHEUS_SERVER="127.0.0.1" #Prometheus address
PROMETHEUS_PORT="9090" #Prometheus port
CONST_DAY = 24 * 3600 * 1 #hours a day * seconds in an hour * no of days saved in Prometheus
RESOLUTION = 15 #Sampling resolution

# for encryption purposes
nonce = b'nonce' #your nonce
key = b'my key' #your jey

# Constants:
NODE_LIST = 'nodeList'
GPU_NODE_LIST = 'gpuNodeList'