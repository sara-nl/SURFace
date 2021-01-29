import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns

SHOW_PLOT = False
DAS_PATH = "/var/scratch/lvs215/processed-surf-dataset/"
SAVEFIG_PATH= "/home/cmt2002/surf-rack-plots/"
FIGNAME = "rack_boxplots"

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


def rack_violinplot(ax, df_covid, df_non_covid, ylabel):
    rack_nodes = get_rack_nodes(df_non_covid) # To get the rack nodes
    rack_values = list()
    rack_names = list()
    box_width = 0.65
    
    for rack, columns in rack_nodes.items():
        arr_covid = get_custom_values(df_covid[list(columns)])
        arr_non_covid = get_custom_values(df_non_covid[list(columns)])
        rack_values.append(arr_covid)
        rack_values.append(arr_non_covid)
        rack_names.append(rack)
        
    sns.boxplot(data=rack_values, ax=ax, fliersize=3, width=box_width, palette=['lightcoral', 'steelblue'] * (int(len(rack_values)/2)))
    ax.set_ylabel(ylabel,fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.tick_params(axis='both', which='minor', labelsize=14)
    ax.set_xticks([i + 0.5 for i in range(0, len(rack_values), 2)])

    # For load1, depict the values that exceed 100 load
    #if ylabel == "Load1":
        #ax.set_ylim(0, 10000)
        #for index, val in enumerate(rack_values):
            #max_val = np.amax(val)
            #if max_val > 10000:
                #ax.text(x=index-0.2, y=10010, s=str(round(max_val, 1)), fontsize=12, color="black", va="center")

    #else:
    ax.set_ylim(0, )
    
    if ylabel == "RAM Utilization [%]":
        ax.yaxis.set_label_coords(-0.075, 0.6)
    else:
        ax.yaxis.set_label_coords(-0.075, 0.5)
    
    ax.axvline(x=19.5, c="green", lw=2)
    ax.set_xticklabels(
        rack_names,
        ha='center', fontsize=16
    )
    for i in range(0, len(rack_values), 2):
        ax.axvline(i + 1.5, lw=1, ls='dashed')

def rack_analysis_violinplot(df_dic, ax, ylabel):
    rack_violinplot(
        ax=ax,
        df_covid=df_dic["covid"],
        df_non_covid=df_dic["non_covid"],
        ylabel=ylabel)

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


_, (ax_ram, ax_power, ax_temp, ax_load) = plt.subplots(4, 1, figsize=(11, 9), constrained_layout=True, sharex=True)
rack_analysis_violinplot(
    df_dic={"covid": df_power_covid, "non_covid": df_power_non_covid},
    ax=ax_power,
    ylabel="Power Consumption [W]")

rack_analysis_violinplot(
    df_dic={"covid": df_temp_covid, "non_covid": df_temp_non_covid},
    ax=ax_temp,
    ylabel="Temperature [C]")

rack_analysis_violinplot(
    df_dic={"covid": df_load_covid, "non_covid": df_load_non_covid},
    ax=ax_load,
    ylabel="Load1")

rack_analysis_violinplot(
    df_dic={"covid": df_ram_covid, "non_covid": df_ram_non_covid},
    ax=ax_ram,
    ylabel="RAM Utilization [%]")

ax_load.set_xlabel("Racks", fontsize=16)

# Depict legend on top of the first plot
lightcoral_patch = mpatches.Patch(color='lightcoral', label='covid (left)')
steelblue_patch = mpatches.Patch(color='steelblue', label='non-covid (right)')
ax_ram.legend(handles=[lightcoral_patch, steelblue_patch], loc="center", bbox_to_anchor=(0.5, 1.1), fontsize=14,
          ncol=2)

plt.savefig((SAVEFIG_PATH + FIGNAME + ".png"), dpi=200)
if SHOW_PLOT:
    plt.show()
plt.pause(0.0001)


print("DONE!")
