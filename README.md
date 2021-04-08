# SURF Automatic Collection Engine (SURFace)

This repository contains several scripts to analyze and visualize data collected from SURF's Lisa cluster. The data can be found on Zenodo at [https://zenodo.org/record/4459519](https://zenodo.org/record/4459519).

## Usage
1. Download the dataset using the link mentioned above
2. Clone this repository to some folder.
3. Per script, modify the paths as required. `"/path/to/surfsara-jobdata/"`, `"path to machine metric dataset"` and variants should point the the dataset downloaded in point 1. `./cache` should be point to a location where some scratch data can be put.
4. Run the notebook on a machine that has 64GB or more RAM, as some analyses require some in-memory storage. For some scripts, a Spark cluster is required due to the sheer amount of data and processing required. If `Koalas` is used in a script, you are most likely needing to setup a small spark cluster. 4-10 machines each having 64GB or more RAM will suffice. In `correlation_plot_koalas.py`, we use 5 machines (1 master, 4 workers) each having 64GB of RAM.
5. The figures will be output in the folder where the notebook resides, or where you point the paths Matplotlib/Seaborn should output to. Tables are printed in the notebook as a string.
## 
Scripts
The scripts have generally a self-describing name. Below we provide some more details per script. 
| Script                                   | Explanation                                                                                                                                                                                                        |
|------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| !LSTM V2.ipynb                           | Investigates the effect of different sampling intervals on predictions of metric values.                                                                                                                           |
| !Network data analysis.ipynb             | Performs various analyses related to network IO.                                                                                                                                                                   |
| !Z-Score.ipynb                           | A script that investigates if anomalies can be detected using z-scores.                                                                                                                                            |
| !jobdata_analysis_new.ipynb              | Performs various different analyses related to the executed jobs within Lisa.                                                                                                                                      |
| Full_Cluster_bottleneck_analysis.ipynb   | Creates a holistic normalized overview of the dataset by aligning job arrivals with various machine metrics.                                                                                                       |
| Generic_outline_dataset.ipynb            | Computes various generic properties of the dataset. The overview table below in the readme is constructed using this script.                                                                                       |
| correlation_single_rack_one_day.ipynb    | Computes the Pearson, Spearman, and Kendall correlation coefficients for all pairs of metrics within the dataset on individual days.                                                                               |
| analysis_coefficient_separate_days.ipynb | Visualizes in various ways the output of correlation_single_rack_one_day.ipynb.                                                                                                                                    |
| correlation_plot_koalas.py               | Computes a dense correlation plot of normalized histograms, scatterplots with linear regression lines per metric pair, and visualized the Pearson, Spearman, and Kendall correlation coefficients per metric pair. |
| koalas_correlation_plot_data_only.ipynb  | Creates a better visualization of the plot of correlation_plot_koalas.py by creating a variant of Seaborn's pairgrid.                                                                                              |
| daily_weekly_trend_load.ipynb            | Creates several weekly and diurnal trend visualizations.                                                                                                                                                           |
| file_sizes_different_granularities.ipynb | Computes the storage overhead for different sampling frequencies using a selection of metrics.                                                                                                                     |
| generate_barplots.py                     | Generates barplots of metric values in covid vs non-covid periods.                                                                                                                                                 |
| generate_boxplots.py                     | Generates boxplots of metric values in covid vs non-covid periods.                                                                                                                                                 |
| job_arrival_characterization.ipynb       | Creates several visualizations and performs different kind of analyses based on job arrivals.                                                                                                                      |
| mean_memory_utilization_nodes.ipynb      | Analyses different aspects of the node RAM usage and creates several different visualization.                                                                                                                      |
| power_consumption_analysis.ipynb         | Performs several analyses on the rack and power consumption and creates several different visualizations.                                                                                                          |
| rack_temp_noenc.py                       | Analyzes for various racks their node temperatures and creates visualizations for them.                                                                                                                            |

## Outline of the dataset
---
The dataset spans from 2019-12-29 to 2020-08-07.

| Element                          | Value          |
|----------------------------------|----------------|
| Sampling frequency               | 15 seconds     |
| Max. samples per metric per node | 1,258,646      |
| Number of metrics                | 327            |
| Number of measurements           | 66,541,895,243 |


## Libraries used 
Most tools in this repository were created and tested using the following libraries and their versions:
| Library     | Version   |
|-------------|-----------|
| Pandas      | 1.2.0     |
| NumPy       | 1.19.4    |
| SciPy       | 1.5.3     |
| statsmodels | 0.12.1    |
| pytz        | 2020.4    |
| SKlearn     | 0.24.0    |
| Tensorflow  | 2.3.1     |
| pyarrow     | 3.0.0     |
| Dask        | 2021.03.0 |
| Matplotlib  | 3.4.1     |
| Seaborn     | 0.11.1    |
| Koalas      | 1.5.0     |
| Spark       | 3.0.0     |
| Hadoop      | 2.7.7     |