import numpy as np
import sys, json, os, pyarrow

curr_path = os.getcwd() + '/surfsara-tool'
sys.path.insert(1, curr_path + '/parse_metric')
sys.path.insert(2, curr_path + '/statistics_scripts')
sys.path.insert(3, curr_path + '/analysis')

from diurnal_analysis import DiurnalAnalysis
from parse_metric import ParseMetric
from generate_default_graph import GenerateDefaultGraph
from generate_table import GenerateTable
import matplotlib.pyplot as plt 
import pandas as pd
from generate_dataset_page import GeneratePage


class DefaultAnalysis(object):

    def __init__(self, node_parquets, parquet, **kargs):
        from analyze_metrics import Metric # Prevents circular error

        self.node_parquets = node_parquets
        self.parquet = parquet  
        self.second_parquet = kargs['second_parquet'] if kargs['second_parquet'] else print("No second parquet passed")
    
        # Get parquet data and load to df
        # df = Metric.get_df(parquet, self.node_parquets).replace(-1, np.NaN)
        
        # Get parquet data and load to df
        df = Metric.get_df(parquet, self.node_parquets).replace(-1, np.NaN)
        # df = pd.read_parquet("/Users/cetinmehmet/Desktop/encryptedParq/surfsara_power_usage")
        df.sort_index(inplace=True)


        if self.second_parquet is not None:
            if self.second_parquet == "node_memory_MemTotal" and self.parquet == "node_memory_MemFree":
                df_total = Metric.get_df(self.second_parquet, self.node_parquets).replace(-1, np.NaN)
                df = 100 * (1 - (df / df_total)) # Get utilized fraction for memory
                self.ylabel="Utilized fraction"
            else:
                print("Second parquet doesn't make sense")
                exit(1)

        self.df_cpu, self.df_gpu = ParseMetric().cpu_gpu(df)

        # Split to df according to covid non covid
        self.df_cpu_covid, self.df_cpu_non_covid = ParseMetric().covid_non_covid(self.df_cpu)
        self.df_gpu_covid, self.df_gpu_non_covid = ParseMetric().covid_non_covid(self.df_gpu)

          # Load json file
        with open(curr_path + "/analysis/metric.json", 'r') as f:
            metric_json = json.load(f)

        # Assign the components of the plot
        self.title = metric_json[parquet]['title']
        self.savefig_title = metric_json[parquet]['savefig_title'] + "default/"
        self.ylabel = metric_json[parquet]['ylabel']

    def get_meta_data(self):
        return self.title, self.savefig_title

    def daily_seasonal_diurnal_pattern(self):
        DiurnalAnalysis().daily_seasonal_diurnal_pattern(
            df_cpu_dic={'covid': self.df_cpu_covid, 
                        'non_covid': self.df_cpu_non_covid,
            }, 
            df_gpu_dic={
                'covid': self.df_gpu_covid,
                'non_covid': self.df_gpu_non_covid
            }, 
            shareX=True, title=self.title, ylabel=self.ylabel,
            savefig_title=self.savefig_title + "daily_seasonal_diurnal"
        )
    
    def daily_monthly_diurnal_pattern(self):
        DiurnalAnalysis().daily_monthly_diurnal_pattern(
            month_dic={'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'June': 6, "July": 7},
            df_cpu=self.df_cpu,
            df_gpu=self.df_gpu,
            savefig_title=self.savefig_title + "daily_monthly_diurnal", 
            ylabel=self.ylabel, 
            title=self.title
        )

    def hourly_seasonal_diurnal_pattern(self, shareX=True):
        DiurnalAnalysis().hourly_seasonal_diurnal_pattern(
            df_cpu_dic={'covid': self.df_cpu_covid, 
                        'non_covid': self.df_cpu_non_covid,
            }, 
            df_gpu_dic={
                'covid': self.df_gpu_covid,
                'non_covid': self.df_gpu_non_covid
            }, 
            ylabel=self.ylabel, shareX=True, title=self.title, 
            savefig_title=self.savefig_title + "hourly_seasonal_diurnal"
        )
    
    def hourly_monthly_diurnal_pattern(self):
        DiurnalAnalysis().hourly_monthly_diurnal_pattern(
            month_dic={'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'June': 6, "July": 7},
            df_cpu=self.df_cpu,
            df_gpu=self.df_gpu,
            savefig_title=self.savefig_title + "hourly_monthly_diurnal", 
            ylabel=self.ylabel, 
            title=self.title
        )

    def rack_analysis(self):
        GenerateDefaultGraph( 
            ylabel=self.ylabel, title=self.title, savefig_title=self.savefig_title + "rack_analysis"
        ).figure_rack_analysis(
            df_cpu_dic={
                'covid': self.df_cpu_covid,
                'non_covid': self.df_cpu_non_covid,
            },
            df_gpu_dic={
                'covid': self.df_gpu_covid, 
                'non_covid': self.df_gpu_non_covid
            }
        )

    def entire_period_analysis(self):
        GenerateDefaultGraph(
            ylabel=self.ylabel, title=self.title, savefig_title=self.savefig_title + "entire_period"
        ).entire_period_analysis(df_cpu=self.df_cpu, df_gpu=self.df_gpu)

    def CDF_plot(self):
        GenerateDefaultGraph(savefig_title = self.savefig_title + "cdf", title=self.title, ylabel=self.ylabel).CDF_plot(
            ax_cpu_dic = {
                'covid': self.df_cpu_covid.mean(),
                'non-covid': self.df_cpu_non_covid.mean()
            },
            ax_gpu_dic = {
                'covid': self.df_gpu_covid.mean(),
                'non-covid': self.df_gpu_non_covid.mean()
            },
        
        )
    
    def create_table(self):
        GenerateTable(title=self.title, savefig_title=self.savefig_title, period=None).default_table(df_dict={
            'df_cpu_covid': self.df_cpu_covid,
            'df_gpu_covid': self.df_gpu_covid,
            'df_cpu_non_covid': self.df_cpu_non_covid,
            'df_gpu_non_covid': self.df_gpu_non_covid
        })

    def all_analysis(self):
        self.daily_seasonal_diurnal_pattern()
        self.daily_monthly_diurnal_pattern()
        self.hourly_seasonal_diurnal_pattern()
        self.hourly_monthly_diurnal_pattern()
        self.rack_analysis()
        self.entire_period_analysis()
        self.CDF_plot()
        

