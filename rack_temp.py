import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import matplotlib.pyplot as plt
import numpy as np
import glob
import time
import datetime as dt
import matplotlib.dates as md
import dateutil
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

metrics = {"surfsara_ambient_temp": "Ambient Temperature"}
#            "nvidia_gpu_temperature_celsius": "GPU Temperature",
#            "nvidia_gpu_fanspeed_percent": "GPU Fanspeed"}

titan_rtx = ["r28n5", "r28n4", "r28n3", "r28n2", "r28n1", "r29n5", "r29n4", "r29n3", "r29n2", "r29n1", "r33n6", "r34n1", "r34n2", "r34n3", "r34n4", "r34n5", "r34n6", "r34n7", "r35n5", "r35n4", "r35n3", "r35n2", "r35n1", "r36n5", "r36n4", "r36n3", "r36n2", "r36n1"]

gpu_nodes = ["r30n1", "r30n2", "r30n3", "r30n4", "r30n5", "r30n6", "r30n7", "r31n1", "r31n2", "r31n3", "r31n4", "r31n5", "r31n6", "r32n1", "r32n2", "r32n3", "r32n4", "r32n5", "r32n6", "r32n7", "r33n2", "r33n3", "r33n4", "r33n5"]

racks = {
"rack_1899": ['r1899n7', 'r1899n4', 'r1899n5', 'r1899n2', 'r1899n3', 'r1899n0', 'r1899n1', 'r1899n14', 'r1899n15', 'r1899n1899', 'r1899n1898', 'r1899n1897', 'r1899n1896', 'r1899n1903', 'r1899n1902', 'r1899n1901', 'r1899n1900', 'r1899n1891', 'r1899n1890', 'r1899n1131', 'r1899n1130', 'r1899n1129', 'r1899n1128', 'r1899n1135', 'r1899n1134', 'r1899n1133', 'r1899n1132', 'r1899n1123', 'r1899n1122', 'r1899n1387', 'r1899n1386', 'r1899n1385'],
"rack_1898": ['r1898n7', 'r1898n4', 'r1898n5', 'r1898n2', 'r1898n3', 'r1898n0', 'r1898n1', 'r1898n14', 'r1898n15', 'r1898n1899', 'r1898n1898', 'r1898n1897', 'r1898n1896', 'r1898n1903', 'r1898n1902', 'r1898n1901', 'r1898n1900', 'r1898n1891', 'r1898n1890', 'r1898n1131', 'r1898n1130', 'r1898n1129', 'r1898n1128', 'r1898n1135', 'r1898n1134', 'r1898n1133', 'r1898n1132', 'r1898n1123', 'r1898n1122', 'r1898n1387', 'r1898n1386', 'r1898n1385'],
"rack_1897": ['r1897n7', 'r1897n4', 'r1897n5', 'r1897n2', 'r1897n3', 'r1897n0', 'r1897n1', 'r1897n14', 'r1897n15', 'r1897n1899', 'r1897n1898', 'r1897n1897', 'r1897n1896', 'r1897n1903', 'r1897n1902', 'r1897n1901', 'r1897n1900', 'r1897n1891', 'r1897n1890', 'r1897n1131', 'r1897n1130', 'r1897n1129', 'r1897n1128', 'r1897n1135', 'r1897n1134', 'r1897n1133', 'r1897n1132', 'r1897n1123', 'r1897n1122', 'r1897n1387', 'r1897n1385'],
"rack_1896": ['r1896n7', 'r1896n4', 'r1896n5', 'r1896n2', 'r1896n3', 'r1896n0', 'r1896n1', 'r1896n14', 'r1896n15', 'r1896n1899', 'r1896n1898', 'r1896n1897', 'r1896n1896', 'r1896n1903', 'r1896n1902', 'r1896n1901', 'r1896n1900', 'r1896n1891', 'r1896n1890', 'r1896n1131', 'r1896n1130', 'r1896n1129', 'r1896n1128', 'r1896n1135', 'r1896n1134', 'r1896n1133', 'r1896n1132', 'r1896n1123', 'r1896n1122', 'r1896n1387', 'r1896n1386', 'r1896n1385'],
"rack_1903": ['r1903n7', 'r1903n4', 'r1903n5', 'r1903n2', 'r1903n3', 'r1903n0', 'r1903n1', 'r1903n14', 'r1903n15', 'r1903n1899', 'r1903n1898', 'r1903n1897', 'r1903n1896', 'r1903n1903', 'r1903n1902', 'r1903n1901', 'r1903n1900', 'r1903n1891', 'r1903n1890', 'r1903n1131', 'r1903n1130', 'r1903n1129', 'r1903n1128', 'r1903n1135', 'r1903n1134', 'r1903n1133', 'r1903n1132', 'r1903n1123', 'r1903n1122', 'r1903n1387', 'r1903n1386', 'r1903n1385'],
"rack_1902": ['r1902n7', 'r1902n4', 'r1902n5', 'r1902n2', 'r1902n3', 'r1902n0', 'r1902n1', 'r1902n14', 'r1902n15', 'r1902n1899', 'r1902n1898', 'r1902n1897', 'r1902n1896', 'r1902n1903', 'r1902n1902', 'r1902n1901', 'r1902n1900', 'r1902n1891', 'r1902n1890', 'r1902n1131', 'r1902n1130', 'r1902n1129', 'r1902n1128', 'r1902n1135', 'r1902n1134', 'r1902n1133', 'r1902n1132', 'r1902n1123', 'r1902n1122', 'r1902n1387', 'r1902n1386', 'r1902n1385'],
"rack_1128": ['r1128n1128', 'r1128n1133'],
"rack_1134": ['r1134n5', 'r1134n2', 'r1134n3', 'r1134n0', 'r1134n1', 'r1134n14', 'r1134n15', 'r1134n1899', 'r1134n1898', 'r1134n1897', 'r1134n1896', 'r1134n1903', 'r1134n1902', 'r1134n1901', 'r1134n1900', 'r1134n1891', 'r1134n1890', 'r1134n1131', 'r1134n1130', 'r1134n1129', 'r1134n1128', 'r1134n1135', 'r1134n1134', 'r1134n1133', 'r1134n1132', 'r1134n1123', 'r1134n1122', 'r1134n1387', 'r1134n1386', 'r1134n1385'],
"rack_1133": ['r1133n4', 'r1133n5', 'r1133n2', 'r1133n3', 'r1133n0', 'r1133n1', 'r1133n14', 'r1133n15', 'r1133n1899', 'r1133n1898', 'r1133n1897', 'r1133n1896', 'r1133n1903', 'r1133n1902', 'r1133n1901', 'r1133n1900', 'r1133n1891', 'r1133n1890', 'r1133n1131', 'r1133n1130', 'r1133n1129', 'r1133n1128', 'r1133n1135', 'r1133n1134', 'r1133n1133', 'r1133n1132', 'r1133n1123', 'r1133n1122', 'r1133n1387', 'r1133n1386', 'r1133n1385'],
"rack_1132": ['r1132n4', 'r1132n5', 'r1132n2', 'r1132n3', 'r1132n0', 'r1132n1', 'r1132n14', 'r1132n15', 'r1132n1899', 'r1132n1898', 'r1132n1897', 'r1132n1896', 'r1132n1903', 'r1132n1902', 'r1132n1901', 'r1132n1900', 'r1132n1891', 'r1132n1890', 'r1132n1131', 'r1132n1130', 'r1132n1129', 'r1132n1128', 'r1132n1135', 'r1132n1134', 'r1132n1133', 'r1132n1132', 'r1132n1123', 'r1132n1122', 'r1132n1387', 'r1132n1386'],
"gpu_rack_1123" : ['r1123n7', 'r1123n4', 'r1123n5', 'r1123n2', 'r1123n3'],
"gpu_rack_1122" : ['r1122n7', 'r1122n4', 'r1122n5', 'r1122n2', 'r1122n3'],
"gpu_rack_1387" : ['r1387n7', 'r1387n4', 'r1387n5', 'r1387n2', 'r1387n3', 'r1387n0', 'r1387n1'],
"gpu_rack_1386" : ['r1386n7', 'r1386n4', 'r1386n5', 'r1386n2', 'r1386n3', 'r1386n0'],
"gpu_rack_1385" : ['r1385n7', 'r1385n4', 'r1385n5', 'r1385n2', 'r1385n3', 'r1385n0', 'r1385n1'],
"gpu_rack_1384" : ['r1384n4', 'r1384n5', 'r1384n2', 'r1384n3', 'r1384n0'],
"gpu_rack_1391" : ['r1391n7', 'r1391n4', 'r1391n5', 'r1391n2', 'r1391n3', 'r1391n0', 'r1391n1'],
"gpu_rack_1390" : ['r1390n7', 'r1390n4', 'r1390n5', 'r1390n2', 'r1390n3'],
"gpu_rack_1389" : ['r1389n7', 'r1389n4', 'r1389n5', 'r1389n2', 'r1389n3'],
"gpu_rack_1379" : ['r1379n7', 'r1379n4', 'r1379n5', 'r1379n2', 'r1379n3']
}

