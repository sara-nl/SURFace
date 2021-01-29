import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd


SHOW_PLOT = False
DAS_PATH = "/var/scratch/lvs215/processed-surf-dataset/"
SAVEFIG_PATH= "/home/cmt2002/surf-rack-plots/"
FIGNAME = "rack_barplots"

def get_rack_nodes(df):
    rack_nodes = {}

    for node in df.columns:
        rack = node.split("n")[0]
        if rack not in rack_nodes:
            rack_nodes[rack] = set()

        rack_nodes[rack].add(node)

    return rack_nodes

def get_custom_values(df):
    values = np.array([])
    for column in df.columns:
        arr = df[column].values
        mask = (np.isnan(arr) | (arr < 0))

        arr = arr[~mask]  # Filter out NaN values and less than 0
        values = np.append(values, arr)

    return values

def load1_rack_barplot(ax, df_covid, df_non_covid, subtitle):
    rack_nodes = get_rack_nodes(df_covid)  # Get the rack nodes
    index = 0
    w = 0.4
    bar_locs = []
    std_data = []
    bar_heights = []
    for rack, columns in rack_nodes.items():
        arr_covid = get_custom_values(df_covid[list(columns)])
        arr_non_covid = get_custom_values(df_non_covid[list(columns)])
        
        bar_locs.extend([index - w / 2, index + w / 2])
        bar_heights.extend([arr_covid.mean(), arr_non_covid.mean()])
        std_data.extend([arr_covid.std(), arr_non_covid.std()])
    
        if arr_covid.std() > 75:
            ax.text(x=index - (w / 2 + 0.23), y=78, s=str(round(arr_covid.std(), 1)), fontsize=14, color="black",
                    va="center")
        if arr_non_covid.std() > 75:
            ax.text(x=index + (w / 2 - 0.23), y=78, s=str(round(arr_non_covid.std(), 1)), fontsize=14, color="black",
                    va="center")

        index += 1

    ax.bar(x=bar_locs,
           height=bar_heights,
           width=w,
           align='center',
           yerr=[np.zeros(len(std_data)), std_data],
           color=["lightcoral", "steelblue"] * int(len(bar_heights) / 2),
           edgecolor='black',
           capsize=4)

    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.tick_params(axis='both', which='minor', labelsize=16)
    ax.set_ylabel("Load1", fontsize=16)
    ax.set_ylim(0, 75)
    ax.set_xlabel(subtitle, fontsize=18)
    ax.set_xticks(np.arange(len(rack_nodes.keys())))
    ax.set_xticklabels(rack_nodes.keys(), fontsize=18)
    ax.yaxis.set_label_coords(-0.06, 0.5)

def rack_barplot(ax, df_covid, df_non_covid, subtitle, ylabel):
    rack_nodes = get_rack_nodes(df_covid)  # Get the rack nodes
    index = 0
    w = 0.4
    bar_locs = []
    std_data = []
    bar_heights = []
    for rack, columns in rack_nodes.items():
        arr_covid = get_custom_values(df_covid[list(columns)])
        arr_non_covid = get_custom_values(df_non_covid[list(columns)])
        
        bar_locs.extend([index - w / 2, index + w / 2])
        bar_heights.extend([arr_covid.mean(), arr_non_covid.mean()])
        std_data.extend([arr_covid.std(), arr_non_covid.std()])
        
        index += 1
        
    ax.bar(x=bar_locs, 
           height=bar_heights, 
           width=w, 
           align='center',
           yerr=[np.zeros(len(std_data)), std_data], 
           color=["lightcoral", "steelblue"] * int(len(bar_heights) / 2),
           edgecolor='black',
           capsize=4)
        
        
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.tick_params(axis='both', which='minor', labelsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.set_ylim(0, )
    ax.set_xlabel(subtitle, fontsize=18)
    ax.set_xticks(np.arange(len(rack_nodes.keys())))
    ax.set_xticklabels(rack_nodes.keys(), fontsize=18)

    if ylabel == "RAM\nUtilization [%]":
        ax.yaxis.set_label_coords(-0.06, 0.67)
    if ylabel == "Power\nConsumption [W]":
        ax.yaxis.set_label_coords(-0.06, 0.56)
    if ylabel == "Temperature [C]":
        ax.yaxis.set_label_coords(-0.06, 0.36)


def rack_analysis_barplot(df_dic, ax, ylabel):
    rack_barplot(
        ax=ax,
        df_covid=df_dic["covid"],
        df_non_covid=df_dic["non_covid"],
        subtitle=None,
        ylabel=ylabel)
    ax.axvline(x=9.5, c="green", lw=1.5)

def load_rack_analysis_barplot(df_dic, ax):
    load1_rack_barplot(
        ax=ax,
        df_covid=df_dic["covid"],
        df_non_covid=df_dic["non_covid"],
        subtitle=None)
    ax.axvline(x=9.5, c="green", lw=1.5)

def covid_non_covid(df):
    if df.index.dtype == "int64":
        df.index = pd.to_datetime(df.index, unit='s')

    covid_df = df.loc['2020-02-27 00:00:00':, :]
    non_covid_df = df.loc[: '2020-02-26 23:59:45', :]
    covid_df.reset_index()
    non_covid_df.reset_index()
    return covid_df, non_covid_df

df_free = pd.read_parquet(DAS_PATH + "node_memory_MemFree")
df_total = pd.read_parquet(DAS_PATH + "node_memory_MemTotal")
df_ram_covid, df_ram_non_covid = covid_non_covid(100 * (1 - (df_free / df_total)))
df_load_covid, df_load_non_covid = covid_non_covid(pd.read_parquet(DAS_PATH + "node_load1"))
df_power_covid, df_power_non_covid = covid_non_covid(pd.read_parquet(DAS_PATH + "surfsara_power_usage"))
df_temp_covid, df_temp_non_covid = covid_non_covid(pd.read_parquet(DAS_PATH + "surfsara_ambient_temp"))


_, (ax_ram, ax_power, ax_temp, ax_load) = plt.subplots(4, 1, figsize=(11, 8), constrained_layout=True, sharex=True)
rack_analysis_barplot(
    df_dic={"covid": df_power_covid, "non_covid": df_power_non_covid},
    ax=ax_power,
    ylabel="Power\nConsumption [W]")
rack_analysis_barplot(
    df_dic={"covid": df_temp_covid, "non_covid": df_temp_non_covid},
    ax=ax_temp,
    ylabel="Temperature [C]")
load_rack_analysis_barplot(
    df_dic={"covid": df_load_covid, "non_covid": df_load_non_covid},
    ax=ax_load)
rack_analysis_barplot(
    df_dic={"covid": df_ram_covid, "non_covid": df_ram_non_covid},
    ax=ax_ram,
    ylabel="RAM\nUtilization [%]")

ax_load.set_xlabel("Racks")
ax_load.text(x=2.5, y=65, s="Generic nodes", fontsize=16)
ax_load.text(x=11.5, y=65, s="ML nodes", fontsize=16)
# Depict legend on top of the first plot
lightcoral_patch = mpatches.Patch(color='lightcoral', label='covid (left)')
steelblue_patch = mpatches.Patch(color='steelblue', label='non-covid (right)')
ax_ram.legend(handles=[lightcoral_patch, steelblue_patch], loc="center", bbox_to_anchor=(0.5, 1.15), fontsize=16,
          ncol=2)

plt.savefig((SAVEFIG_PATH + FIGNAME + ".pdf"), dpi=100)
if SHOW_PLOT:
    plt.show()
plt.pause(0.0001)


print("DONE!")
