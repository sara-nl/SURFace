import sys
import time

import matplotlib
import numpy as np
import pandas as pd
import preserve

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import seaborn as sns
import scipy
import dask.dataframe as dd
from pyspark.sql import SparkSession
import databricks.koalas as ks

from datetime import datetime

data_locations = [
    "path to machine metric dataset/surfsara_power_usage/",
    "path to machine metric dataset/surfsara_ambient_temp/",
    "path to machine metric dataset/node_procs_running/",
    "path to machine metric dataset/node_memory_MemTotal%20-%20node_memory_MemFree%20-%20node_memory_Buffers%20-%20node_memory_Cached%20-%20node_memory_Slab%20-%20node_memory_PageTables%20-%20node_memory_SwapCached/",
    "path to machine metric dataset/node_load1/",
]

gpu_data_locations = [
    "nvidia_gpu_power_usage_milliwatts/",
    "nvidia_gpu_fanspeed_percent/",
]

value_names = [
        'power_usage',
        'temperature',
        'processes_running',
        'memory_used',
        'load1',
    ]


def wait_for_reservation(manager, timeout, reservation_id, quiet=True):
    pm = manager
    starttime = time.time()
    lasttime = starttime + int(timeout)

    waittime = 5
    timeswaited = 0

    while True:
        state = pm.fetch_reservation(reservation_id).state
        if state == "R":
            break

        curtime = time.time()
        maxwaittime = lasttime - curtime
        nextwaittime = int(min(maxwaittime, waittime))
        if nextwaittime <= 0:
            print("[%.1f] Current state: %s. Reached timeout." % (curtime, state))
            sys.exit("wait-for-reservation timed out")
        if not quiet:
            print("[%.1f] Current state: %s. Waiting %u more seconds." % (curtime, state, nextwaittime))
        time.sleep(nextwaittime)

        timeswaited += 1
        if timeswaited == 12:
            waittime = 10  # After a minute, decrease the polling frequency
        elif timeswaited == 36:
            waittime = 15  # After 5 minutes, decrease the polling frequency
        elif timeswaited == 76:
            waittime = 30  # After 15 minutes, decrease the polling frequency

cache_file = "./koalas_correlation_plot_joined_df"
if not os.path.exists(cache_file):
    if 'DAS5' in os.environ:  # If we want to execute it on the DAS-5 super computer
        if 'DEPLOYER_HOME' not in os.environ:
            print("NEED TO SET $DEPLOYER_HOME - see Tim Hegeman's DAS deploy script")
            exit(-2)

        try:
            reservation_manager = preserve.get_PreserveManager()
            reservation_id = reservation_manager.create_reservation(5, "48:00:00")
            wait_for_reservation(reservation_manager, 600, str(reservation_id), False)

            # Now start Hadoop and Spark
            os.system(
                "cd {}; ./deployer deploy --preserve-id {} -s env/das5-hadoop.settings hadoop 2.7.7 yarn_enable=false".format(
                    os.environ['DEPLOYER_HOME'], reservation_id))
            os.system("cd {}; ./deployer deploy --preserve-id {} -s env/das5-spark-numa.settings spark 3.0.0".format(
                os.environ['DEPLOYER_HOME'], reservation_id))

            master_node = reservation_manager.get_own_reservations()[reservation_id].assigned_machines[0]
            print("We are on DAS5, {0} is master.".format(master_node))
            spark = SparkSession.builder \
                .master("spark://" + master_node + ":7077") \
                .appName("SURF Data Analysis") \
                .config("spark.executor.memory", "30G") \
                .config("spark.executor.cores", "8") \
                .config("spark.executor.instances", "10") \
                .config("spark.driver.memory", "30G") \
                .config("spark.sql.execution.arrow.enabled", "true") \
                .config("spark.local.dir", "/tmp") \
                .getOrCreate()
        except:
            if spark: spark.stop()
            reservation_manager.kill_reservation(reservation_id)
    else:
        print("This cannot be run on a local node. If you want to connect a cluster, adjust the code.")
        exit(-3)

    try:
        dfs = []

        for index, location in enumerate(data_locations):
            df = ks.from_pandas(pd.read_parquet(location, engine='pyarrow'))
            
            if location == "path to machine metric dataset/node_memory_MemTotal%20-%20node_memory_MemFree%20-%20node_memory_Buffers%20-%20node_memory_Cached%20-%20node_memory_Slab%20-%20node_memory_PageTables%20-%20node_memory_SwapCached/":
                df = df / (1024 * 1024 * 1024) # TO GB
            
            df = df.reset_index().melt(id_vars=['index'], var_name="node", value_name=value_names[index])
            df = df.dropna(subset=[value_names[index]])
            dfs.append(df)

        # We merge all columns that we want to correlate into one dataframe, merging based on time and node.
        joined_df = dfs[0]
        for index in range(1, len(dfs)):
            joined_df = joined_df.merge(dfs[index], on=['index', 'node'], how='inner')

        joined_df = joined_df.drop(['index', 'node'], axis=1)

        # Drop all rows with a NaN value, numpy doesn't handle this stuff well.
        joined_df = joined_df.dropna()

        joined_df.to_parquet(cache_file)
    except:
        exit(-4)
    finally:
        # No matter what, error or success, we cancel the reservervation here as we are done with Spark.
        spark.stop()
        reservation_manager.kill_reservation(reservation_id)


