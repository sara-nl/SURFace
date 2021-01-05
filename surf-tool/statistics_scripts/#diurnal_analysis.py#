import pandas as pd
import sys
import matplotlib.pyplot as plt
import pytz, os
import numpy as np

curr_path = os.getcwd() + '/surfsara-tool'
sys.path.insert(1, curr_path + '/statistics_scripts')


from generate_default_graph import GenerateDefaultGraph

"""
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

INTERVAL = 15
HOUR = INTERVAL * 4
DAY = HOUR * 24
MONTH = DAY * 30
HOURS_IN_WEEK = 168

class DiurnalAnalysis:

    # This function belongs to Laurens Versluis: https://github.com/lfdversluis
    def get_diurnal_df(self, df):
        df = df.loc[:, (df.max() > 0)]

        # Parse all times to UTC datetime objects
        # VERY IMPORTANT! By default pandas assumes nanoseconds as units, very annoying to debug
        # if you do not set unit="s" as you will get duplicate index issues...
        df["dt"] = pd.to_datetime(df.index, utc=True, unit="s")
        # Convert everything into localized Amsterdam time and then drop the timezone info again
        # dropping it is required to save the parquet file.
        df["dt"] = df["dt"].dt.tz_convert(pytz.timezone('Europe/Amsterdam')).dt.tz_localize(None)
        # Get hour of day and day columns to plot :)
        df["hour"] = df["dt"].dt.hour
        df["day"] = df["dt"].apply(lambda x: x.weekday())
        df["month"] = df["dt"].dt.month

        return df

    def __get_hourly_seasonal_df(self, df):
        """
        Hourly analysis:
            a. "Aggregated" over the entire period
            b. "Aggregated" per month 
        """
        df = self.get_diurnal_df(df)
        df_per_hour_per_node = df.groupby("hour").mean() # seasonal aggregation per hour
        df_per_hour_aggregate = df_per_hour_per_node.aggregate(func=sum, axis=1) # Take mean of all the nodes
        
        return df_per_hour_aggregate
    
    def __get_daily_seasonal_df(self, df):
        DAY = 24 # hours
        df = self.get_diurnal_df(df)

        df_per_day_per_node = df.groupby(["day", "hour"]).mean() # seasonal aggregation per day of week 
        df_sum = df_per_day_per_node.aggregate(func=sum, axis=1)# Take aggregate of all the nodes
        df_sum.index = [hour for hour in range(0, DAY*7)]
        return df_sum

    def get_daily_month_df(self, df, month):  
        df = self.get_diurnal_df(df)
        df_per_daily_per_node_monthly = df.loc[df["month"]==month, :].groupby(["day", "hour"]).mean()

        df_sum = df_per_daily_per_node_monthly.aggregate(func=sum, axis=1)# Take aggregate of all the nodes
        df_sum.index = np.arange(HOURS_IN_WEEK)
        
        return df_sum

    def get_hourly_month_df(self, df, month):
        df = self.get_diurnal_df(df)
        df_per_hour_per_node_monthly = df.loc[df["month"]==month, :].groupby("hour").mean()
        df_per_hour_aggregate_month = df_per_hour_per_node_monthly.aggregate(func=sum, axis=1)

        return df_per_hour_aggregate_month

    def daily_monthly_diurnal_pattern(self, df_cpu, df_gpu, month_dic, savefig_title, ylabel, title):
        GenerateDefaultGraph(title=title, savefig_title=savefig_title, ylabel=ylabel).figure_daily_per_monthly(
            df_cpu=df_cpu,
            df_gpu=df_gpu,
            month_dic=month_dic,
        )

    def daily_seasonal_diurnal_pattern(
        self, df_cpu_dic, df_gpu_dic, ylabel=None,
        shareX=None, title=None, savefig_title=None
    ):
        # Get daily_per_seasonal diurnal analysis
        df_gpu_covid = self.__get_daily_seasonal_df(df_gpu_dic['covid'])
        df_gpu_non_covid = self.__get_daily_seasonal_df(df_gpu_dic['non_covid'])
        df_cpu_covid = self.__get_daily_seasonal_df(df_cpu_dic['covid'])
        df_cpu_non_covid = self.__get_daily_seasonal_df(df_cpu_dic['non_covid'])

        #TODO: Use functions after this part
        GenerateDefaultGraph(title=title, savefig_title=savefig_title, ylabel=ylabel).figure_daily_per_seasonal (
            df_cpu_dic={
                'covid': df_cpu_covid,
                'non_covid': df_cpu_non_covid
            },
            df_gpu_dic={
                'covid': df_gpu_covid,
                'non_covid': df_gpu_non_covid
            },
        )
    
    def hourly_monthly_diurnal_pattern(
        self, df_cpu, df_gpu, month_dic, ylabel, savefig_title, title
    ):
        GenerateDefaultGraph(savefig_title=savefig_title, title=title, ylabel=ylabel).figure_hourly_monthly(
            df_cpu=df_cpu,
            df_gpu=df_gpu,
            month_dic=month_dic,
        )

    def hourly_seasonal_diurnal_pattern (
        self, df_cpu_dic, df_gpu_dic, ylabel=None, 
        shareX=None, title=None, savefig_title=None
    ):
        # Get daily_per_seasonal diurnal analysis
        df_cpu_covid = self.__get_hourly_seasonal_df(df_cpu_dic['covid'])
        df_cpu_non_covid = self.__get_hourly_seasonal_df(df_cpu_dic['non_covid'])
        df_gpu_covid = self.__get_hourly_seasonal_df(df_gpu_dic['covid'])
        df_gpu_non_covid = self.__get_hourly_seasonal_df(df_gpu_dic['non_covid'])

        GenerateDefaultGraph(title=title, savefig_title=savefig_title, ylabel=ylabel).figure_hourly_seasonal(
            df_cpu_dic={
                'covid': df_cpu_covid,
                'non_covid': df_cpu_non_covid
            },
            df_gpu_dic={
                'covid': df_gpu_covid,
                'non_covid': df_gpu_non_covid
            },
        )

        



        







