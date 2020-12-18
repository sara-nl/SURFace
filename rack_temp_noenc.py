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


racks = {
"rack_10" : ["r10n" + str(i) for i in range(1,33)], 
"rack_11": ["r11n" + str(i) for i in range(1,33)],
"gpu_rack_32": ["r32n" + str(i) for i in range(1,8)],
"gpu_rack_31": ["r31n" + str(i) for i in range(1,7)],
"gpu_rack_30" : ["r30n1", "r30n2", "r30n3", "r30n4", "r30n5", "r30n6", "r30n7"],
"gpu_rack_34" : ["r34n1", "r34n2", "r34n3", "r34n4", "r34n5", "r34n6", "r34n7"],
"gpu_rack_33" : ["r33n2", "r33n3", "r33n4", "r33n5", "r33n6"],
}

aggregate_per = {"hour": 3600 / 15, "day": 3600 * 24 / 15}

# combine all the metrics specified above into a larger dataframe for the given node
def get_metrics(path, node):
    metrics_values = {}
    for metric in metrics.keys():
        metric_df = pd.read_parquet(path = path + "/" + metric + "/", engine = "pyarrow")
        # get data per node
        data_per_node = metric_df[node]
        # let's aggregate the data
        agg_interval = aggregate_per["hour"]
        # make the epoch time a column
        data_per_node = data_per_node.reset_index()
        # make the epoch time a datetime
        data_per_node["time"] = pd.to_datetime(data_per_node["index"], unit="s")
        # re-index per time
        data_per_node = data_per_node.set_index("time")
        data_per_node = data_per_node.groupby([data_per_node.index.month, data_per_node.index.day]).max()
        # save the metrics data
        metrics_values[metric] = data_per_node
    return metrics_values

# draw a given metric
def draw_metric(ax, metric_value, metric, node):

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
        metrics_values = get_metrics("/var/scratch/lvs215/processed-surf-dataset/", node)
        metrics_arr.append(metrics_values["surfsara_ambient_temp"][node].values)

    rack_df = pd.DataFrame(metrics_arr)
    rack_df = rack_df.loc[:, (rack_df != 0).any(axis = 0)]
    rack_df = rack_df.replace(0, np.nan)
    #print(rack_df)

    crnt_max = 35 #np.max(rack_df.max())
    crnt_min = 20 #np.min(rack_df.min())
    step = (crnt_max - crnt_min) / 5  
    labels = np.arange(crnt_min, crnt_max, step)  

    #print(crnt_min, crnt_max)

    myColors = ("royalblue", "cornflowerblue", "mistyrose", "tomato", "red")
    cmap = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))

    heatmap = sns.heatmap(data = rack_df, cmap=cmap, vmin=crnt_min-0.3, vmax=crnt_max+0.3)
    colorbar = heatmap.collections[0].colorbar

    
    intticks = [20, 23, 26, 29, 32, 35]
    colticks = [str(s) + u"\u00b0"+"C" for s in intticks]
    print (colticks)

    colorbar.set_ticks(intticks)
    colorbar.set_ticklabels(list(map(str,colticks)))


    heatmap.set_xlabel("Time [days]")
    heatmap.set_xticks(np.arange(0, 243, 30))
    heatmap.set_xticklabels(np.arange(0, 243, 30), rotation=0)
    heatmap.set_ylabel("Node in Rack\n(increasing distance to floor)")
    heatmap.set_yticklabels(nodes, rotation=0)

    plt.tight_layout()
    #plt.savefig("node-" + node + ".pdf", format="pdf", dpi=300, bbox_inches="tight")
    plt.savefig("maxtemp-rack-" + rack + ".pdf", format="pdf", dpi=300, bbox_inches="tight")
    plt.close()

for rack, nodes in racks.items():
    draw_rack(rack, nodes)


