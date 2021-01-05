import matplotlib.pyplot as plt
import os
from pathlib import Path
import numpy as np
import pandas as pd

TOOL_PATH = Path(os.path.abspath(__file__)).parent.parent


class GenerateTable:
    def __init__(self, savefig_title, title, **kargs):

        self.savefig_title = savefig_title
        self.title = title
        self.period = kargs['period'] if kargs['period'] else print("No period specified")
        if self.period == "FULL":
            self.timestamp = " full season "
        elif self.period == None:
            self.timestamp = ""
        else:
            self.timestamp = str(" " + self.period[0].strftime("%Y-%m-%d") + " to " + self.period[1].strftime("%Y-%m-%d")) 

    
    def default_table(self, df_dict):
        fig, ax = plt.subplots(2, 2) # Two tables: 1 for cpu 1 for gpu nodes
        df_cpu_covid_vals = self.__get_values(df_dict['df_cpu_covid'])
        df_gpu_covid_vals = self.__get_values(df_dict['df_gpu_covid'])
        df_cpu_non_covid_vals = self.__get_values(df_dict['df_cpu_non_covid'])
        df_gpu_non_covid_vals = self.__get_values(df_dict['df_gpu_non_covid'])

        df = pd.DataFrame(
            index=["cpu covid", "cpu non-covid", "gpu covid", "gpu non-covid"], 
            data=[df_cpu_covid_vals, df_cpu_non_covid_vals, df_gpu_covid_vals, df_gpu_non_covid_vals]
        )
        self.__create_table(ax, df, title=self.title + " " + self.timestamp)

        # Save figure and show
        self.savefig_title = "default_" + self.savefig_title + "table"
        plt.savefig(os.path.join(str(TOOL_PATH) + "/plots" + self.savefig_title + ".pdf"), dpi=100) 
        plt.show()

    # Custom analysis where period, nodes, or rack is specified
    def custom_table(self, df_dict):

        df_keys = []
        # Get the df keys passed
        for k in df_dict:
            if df_dict[k] != None:
                df_keys.append(k)

        # Nodes specified: Custom nodes; Custom period
        if 'df_custom' in df_keys:
            df = df_dict['df_custom'][0]
            df.sort_index(inplace=True)

            fig, ax = plt.subplots(1, 1, sharex=True, constrained_layout=True)
            self.__create_table(ax, df, title=self.title + " custom nodes " + self.timestamp)

        # Nodes covid non covid
        elif 'df_covid' in df_keys:
            df_covid = df_dict['df_covid'][0]
            df_non_covid = df_dict['df_non_covid'][0]
            
            fig, (ax_covid, ax_non_covid) = plt.subplots(2, 1, sharex=True, constrained_layout=True, figsize=(20, len(df_covid.columns)/2)) # Two tables for covid vs non-covid
            self.__create_table(ax_covid, df_covid, title=self.title + " custom nodes " + "covid period")
            self.__create_table(ax_non_covid, df_non_covid, title=self.title + " custom nodes " + "non-covid period")

        # Rack specified with custom period
        elif 'df_rack' in df_keys:
            df_rack = df_dict['df_rack'][0]
            df_rack.sort_index(inplace=True)
            rack_name = df_rack.columns[0].split("n")[0]
            
            fig, ax = plt.subplots(1, 1, sharex=True, constrained_layout=True)
            self.__create_table(ax, df_rack, title=self.title + " rack " + rack_name + " " + self.timestamp)

        # Rack specified with covid vs non-covid
        elif 'df_rack_covid' in df_keys:
            df_rack_covid = df_dict['df_rack_covid'][0]
            df_rack_non_covid = df_dict['df_rack_non_covid'][0]
            rack_name = df_rack_covid.columns[0].split("n")[0]

            fig, (ax_covid, ax_non_covid) = plt.subplots(1, 2, constrained_layout=True, figsize=(20, len(df_rack_covid.columns)/2))
            self.__create_table(ax_covid, df_rack_covid, title=self.title + " rack " + rack_name + " covid")
            self.__create_table(ax_non_covid, df_rack_non_covid, title=self.title + " rack " + rack_name + " non-covid")

        # Custom period; nodes are default CPU vs GPU
        elif 'df_cpu' in df_keys:
            df_cpu = df_dict['df_cpu'][0]
            df_gpu = df_dict['df_gpu'][0]

            fig, (ax_cpu, ax_gpu) = plt.subplots(1, 2, constrained_layout=True, figsize=(20, 40)) # Two tables: 1 for cpu 1 for gpu nodes
            self.__create_table(ax_cpu, df_cpu, title=self.title +  " CPU nodes " + self.timestamp)
            self.__create_table(ax_gpu, df_gpu, title=self.title + " GPU nodes " + self.timestamp)

        # Save figure and show
        self.savefig_title = self.savefig_title + "table"
        plt.savefig(os.path.join(str(TOOL_PATH) + "/plots" + self.savefig_title + ".pdf"), dpi=100) 
        plt.show()

    ## private functions
    def __create_table(self, ax, df, title):

        col_headers = ["Node", "Mean", "Median", "Min", "Max", "Std"]
        cell_text = list()
        for node in df.columns:
            curr = df[node]
            text = [str(round(val, 1)) for val in [curr.mean(), curr.median(), curr.min(), curr.max(), curr.std()]]
            cell_text.append([node] + text)

        ax.set_axis_off()
        table = ax.table(
            cellText=cell_text,
            colColours=["orange"] + ["blue"] * 5,
            colLabels=col_headers,
            cellLoc='center',
            loc='upper left')

        # color the column headers to white
        for i in range(len(col_headers)):
            table._cells[(0, i)]._text.set_color("#FFFFFF")

        table.scale(2, 2.5)
        table.auto_set_column_width(col=range(0, 6))
        table.set_fontsize(24)
        ax.set_title(title, fontsize=24)
        ax.axis("off")

    def __get_values(self, df):
        values = np.array([])
        for column in df.columns:
            arr = df[column].values
            mask = (np.isnan(arr) | (arr < 0))
            arr = arr[~mask]  # Filter out NaN values and less than 0
            values = np.append(values, arr)

        return values