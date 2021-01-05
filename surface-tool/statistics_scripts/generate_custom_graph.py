import matplotlib.pyplot as plt
import sys, os
from pathlib import Path
import matplotlib.pylab as pylab
import numpy as np
import pandas as pd
import datetime

curr_path = os.getcwd() + '/surfsara-tool'
sys.path.insert(1, curr_path + '/parser')
sys.path.insert(2, curr_path + '/statistics_scripts')
sys.path.insert(3, curr_path + '/analysis')

# Configure label sizes of graphs
params = {
    'xtick.labelsize':16,
    'ytick.labelsize':16,
    'axes.labelsize':18,
    'figure.figsize': (10, 8),
    'savefig.format': 'pdf',
    'axes.titlesize': 20,
    'legend.loc': 'best',
    'legend.fontsize': "large"
}

pylab.rcParams.update(params)


DAY = 24
MID_DAY = int(DAY / 2)
WEEK = 7 * DAY
TOOL_PATH = Path(os.path.abspath(__file__)).parent.parent
MARKERS = ['s', '*', 'o', 'v', '<', 'p', '.', 'd']
COLORS = ['lightcoral', 'steelblue', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
SHOW_PLOT = False


class GenerateCustomGraph:

    def __init__(self, title, savefig_title, **kargs):
        self.title = title
        self.savefig_title = savefig_title
        self.ylabel = kargs['ylabel'] 
        self.period = kargs['period'] if kargs['period'] else print("")
        if self.period == "FULL":
            self.timestamp = ""
        elif self.period == None:
            self.timestamp = ""
        else:
            self.timestamp = str(" " + self.period[0].strftime("%Y-%m-%d") + " to " + self.period[1].strftime("%Y-%m-%d")) 

    #### PRIVATE FUNCTIONS ####
    def __save_formatted_fig(self, analysis_type):
        savefig_path = str(TOOL_PATH) + "/plots/" + self.savefig_title + analysis_type + ".pdf"
        plt.savefig(savefig_path, dpi=100)
        
    ############### CUSTOM ANALYSIS ###################
    def entire_period_analysis(self, df_dict):

        def get_converted_xticks(ax):
            return [pd.to_datetime(tick, unit='d').date().strftime("%d\n%b") for tick in ax.get_xticks()]

        def ax_components(ax):                
            # Set other features of plot
            ax.set_ylim(0, )
            ax.set_xlabel("2020")
            ax.set_ylabel(self.ylabel)
            ax.set_title(self.title + self.timestamp)
            ax.legend(loc="lower right", fontsize=16, markerscale=1.5)
            ax.set_xticklabels(labels=get_converted_xticks(ax))

        _, (ax) = plt.subplots( figsize=(18,10))
        df_keys = []

        # Get the df keys passed
        for k in df_dict:
            if df_dict[k] != None:
                df_keys.append(k)

        if 'df_rack_covid' in df_keys:
            print("no covid analysis for entire period")
            exit(1)

        # Nodes specified: Custom nodes; Custom period
        elif 'df_custom' in df_keys:
            df = df_dict['df_custom'][0] # Must remove the brackets by getting [0] of list
            df.index = pd.to_datetime(df.index, unit='s')
            df.sort_index(inplace=True)
            if "dt" in df.columns:
                del df["dt"]

            fig, ax_arr = plt.subplots(len(df.columns), 1, constrained_layout=True, figsize=(11, 5 * len(df.columns)))
            ax_arr = fig.axes

            for i in range(len(df.columns)):                
                curr_node = df.iloc[:, i:i+1]
                ax_arr[i].plot(curr_node, label=curr_node.columns[0], color=COLORS[i])
                print("VAL")
                print(curr_node.columns)
                mean_val = round(curr_node.mean(axis=0).values[0], 1)
                median_val = round(curr_node.median(axis=0).values[0], 1)
                #median_val2 = round(curr_node[curr_node.values > 0].median(axis=0).values[0],1)
                ax_arr[i].axhline(y=mean_val, c='green', ls='-', lw=2, label="mean (" + str(mean_val)+ ")")
                ax_arr[i].axhline(y=median_val, c=COLORS[1], ls='--', lw=2, label="median: (" + str(median_val) + ")")
                #print(curr_node.index)
                ax_arr[i].axvline(x=datetime.datetime.strptime('2020-02-27 00:00:00', '%Y-%m-%d %H:%M:%S'), c='skyblue', lw=1, ls='-')
                #ax_arr[i].axhline(y=median_val2, c='gray', ls='-', lw=4, label="median (zeros filtered): " + str(median_val2))
                ax_components(ax_arr[i])

               
         # Rack specified
        elif 'df_rack' in df_keys:
            df = df_dict['df_rack'][0]
            df.sort_index(inplace=True)
            df.index = pd.to_datetime(df.index, unit='s')

            df_aggr = df.aggregate(func=sum, axis=1) # Aggregate the nodes in the rack
            df_mean = df.mean(axis=1)

            col_len = len(df.columns) + 2 # Plus 2 is for 2 additional plots: Mean and Aggregate

            # Plot all the nodes in the rack + a graph for the mean of the rack and aggregated value
            fig, ax_arr = plt.subplots(col_len, 1, constrained_layout=True, figsize=(11, 5 * col_len))
            ax_arr = fig.axes

            ax_arr[0].plot(df_aggr, color=COLORS[1], label=str("Rack " + "aggregated load1"))
            ax_arr[1].plot(df_mean, color=COLORS[1], label=str("Rack " + "mean load1"))
            ax_components(ax_arr[0])
            ax_components(ax_arr[1])

            for i in range(2, col_len):                
                curr_node = df.iloc[:, i-2:i-1]
                ax_arr[i].plot(curr_node, label=str("Node " + curr_node.columns[0]), color=COLORS[i % len(COLORS)])
                mean_val = round(curr_node.mean(axis=0).values[0], 1)
                median_val = round(curr_node.median(axis=0).values[0], 1)
                median_val2 = round(curr_node[curr_node.values > 0].median(axis=0).values[0], 1)
                ax_arr[i].axhline(y=mean_val, c='black', ls=':', lw=4, label="mean: " + str(mean_val))
                ax_arr[i].axhline(y=median_val, c='black', ls='--', lw=4, label="median: " + str(median_val))
                ax_arr[i].axhline(y=median_val2, c='gray', ls='-', lw=4, label="median (zeros filtered): " + str(median_val2))
                ax_components(ax_arr[i])


        # Custom period; nodes are default CPU vs GPU
        elif 'df_cpu' in df_keys:
            df_cpu = df_dict['df_cpu'][0]
            df_gpu = df_dict['df_gpu'][0]

            df_cpu.index = pd.to_datetime(df_cpu.index, unit='s')
            df_gpu.index = pd.to_datetime(df_gpu.index, unit='s')

            # Pass the mean of the nodes
            df_cpu_mean = df_cpu.mean(axis=1)
            df_gpu_mean = df_gpu.mean(axis=1)

            ax.plot(df_cpu_mean, label="CPU", color=COLORS[0])
            ax.plot(df_gpu_mean, label="GPU", color=COLORS[1])
            ax_components(ax)

        # Period not specified
        elif 'df_covid' in df_keys:
            print("Not possible for this analysis type")
            

        # Nodes not specified
        elif 'df_cpu_covid' in df_keys:
            print("Not possible for this analysis type")
            

        
        self.__save_formatted_fig(analysis_type="entire_period")
        if SHOW_PLOT:
            plt.show()
        plt.pause(0.0001)

    def custom_daily_seasonal_diurnal_pattern(self, df_dict):
        def get_time_df(df):
            df["dt"] = pd.to_datetime(df.index, utc=True, unit="s")
            df["hour"] = df["dt"].dt.hour
            df["day"] = df["dt"].apply(lambda x: x.weekday())

            df = df.groupby(["day", "hour"]).mean()
            df.index = [hour for hour in range(0, 24*7)]
            return df

        def del_time_cols(df):
            if "hour" in df.columns:
                del df["hour"]
            if "day" in df.columns:
                del df["day"]
            df.reset_index()

        def ax_components(ax, subplot=""):
            ax.set_title(self.title + subplot + self.timestamp)
            ax.set_ylabel(self.ylabel)
            ax.set_ylim(0, )
            ax.set_xlabel("Days")
            ax.set_xticks([tick for tick in range(MID_DAY-1, WEEK, DAY)])
            ax.set_xticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
            ax.legend(loc="upper right", fontsize=18, markerscale=1.5)
            xcoords = [0] + [xcoord for xcoord in range(23, WEEK, DAY)]
            for xc in xcoords:
                ax.axvline(x=xc, color="gray", lw=0.5)

        df_keys = []

        # Get the df keys passed
        for k in df_dict:
            if df_dict[k] != None:
                df_keys.append(k)

        # Nodes specified: Custom nodes; Custom period
        if 'df_custom' in df_keys:
            df = df_dict['df_custom'][0]
            df.sort_index(inplace=True)
            df = get_time_df(df)
            
            fig, ax_arr = plt.subplots(len(df.columns), 1, figsize=(11, 5*len(df.columns)), sharex=True, constrained_layout=True)
            ax_arr = fig.axes

            for i in range(len(df.columns)):
                # Must remove the brackets by getting [0] of list
                curr_node = df.iloc[:, i:i+1]
                ax_arr[i].plot(curr_node, label=curr_node.columns[0], color=COLORS[i % len(COLORS)], marker=MARKERS[i])
                ax_components(ax_arr[i])

            del_time_cols(df)


        # Nodes covid non covid
        if 'df_covid' in df_keys:
            df_covid = df_dict['df_covid'][0]
            df_non_covid = df_dict['df_non_covid'][0]

            df_covid = get_time_df(df_covid)
            df_non_covid = get_time_df(df_non_covid)

            fig, ax_arr = plt.subplots(len(df_covid.columns), 1, constrained_layout=True)
            ax_arr = fig.axes

            for i in range(len(df_covid.columns)):
                ax_arr[i].plot(df_covid.iloc[:, i:i+1], label=df_covid.iloc[:, i:i+1].columns[0] + " covid", color=COLORS[0], marker=MARKERS[0])
                ax_arr[i].plot(df_non_covid.iloc[:, i:i+1], label=df_non_covid.iloc[:, i:i+1].columns[0] + " non-covid", color=COLORS[1], marker=MARKERS[1])
                ax_components(ax_arr[i])
            
            del_time_cols(df_covid)
            del_time_cols(df_non_covid)

        # Rack specified
        elif 'df_rack' in df_keys:
            df = df_dict['df_rack'][0]
            df.sort_index(inplace=True)        
            df = get_time_df(df)
            df_aggr = df.aggregate(func=sum, axis=1) # Aggregate the nodes in the rack

            col_len = len(df.columns) + 1 # Plus 1 is for 1 additional plot: Aggregate

            # Plot all the nodes in the rack + a graph for the mean of the rack and aggregated value
            fig, ax_arr = plt.subplots(col_len, 1, constrained_layout=True, figsize=(11, 5 * col_len))
            ax_arr = fig.axes

            ax_arr[0].plot(df_aggr, color=COLORS[1], label=str("Rack " + "aggregated load1"))
            ax_components(ax_arr[0])

            for i in range(1, col_len):                
                curr_node = df.iloc[:, i-1:i]
                ax_arr[i].plot(curr_node, label=str("Node " + curr_node.columns[0]), color=COLORS[i % len(COLORS)])
                ax_components(ax_arr[i])

            del_time_cols(df)
            
        elif 'df_rack_covid' in df_keys:
            df_covid = df_dict['df_rack_covid'][0]
            df_non_covid = df_dict['df_rack_non_covid'][0]

            df_rack_covid = get_time_df(df_covid)
            df_rack_non_covid = get_time_df(df_non_covid)

            df_covid_aggr = df_rack_covid.aggregate(func=sum, axis=1) # Aggregate the nodes in the rack 
            df_non_covid_aggr = df_rack_non_covid.aggregate(func=sum, axis=1) # Aggregate the nodes in the rack 

            col_len = len(df_covid.columns) + 1 # Plus 2 is for 2 additional plots: Aggregate covid and non-covid

            # Plot all the nodes in the rack + a graph for the mean of the rack and aggregated value
            fig, ax_arr = plt.subplots(col_len, 1, constrained_layout=True, figsize=(11, 5 * col_len))
            ax_arr = fig.axes

            ax_arr[0].plot(df_covid_aggr, color=COLORS[0], marker=MARKERS[0], label=str("Covid - rack " + df_covid.columns[0].split("n")[0]))
            ax_arr[0].plot(df_non_covid_aggr, color=COLORS[1], marker=MARKERS[1], label=str("Non-covid - rack " + df_covid.columns[0].split("n")[0]))
            ax_components(ax_arr[0], subplot=" aggregated values")

            for i in range(1, col_len):                
                curr_node_covid = df_rack_covid.iloc[:, i-1:i]
                curr_node_non_covid = df_rack_non_covid.iloc[:, i-1:i]

                ax_arr[i].plot(curr_node_covid, label=str("Covid - node " + curr_node_covid.columns[0]), color=COLORS[0], marker=MARKERS[0])
                ax_arr[i].plot(curr_node_non_covid, label=str("Non-covid - node " + curr_node_non_covid.columns[0]), color=COLORS[1], marker=MARKERS[1])
                ax_components(ax_arr[i])

            del_time_cols(df_rack_covid)
            del_time_cols(df_rack_non_covid)

        # Custom period; nodes are default CPU vs GPU
        elif 'df_cpu' in df_keys:
            df_cpu = df_dict['df_cpu'][0]
            df_gpu = df_dict['df_gpu'][0]

            df_cpu = get_time_df(df_cpu)
            df_gpu = get_time_df(df_gpu)

            df_cpu_aggr = df_cpu.aggregate(func=sum, axis=1)
            df_gpu_aggr = df_gpu.aggregate(func=sum, axis=1)

            _, ax = plt.subplots()  
            ax.plot(df_cpu_aggr, label="CPU", color=COLORS[2], marker=MARKERS[2])
            ax.plot(df_gpu_aggr, label="GPU", color=COLORS[3], marker=MARKERS[3])
            ax_components(ax)

            del_time_cols(df_cpu)
            del_time_cols(df_gpu)

        self.title += self.timestamp
        self.__save_formatted_fig(analysis_type="daily_seasonal_diurnal")
        if SHOW_PLOT:
            plt.show()
        plt.pause(0.0001)


    def custom_hourly_seasonal_diurnal_pattern(self, df_dict):

        def get_time_df(df):
            df["dt"] = pd.to_datetime(df.index, utc=True, unit="s")
            df["hour"] = df["dt"].dt.hour

            df = df.groupby("hour").mean()
            return df

        def del_time_cols(df):
            if "hour" in df.columns:
                del df["hour"]

        def ax_components(ax):
            ax.set_xticks([i for i in range(24)], minor=True)
            ax.tick_params('x', length=12, width=2, which='major')
            ax.tick_params('x', length=8, width=1, which='minor')
            ax.set_title(self.title + self.timestamp)
            ax.set_ylabel(self.ylabel)
            ax.set_ylim(0, )
            ax.set_xlabel("Hours")
            ax.legend(loc="upper right", fontsize=18, markerscale=1.5)

        df_keys = []

        # Get the df keys passed
        for k in df_dict:
            if df_dict[k] != None:
                df_keys.append(k)

        # Nodes specified: Custom nodes; Custom period
        if 'df_custom' in df_keys:
            df = df_dict['df_custom'][0]
            df.sort_index(inplace=True)

            df = get_time_df(df)
            
            fig, ax_arr = plt.subplots(len(df.columns), 1, figsize=(11, 5 * len(df.columns)), sharex=True, constrained_layout=True)
            ax_arr = fig.axes

            for i in range(len(df.columns)):
                # Must remove the brackets by getting [0] of list
                curr_node = df.iloc[:, i:i+1]
                ax_arr[i].plot(curr_node, label=curr_node.columns[0], color=COLORS[i], marker=MARKERS[i])
                ax_components(ax_arr[i])

            del_time_cols(df)

                # Nodes covid non covid
        elif 'df_covid' in df_keys:
            df_covid = df_dict['df_covid'][0]
            df_non_covid = df_dict['df_non_covid'][0]

            df_covid = get_time_df(df_covid)
            df_non_covid = get_time_df(df_non_covid)
            
            fig, ax_arr = plt.subplots(len(df_covid.columns), 1, figsize=(11, 5*len(df_covid.columns)), sharex=True, constrained_layout=True)
            ax_arr = fig.axes

            for i in range(len(df_covid.columns)):
                ax_arr[i].plot(df_covid.iloc[:, i:i+1], label=df_covid.iloc[:, i:i+1].columns[0] + " covid", color=COLORS[0], marker=MARKERS[0])
                ax_arr[i].plot(df_non_covid.iloc[:, i:i+1], label=df_non_covid.iloc[:, i:i+1].columns[0] + " non-covid", color=COLORS[1], marker=MARKERS[1])
                ax_components(ax_arr[i])

            del_time_cols(df_covid)
            del_time_cols(df_non_covid)

         # Rack specified
        elif 'df_rack' in df_keys:
            df = df_dict['df_rack'][0]
            df.sort_index(inplace=True)
            df = get_time_df(df)
            df_aggr = df.aggregate(func=sum, axis=1) # Aggregate the nodes in the rack
            df_mean = df.mean(axis=1)

            cols = len(df.columns) + 2
            # Plot all the nodes in the rack + a graph for the mean of the rack and aggregated value
            fig, ax_arr = plt.subplots(cols, 1, sharex=True, constrained_layout=True, figsize=(11, 5 * cols))
            ax_arr = fig.axes

            ax_arr[0].plot(df_aggr, color=COLORS[1], label=str("Rack " + df.columns[0].split("n")[0]) + " aggregated load1")
            ax_arr[1].plot(df_mean, color=COLORS[1], label=str("Rack " + df.columns[0].split("n")[0]) + " mean load1")
            ax_components(ax_arr[0])
            ax_components(ax_arr[1])

            for i in range(2, cols):                
                curr_node = df.iloc[:, i-2:i-1]
                ax_arr[i].plot(curr_node, label=curr_node.columns[0], color=COLORS[i % len(COLORS)])
                ax_components(ax_arr[i])

            del_time_cols(df)

        elif 'df_rack_covid' in df_keys:
            df_covid = df_dict['df_rack_covid'][0]
            df_non_covid = df_dict['df_rack_non_covid'][0]

            df_covid = get_time_df(df_covid)
            df_non_covid = get_time_df(df_non_covid)

            df_covid_aggr = df_covid.aggregate(func=sum, axis=1) # Aggregate the nodes in the rack 
            df_non_covid_aggr = df_non_covid.aggregate(func=sum, axis=1) # Aggregate the nodes in the rack 

            col_len = len(df_covid.columns) + 1 # Plus 1 is for 1 additional plot: Aggregate

            # Plot all the nodes in the rack + a graph for the mean of the rack and aggregated value
            fig, ax_arr = plt.subplots(col_len, 1, constrained_layout=True, figsize=(11, 5 * col_len))
            ax_arr = fig.axes

            ax_arr[0].plot(df_covid_aggr, color=COLORS[0], marker=MARKERS[0], label=str("Covid - rack " + df_covid.columns[0].split("n")[0]))
            ax_arr[0].plot(df_non_covid_aggr, color=COLORS[1], marker=MARKERS[1], label=str("Non-covid - rack " + df_covid.columns[0].split("n")[0]))
            ax_components(ax_arr[0])

            for i in range(1, col_len):                
                curr_node_covid = df_covid.iloc[:, i-1:i]
                curr_node_non_covid = df_non_covid.iloc[:, i-1:i]

                ax_arr[i].plot(curr_node_covid, label=str("Covid - node " + curr_node_covid.columns[0]), color=COLORS[0], marker=MARKERS[0])
                ax_arr[i].plot(curr_node_non_covid, label=str("Non-covid - node " + curr_node_non_covid.columns[0]), color=COLORS[1], marker=MARKERS[1])
                ax_components(ax_arr[i])

            del_time_cols(df_covid)
            del_time_cols(df_non_covid)

        # Custom period; nodes are default CPU vs GPU
        elif 'df_cpu' in df_keys:
            df_cpu = df_dict['df_cpu'][0]
            df_gpu = df_dict['df_gpu'][0]

            df_cpu = get_time_df(df_cpu)
            df_gpu = get_time_df(df_gpu)

            df_cpu = df_cpu.aggregate(func=sum, axis=1)
            df_gpu = df_gpu.aggregate(func=sum, axis=1)

            _, ax = plt.subplots()
            ax.plot(df_cpu, label="CPU", color=COLORS[2], marker=MARKERS[2])
            ax.plot(df_gpu, label="GPU", color=COLORS[3], marker=MARKERS[3])
            ax_components(ax)

            self.title += " CPU vs GPU nodes aggregated values "
            del_time_cols(df_cpu)
            del_time_cols(df_gpu)

        self.title += self.timestamp

        self.__save_formatted_fig(analysis_type="hourly_seasonal_diurnal")
        if SHOW_PLOT:
            plt.show()
        plt.pause(0.0001)

    def custom_cdf(self, df_dict):
        df_keys = []

        # Get all the values in the df
        def get_custom_values(df):
            values = np.array([])
            print(df.columns)
            for column in df.columns:
                arr = np.array(df[column].values)
                mask = (np.isnan(arr) | (arr < 0))
                arr = arr[~mask]  # Filter out NaN values and less than 0                                                                                    
                values = np.append(values, arr)

            return values

        def ax_components(ax):
            ax.set_title(self.title)
            ax.set_ylabel("Frequency")
            ax.set_xlim(0, )
            ax.set_xlabel(self.ylabel)
            ax.legend(loc='lower right', fontsize=18, markerscale=1.5)


        # Get the df keys passed
        for k in df_dict:
            if df_dict[k] != None:
                df_keys.append(k)

        # Nodes specified: Custom nodes; Custom period
        if 'df_custom' in df_keys:
            df = df_dict['df_custom'][0]
            df.sort_index(inplace=True)

            self.title += self.timestamp
            fig, ax_arr = plt.subplots(len(df.columns), 1, figsize=(11, len(df.columns)*5) , sharex=True, constrained_layout=True)
            ax_arr = fig.axes
            for i in range(len(df.columns)):
                # Must remove the brackets by getting [0] of list
                curr_node = df.iloc[:, i:i+1]
                ax_arr[i].hist(get_custom_values(curr_node), label=curr_node.columns[0], color=COLORS[i], density=True, histtype='step', bins=100, cumulative=True)
                ax_components(ax_arr[i])

        # Nodes covid non covid
        elif 'df_covid' in df_keys:
            df_covid = df_dict['df_covid'][0]
            df_non_covid = df_dict['df_non_covid'][0]
            
            fig, ax_arr = plt.subplots(len(df_covid.columns), 1, sharex=True, constrained_layout=True)
            ax_arr = fig.axes
            for i in range(len(df_covid.columns)):
                ax_arr[i].hist(get_custom_values(df_covid.iloc[:, i:i+1]), label=df_covid.iloc[:, i:i+1].columns[0] + " covid", color=COLORS[0], density=True, histtype='step', bins=100, cumulative=True)
                ax_arr[i].hist(get_custom_values(df_non_covid.iloc[:, i:i+1]), label=df_non_covid.iloc[:, i:i+1].columns[0] + " non-covid", color=COLORS[1], density=True, histtype='step', bins=100, cumulative=True)
                ax_components(ax_arr[i])

         # Rack specified
        elif 'df_rack' in df_keys:
            self.title += self.timestamp
            df = df_dict['df_rack'][0]
            df.sort_index(inplace=True)
            df_values = get_custom_values(df) # get all the values in df
            
            _, (ax_cdf, ax_hist) = plt.subplots(2, 1, constrained_layout=True)
            ax_cdf.hist(df_values, label=df.columns[0].split("n")[0], color=COLORS[0], density=True, histtype='step', bins=100, cumulative=True)
            ax_cdf.set_ylabel("Density")
            ax_hist.hist(df_values, bins=1000)
            ax_components(ax_cdf)
            ax_components(ax_hist)

        elif 'df_rack_covid' in df_keys:
            df_covid = df_dict['df_rack_covid'][0]
            df_non_covid = df_dict['df_rack_non_covid'][0]

            df_covid_values = get_custom_values(df_covid) # Aggregate the nodes in the rack 
            df_non_covid_values = get_custom_values(df_non_covid) # Aggregate the nodes in the rack 

            _, (ax_cdf, ax_covid, ax_non_covid) = plt.subplots(3, 1, constrained_layout=True)
            ax_cdf.hist(df_covid_values, label=df_covid.columns[0].split("n")[0] + " covid", color=COLORS[0], density=True, histtype='step', bins=100, cumulative=True)
            ax_cdf.hist(df_non_covid_values, label=df_non_covid.columns[0].split("n")[0] + " non-covid", color=COLORS[1], density=True, histtype='step', bins=100, cumulative=True)
            ax_cdf.set_ylabel("Density")
            ax_covid.hist(df_covid_values, label="covid", bins=1000)
            ax_non_covid.hist(df_non_covid_values, label="non-covid", bins=1000)
            ax_components(ax_cdf)
            ax_components(ax_covid)
            ax_components(ax_non_covid)

        # Custom period; nodes are default CPU vs GPU
        elif 'df_cpu' in df_keys:
            self.title += " CPU vs GPU nodes all values " + self.timestamp
            df_cpu = df_dict['df_cpu'][0]
            df_gpu = df_dict['df_gpu'][0]

            df_cpu = get_custom_values(df_cpu)
            df_gpu = get_custom_values(df_gpu)

            _, (ax_cdf, ax_cpu, ax_gpu) = plt.subplots(3, 1, constrained_layout=True)

            ax_cdf.hist(df_cpu, label="CPU", color=COLORS[2], density=True, bins=1000, histtype='step', cumulative=True)
            ax_cdf.hist(df_gpu, label="GPU", color=COLORS[3], density=True, bins=1000, histtype='step', cumulative=True)
            ax_cdf.set_ylabel("Density")
            ax_cpu.hist(df_cpu, label="CPU", bins=1000)
            ax_gpu.hist(df_gpu, label="GPU", bins=1000)
            ax_components(ax_cdf)
            ax_components(ax_cpu)
            ax_components(ax_gpu)

        self.title += self.timestamp
        self.__save_formatted_fig(analysis_type="cdf")
        if SHOW_PLOT:
            plt.show()
