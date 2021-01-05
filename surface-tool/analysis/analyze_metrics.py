import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, sys, pyarrow
import seaborn as sns
from pathlib import Path
import calendar

curr_path = os.getcwd() + '/surfsara-tool'
sys.path.insert(1, curr_path + '/parse_metric')
sys.path.insert(2, curr_path + '/statistics_scripts')
sys.path.insert(3, curr_path + '/analysis')

from diurnal_analysis import DiurnalAnalysis
from parse_metric import ParseMetric
from custom_analysis import CustomAnalysis
from default_analysis import DefaultAnalysis

"""
    Analyze the following metrics:
        1. # of processes running-blocked
        2. file description allocation
        3. caches, 
        4. utilized main memory (RAM), 
        5. disk IO, read, and write time
        6. disk IO size [B] + breakdown per read/write,

    Split the metrics in terms of:
        1. Plot the entire set of nodes, which means no partition in nodes
        2. Split the nodes, CPU vs GPU

    Summarize data:
        1. counts
        2. basic statistics (mean, min, median, max, other quartiles, stddev, CoV if possible)
        3. meta-metric

    Diurnal Analysis:
        1. Hourly analysis:
            a. "Aggregated" over the entire period
            b. "Aggregated" per month 

            The hourly analysis allows us to see differences in office hours (9-5) vs non-office hours; 
            Did the covid period affect people’s working habits (did they do more outside office hours for example?)
        2. Daily analysis:
            a. "Aggregated" over the entire period
            b. "Aggregate" per month

        3. Workday vs weekend:
            a. "Aggregated" over the entire period
            b. "Aggregate" per month
        
        4. Monthly (seasonal patterns):
            a. aggregate all data per month (for each metric → one value per month, 
            or the basic statistics (mean, min, median, max, other quartiles, stddev, CoV if possible))

        5. Per node per metric create a plot to inspect per node.
        6. Inspect Eigen values per node/metric.


"""

TOOL_PATH = Path(os.path.abspath(__file__)).parent.parent


class Metric:

    def __init__(self, new_node_parquets: dict):
        self.new_node_parquets = new_node_parquets

    def custom(self, parquet, **kargs):
        second_parquet = kargs['second_parquet']
        nodes = kargs['nodes']
        period = kargs['period']
        racks = kargs['racks']
        return CustomAnalysis(node_parquets=self.new_node_parquets, 
                    parquet=parquet, second_parquet=second_parquet, 
                    racks=racks, nodes=nodes, period=period) 

    def default(self, parquet, **kargs):
        second_parquet = kargs['second_parquet']
        return DefaultAnalysis(self.new_node_parquets, parquet, second_parquet=second_parquet)

    @staticmethod
    def __get_parquet_path(metric, parq_dic):
        for key, value in parq_dic.items():
            if key == metric:
                return value

    @staticmethod
    def get_df(metric, parq_dic):
        """
        return the df for the corresponding "metric" from the "parquet dict"
        :param metric:
        :param parq_dic:
        :return:
        """
        path = Metric.__get_parquet_path(metric, parq_dic)
        return pd.read_parquet(path)







