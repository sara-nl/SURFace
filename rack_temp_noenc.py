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

plt.rcParams.update({'font.size': 18})

racks = {
"rack_10" : ["r10n" + str(i) for i in range(1,33)],
"gpu_rack_32": ["r32n" + str(i) for i in range(1,8)],
}

metrics = {"surfsara_ambient_temp": "Ambient Temperature"}

# combine all the metrics specified above into a larger dataframe for the given node
def get_metrics(path, node):
    metrics_values = {}
    for metric in metrics.keys():
        metric_df = pd.read_parquet(path = path + "/" + metric + "/", engine = "pyarrow")
        # get data per node
        data_per_node = metric_df[node]
        # reset the index
        data_per_node = data_per_node.reset_index()
        # make the epoch time a datetime
        data_per_node["time"] = pd.to_datetime(data_per_node["index"], unit="s")
        # re-index per date time
        data_per_node = data_per_node.set_index("time")
        # grab the max temperature per hour of day to plot it into the heatmap
        data_per_node = data_per_node.groupby([data_per_node.index.month, data_per_node.index.day]).max()
        # save the metrics data
        metrics_values[metric] = data_per_node
    return metrics_values

# draw figures for a given rack
def draw_rack(rack, nodes):
    fig, ax = plt.subplots(nrows = 1, ncols = 1, figsize = (12, 3.5))
    metrics_arr = []
    for node in nodes:
        metrics_values = get_metrics("/var/scratch/lvs215/processed-surf-dataset/", node)
        metrics_arr.append(metrics_values["surfsara_ambient_temp"][node].values)

    rack_df = pd.DataFrame(metrics_arr)
    rack_df = rack_df.loc[:, (rack_df != 0).any(axis = 0)]
    rack_df = rack_df.replace(0, np.nan)
    rack_df = rack_df.dropna(axis="columns", how="all")

    crnt_max = 35 #np.max(rack_df.max())
    crnt_min = 20 #np.min(rack_df.min())

    # custom colors for the heatmap
    myColors = ("royalblue", "cornflowerblue", "mistyrose", "tomato", "red")
    cmap = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))

    heatmap = sns.heatmap(data = rack_df, cmap=cmap, vmin=crnt_min-0.3, vmax=crnt_max+0.3)
    colorbar = heatmap.collections[0].colorbar

    # the following are degrees Celsius for the heatmap legend
    intticks = [20, 23, 26, 29, 32, 35]
    # add the Celsius symbol to the legend value
    colticks = [str(s) + u"\u00b0"+"C" for s in intticks]

    colorbar.set_ticks(intticks)
    colorbar.set_ticklabels(list(map(str,colticks)))

    heatmap.set_xlabel("Time [days]")
    heatmap.set_xticks(np.arange(0, 215, 30))
    heatmap.set_xticklabels(np.arange(0, 215, 30), rotation=0)
    heatmap.set_ylabel("Node in Rack\n(distance to floor\nincreasing)")
    heatmap.set_yticklabels(nodes, rotation=0)

    plt.tight_layout()
    plt.savefig("maxtemp-rack-" + rack + ".pdf", format="pdf", dpi=300, bbox_inches="tight")
    plt.close()

for rack, nodes in racks.items():
    draw_rack(rack, nodes)
