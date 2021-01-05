import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys

"""
    This script is used to produce the violin plots for the surfing article and the Mehmet's research project.
    The differences made between figures are:
        1. The x parameter in the ax.text() function to adjust the position of the max PDF value.
        2. The parameters passed to the set_ylim has changed depending on the metric.
"""


DAS_PATH = "/var/scratch/lvs215/processed-surf-dataset/"

metric = sys.argv[1]
ylabel = ""
title = ""

WIDTH = 5
HEIGHT = 11

if metric == "node_memory_MemFree":
    df_total = pd.read_parquet(DAS_PATH + "node_memory_MemTotal")
    df_free = pd.read_parquet(DAS_PATH + "node_memory_MemFree")
    df = 100 * (1 - (df_free / df_total)) # Utilization fraction
    # df = (df_total - df_free) / (1024 * 1024 * 1024)
    ylabel = "RAM Utilization [%]"
    title = ""

elif metric == "node_load1":
    df = pd.read_parquet(DAS_PATH + metric)
    ylabel = "Load1"
    title = ""

elif metric == "surfsara_ambient_temp":
    df = pd.read_parquet(DAS_PATH + metric)
    ylabel = "Temperature [C]"
    title = ""

elif metric == "surfsara_power_usage":
    df = pd.read_parquet(DAS_PATH + metric)
    ylabel = "Power consumption [W]"
    title = ""

else:
    print("Select node_load1, surfsara_ambient_temp, surfsara_power_usage, or node_memory_MemFree")
    exit(1)


#%% Helper functions
def covid_non_covid(df):
    if df.index.dtype == "int64":
        df.index = pd.to_datetime(df.index, unit='s')

    covid_df = df.loc['2020-02-27 00:00:00' :, :]
    non_covid_df = df.loc[: '2020-02-26 23:59:45', :]
    covid_df.reset_index()
    non_covid_df.reset_index()
    return covid_df, non_covid_df

def get_custom_values(df):
    values = np.array([])
    for column in df.columns:
        arr = df[column].values
        mask = (np.isnan(arr) | (arr < 0))
        
        arr = np.round(arr[~mask], 1)  # Filter out NaN values and less than 0 and round the values for ram utilization
        values = np.append(values, arr)
    return values

def get_max_pdf(df):
    def normalize(df):
        df = df.value_counts(sort=False, normalize=True).rename_axis('target').reset_index(name='pdf')
        df["cdf"] = df["pdf"].cumsum()
        return df
        
    df_new = normalize(pd.DataFrame(df))
    index_max_pdf = df_new["pdf"].idxmax()
    max_value = df_new.iloc[index_max_pdf]
    return (max_value["pdf"], max_value["target"])

df_covid, df_non_covid = covid_non_covid(df)
savefig_title = metric + "_cluster_violinplot.pdf"

df_covid_vals = get_custom_values(df_covid)
df_non_covid_vals = get_custom_values(df_non_covid)


def plot_violin(covid_val, non_covid_val, ax, title, ylabel):
    sns.violinplot(
        data=[covid_val, non_covid_val], 
        palette=["lightcoral", "steelblue"],
        ax=ax, width=0.95, cut=0)

    ax.set_ylabel(ylabel, fontsize=22)
    ax.tick_params(axis='both', which='major', labelsize=20)
    ax.tick_params(axis='both', which='minor', labelsize=20)
    ax.text(x=0-0.45, y=int(get_max_pdf(covid_val)[1]), s="{:.2f}".format(get_max_pdf(covid_val)[0]), fontsize=15, color="black", va="center")
    ax.text(x=1-0.56, y=int(get_max_pdf(non_covid_val)[1])+1, s="{:.2f}".format(get_max_pdf(non_covid_val)[0]), fontsize=15, color="black", va="center")
    ax.set_xticks(np.arange(2))
    ax.set_ylim(0, )
    ax.set_xticklabels(
        ('covid', 'non-covid'),
       ha='center', fontsize=22
    )
    # Just for load1 plots
    #max_covid_val = np.max(covid_val)
    #max_non_covid_val = np.max(non_covid_val)
    
    #if max_covid_val > 50:
       # ax.text(x=0-0.07, y=51, s=str(max_covid_val), fontsize=15, color="black", va="center")
    #if max_non_covid_val > 50:
        # ax.text(x=1, y=51, s=str(max_non_covid_val), fontsize=15, color="black", va="center")


fig, ax = plt.subplots(figsize=(HEIGHT, WIDTH), constrained_layout=True)

plot_violin(covid_val=df_covid_vals, non_covid_val=df_non_covid_vals, ax=ax, title=title, ylabel=ylabel)
plt.savefig("/home/cmt2002/cluster_analysis/plots/" + savefig_title, dpi=100)

print("Done!")