aggregate_per = {"hour": 3600 / 15, "day": 3600 * 24 / 15}

# combine all the metrics specified above into a larger dataframe for the given node
def get_metrics(path, node):
    metrics_values = {}
    for metric in metrics.keys():
        metric_df = read_parquet(path + "/" + metric)
        #print(metric_df)
        data_per_node = metric_df[node]
        # replace missing data with zeroes
        data_per_node[data_per_node == -1] = 0
        # let's aggregate the data
        agg_interval = aggregate_per["hour"]
        # make the epoch time a column
        data_per_node = data_per_node.reset_index()
        # make the epoch time a datetime
        data_per_node["time"] = pd.to_datetime(data_per_node["time"], unit = "s")
        data_per_node = data_per_node.set_index("time")
        #data_per_node = data_per_node.groupby([data_per_node.index.month, data_per_node.index.day, data_per_node.index.hour]).max()
        data_per_node = data_per_node.groupby([data_per_node.index.month, data_per_node.index.day]).max()
        #df = pd.DataFrame(data_per_node.to_records())
        #print(data_per_node)
        #data_per_node = data_per_node.groupby(data_per_node.time.dt.time).median()
        #print(len(data_per_node))
        #print(data_per_node)
        #:data_per_node = data_per_node / np.max(data_per_node)
        #print("{}: mean = {}, median = {}, min = {}, max = {}".format(metric, np.mean(data_per_node), np.median(data_per_node), np.min(data_per_node), np.max(data_per_node)))
        metrics_values[metric] = data_per_node
    return metrics_values
    