def corrdot(x_series, y_series, **kwargs):
    # Check if we have cached the result prior, because computing the correlation is a heavy operation.
    coef_file = "./cache/{}_{}_correlations.csv".format(x_series.name, y_series.name)
    if not os.path.exists(coef_file):
        print("Computing correlations for " + coef_file)
        df = pd.read_parquet(cache_file,
                             columns=[x_series.name, y_series.name],
                             engine='pyarrow'
                             )

        correlations = [scipy.stats.pearsonr(df[x_series.name], df[y_series.name])[0],
                        scipy.stats.spearmanr(df[x_series.name], df[y_series.name])[0],
                        scipy.stats.kendalltau(df[x_series.name], df[y_series.name])[0],
                        ]

        del df
        with open(coef_file, "w") as file1:
            file1.write("|".join([str(x) for x in correlations]))
    else:
        with open(coef_file, "r") as file1:
            correlations = [float(x) for x in file1.readline().split("|")]

    # Plot the correlations using a scatterplot
    ax = plt.gca()
#     ax.set_axis_off()

    correlation_names = ["Pearson", "Spearman", "Kendall"]
    x = list(range(1, len(correlations) + 1))
    y = [.5] * len(correlations)

    step = 0.76 / float(2 * len(correlations) - 2)
    x_fraction = 0.13

    # Get a colormap for the inverval -1,1 as this is the min/max of the correlation values
    cmap = plt.cm.get_cmap('coolwarm')
    cNorm = plt.cm.colors.Normalize(vmin=-1, vmax=1)
    scalarMap = plt.cm.ScalarMappable(norm=cNorm, cmap=cmap)

    for index, corr_r in enumerate(correlations):
        font_size = abs(corr_r) * 18 + 15
        corr_text = f"{corr_r:2.2f}".replace("0.", ".")

        # Create a background rectangle to depict the color intensity of the correlation
        # As it's a patch, it's based on the percentage location in the plot.
        rgba = scalarMap.to_rgba(corr_r)

        # As we cannot use ax.transAxes with Rectangle, compute the bounds :(
        y_start, y_end = ax.get_ylim()
        x_start, x_end = ax.get_xlim()

        rect_x = (x_fraction - .15) * (x_end - x_start)
        rect_y = (y[index] - .11) * (y_end - y_start)
        rect_width = 0.29 * (x_end - x_start)
        rect_height = 0.24 * (y_end - y_start)

        rect = plt.Rectangle((rect_x, rect_y), rect_width, rect_height,
                             fill=True, color=rgba, alpha=0.5, zorder=0)
        ax.add_patch(rect)

        # Show the type of correlation and its value.
        # Make sure to use "axes fraction" so this code always work even when the axes range other than 0-1.
        ax.text(x_fraction, y[index] + .25, correlation_names[index], ha='center', va='top', fontsize=14,
                transform=ax.transAxes)
        ax.text(x_fraction, y[index], corr_text, ha='center', va='center', transform=ax.transAxes, fontsize=font_size)
        x_fraction = x_fraction + step

        # Add a visual devider between the groups
        if index < len(correlations) - 1:
            # ax.annotate("|", (x_fraction, y[index]), ha='center', va='center', xycoords="axes fraction", fontsize=25, color="lightgrey")
            x_fraction = x_fraction + step


