import sys, os, datetime
import pandas as pd
from pathlib import Path
import argparse
import time

curr_path = os.getcwd() + '/surfsara-tool'
sys.path.insert(1, curr_path + '/parser')
sys.path.insert(2, curr_path + '/analysis')
sys.path.insert(3, curr_path)

from parse_parquet import ParseParquet
from parse_argument import ParseArgument
from analyze_metrics import Metric

"""
analysis --period="FULL_DATASET" --source:"cpu"
"""


"""
    Covid: [27th of February - End of the current dataset]
    NON-COVID: [Start of the current dataset - 26th of February]
"""


# TODO: find a better place to carry this function
def get_dataset_path(path):
    if path[-1] != '/':
        return path + '/'
    return path


# Get the command line arguments and pass them for through analysis
def main():

    args = ParseArgument().get_args() # Get the arguments from the command line

    # Get the dataset path, parse the data to 2 dictionaries containing node and gpu parquet paths
    dataset_path = get_dataset_path(args.path)
    new_node_parquets = ParseParquet(dataset_path).get_parquets()
    metric = Metric(new_node_parquets)

    # Get start and endtime
    period = args.periodname[0]
    nodes = args.nodenames
    racks = args.racknames

    metric1, metric2 = "", ""
    if len(args.metricname) == 2:
        metric1 = args.metricname[0]
        metric2 = args.metricname[1]
    else:
        metric1 = args.metricname[0]

    metric_name = " ".join(metric1.split("_")[1:])
    custom_analysis = False if period == "" and nodes == [] and racks == "" else True

    if nodes != [] and racks != "":
        print("Racks and nodes can't be analyzed at once.")
        exit(1)

    print("Please wait, as we are analyzing %s..." % metric_name)
    if custom_analysis: 
        print("Custom analysis: ")
        #metric.custom(metric1, second_parquet=metric2, nodes=nodes, racks=racks, period=period).entire_period_analysis()
        #metric.custom(metric1, second_parquet=metric2, nodes=nodes, period=period, racks=racks).hourly_seasonal_diurnal_pattern()
        #metric.custom(metric1, second_parquet=metric2, nodes=nodes, period=period, racks=racks).daily_seasonal_diurnal_pattern()
        metric.custom(metric_parquet, second_parquet=metric2, nodes=nodes, racks=racks, period=period).all_analysis()
        # metric.custom(metric_parquet, second_parquet=None, nodes=nodes, period=period, racks=racks).cdf()
       # metric.custom(metric1, second_parquet=metric2, nodes=nodes, racks=racks, period=period).all_analysis()
    # Default covid vs non-covid analysis
    else: 
        print("Default analysis (covid vs non-covid): ")
        #metric.default(metric1, second_parquet=metric2).rack_analysis()
        metric.default(metric1, second_parquet=metric2).all_analysis()
        #metric.default(metric1, second_parquet=metric2).hourly_seasonal_diurnal_pattern()
    
    print("Done!")
    exit(0)


if __name__ == "__main__":
    main()