# read data from parquet files
def read_parquet(path):
    file_name = glob.glob(path + "/*.parquet")[0]
    #print(file_name)
    table = pq.read_table(file_name)
    return table.to_pandas()    

# draw a given metric
def draw_metric(ax, metric_value, metric, node):
    #for x, y, z in metric_value[node].index:
    #    print(x, y, z)

    ax_time = ["{}/{}/2020".format(y,x) for x,y in metric_value[node].index]
    i = 0
    ticks = []
    labels = []
    while i < len(metric_value[node].index):
        ticks.append(i)
        labels.append(ax_time[i])
        i += 30 # we want to have ticks every 2 weeks or so
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)

    #ax.set_ylim(-0.09, 1.1)
    ax.set_title(metric) 
    #print(metric_value[node].values)
    ax.plot(metric_value[node].values, rasterized=True)

# plot all metrics and save into a pdf file
def plot_metrics(metrics_values, node, ax):
    i = 0
    #plt.locator_params(axis='x', nticks=10)
    for metric, name in metrics.items():
        draw_metric(ax, metrics_values[metric], name, node)
        i += 1
 
# draw figures for a given rack
def draw_rack(rack, nodes):
    fig, ax = plt.subplots(nrows = len(metrics.keys()), ncols = 1, figsize = (10, len(metrics.keys()) * 2))
    metrics_arr = []
    for node in nodes:
        metrics_values = get_metrics("/var/scratch/aua400/encryptedParq/pqEncrypted/", node)
        metrics_arr.append(metrics_values["surfsara_ambient_temp"][node].values)

    rack_df = pd.DataFrame(metrics_arr)
    rack_df = rack_df.loc[:, (rack_df != 0).any(axis = 0)]
    rack_df = rack_df.replace(0, np.nan)
    print(rack_df)

    crnt_max = np.max(rack_df.max())
    crnt_min = np.min(rack_df.min())
    step = (crnt_max - crnt_min) / 5  
    labels = np.arange(crnt_min, crnt_max, step)  

    print(crnt_min, crnt_max)

    myColors = ("royalblue", "cornflowerblue", "mistyrose", "tomato", "red")
    cmap = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))

    heatmap = sns.heatmap(data = rack_df, cmap=cmap, vmin=crnt_min-0.1, vmax=crnt_max+0.1)
    colorbar = heatmap.collections[0].colorbar

    
    colticks = labels #[25.75, 27.2, 28.9, 30.6, 32.3, 34]
    
    colorbar.set_ticks(colticks)
    colorbar.set_ticklabels(list(map(str,colticks)))


    heatmap.set_xlabel("Time [days]")
    heatmap.set_ylabel("Node in Rack\n(increasing distance to floor)")
    heatmap.set_yticklabels(nodes, rotation=0)

    plt.tight_layout()
    #plt.savefig("node-" + node + ".pdf", format="pdf", dpi=300, bbox_inches="tight")
    plt.savefig("maxtemp-rack-" + rack + ".pdf", format="pdf", dpi=300, bbox_inches="tight")
    plt.close()

for rack, nodes in racks.items():
    print(rack, nodes)
    draw_rack(rack, nodes)