def scatter_reg(x_series, y_series, **kwargs):
    ax = plt.gca()
    kwargs['color'] = "lightcoral"
    
    plot_cache = os.path.join("./cache", f"correlation_plot_scatter_reg_scatter_{x_series.name}_{y_series.name}.npy")
    print(plot_cache)
    
    if not os.path.exists(plot_cache):
        print("computing " + plot_cache)
        df = pd.read_parquet(cache_file,
                         columns=[x_series.name, y_series.name],
                         engine='pyarrow'
                         ).dropna()

        # Grab the actual data.
    #     print(x_series, y_series)
        x_series = df[x_series.name]
        y_series = df[y_series.name]

        df = df.groupby([x_series.name, y_series.name]).size().reset_index().rename(columns={0: 'count'})
        
        x_vals = df[x_series.name]
        y_vals = df[y_series.name]
        del df
        with open(plot_cache, 'wb') as plot_cache_file:
            np.save(plot_cache_file, x_vals)
            np.save(plot_cache_file, y_vals)
    else:
        with open(plot_cache, 'rb') as plot_cache_file:
            x_vals = np.load(plot_cache_file)
            y_vals = np.load(plot_cache_file)

    #         ax.scatter(df[x_series.name], df[y_series.name], df['count'])
    ax.scatter(x_vals, y_vals, **kwargs)

    ax.set_xlim(0)
    ax.set_ylim(0)
    ax.grid(True)

    # We then plot the regression line
    # Note: this probably can be computed using Dask arrays and apply_along_axis. Future work.
    plot_cache = os.path.join("./cache", f"correlation_plot_scatter_reg_plot_{x_series.name}_{y_series.name}.npy")
    
    if not os.path.exists(plot_cache):
        print("computing " + plot_cache)
        x_vals = np.unique(x_series)
        y_vals = np.poly1d(np.polyfit(x_series, y_series, 1))(x_vals)
        with open(plot_cache, 'wb') as plot_cache_file:
            np.save(plot_cache_file, x_vals)
            np.save(plot_cache_file, y_vals)
    else:
        with open(plot_cache, 'rb') as plot_cache_file:
            x_vals = np.load(plot_cache_file)
            y_vals = np.load(plot_cache_file)
    kwargs['color'] = "black"
    ax.plot(x_vals, y_vals, linewidth=3, **kwargs)


    del x_vals
    del y_vals
    del x_series
    del y_series


def run_distplot(series, **kwargs):
    kwargs['color'] = "lightcoral"
    print(series.name)
    
    ind = series[0]  # Hack to get the column index
    series = pd.read_parquet(cache_file,
                             columns=[columns[ind]],
                             engine='pyarrow'
                             )

    ax = plt.gca()
    #sns.distplot(series, ax=ax, kde_kws={"color": "k", "lw": 3}, color="lightcoral", **kwargs)
    sns.distplot(series, ax=ax, kde_kws={"color": "steelblue", "lw": 3}, **kwargs)
    ax.set_ylim(0,1)
    del series

plot_labels = {
    'power_usage': "Power Usage [W]",
    'temperature': "Temperature [" + u"\u00b0" + "C]",
    'processes_running': "Processes\nRunning",
    'memory_used': "Memory Used [GB]",
    'load1': "load1",
}

columns = list(dd.read_parquet(cache_file, engine='pyarrow').columns)
col_indices = list(range(len(columns)))
fake_df = pd.DataFrame([col_indices], columns=columns, dtype=np.int64)

sns.set(style='white', font_scale=1.4)
g = sns.PairGrid(fake_df, aspect=1.8, diag_sharey=False)
print("Producing scatter plots below the diagonal...")
g.map_lower(scatter_reg, rasterized=True)
print("Generating histograms on the diagonal (distplots)...")
g.map_diag(run_distplot)
print("Creating correlation coefficients for above the diagonal...")
g.map_upper(corrdot, rasterized=True)

print("Done with creating the plot. Setting x labels now." )
# Set the correct labels
for i in range(5):
    for j in range(5):
        xlabel = g.axes[i][j].get_xlabel()
        ylabel = g.axes[i][j].get_ylabel()
        if xlabel in plot_labels.keys():
            g.axes[i][j].set_xlabel(plot_labels[xlabel], fontsize=16)
        if ylabel in plot_labels.keys():
            g.axes[i][j].set_ylabel(plot_labels[ylabel], fontsize=16, labelpad=20)
            # Align the labels on the yaxis
            g.axes[i][j].yaxis.set_label_coords(-.25, 0.5)

fig = g.fig
fig.tight_layout()
date_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

print("Writing plot to file.")
# a pdf would be 400-500mb at least, use png.
fig.savefig("pearson_correlation_plot_{}_{}.png".format("-".join(value_names), date_time))
fig.savefig("pearson_correlation_plot_{}.pdf".format("-".join(value_names)))
print("done")

del g
