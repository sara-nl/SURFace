import os

ROOT = 0
DIR = 1
FILE = 2


class ParseParquet:

    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.new_node_dir = next(os.walk(dataset_path))[DIR]

    def __construct_parquet_path(self, metric_dir: list, pq_path: str):
        """
        Construct a dict with metric name as the key and metric path as the value
        :param parq:
        :param dir:
        :return dict:
        """
        metric_path_dic = {}

        for metric in metric_dir:
            metric_path = self.dataset_path + pq_path + "/" + metric    # path to metric
            parquet = "".join(next(os.walk(metric_path))[FILE])         # parquet file
            metric_parquet_path = metric_path + parquet           # path to parquet file
            metric_path_dic[metric] = metric_parquet_path               # key: metric, value: path_to_parquet

        return metric_path_dic

    def __construct_new_data_parq_path(self, metric_dir: list):
        metric_path_dic = {}

        for metric in metric_dir:
            metric_path = self.dataset_path + "/" + metric
            metric_path_dic[metric] = metric_path

        return metric_path_dic

    def get_parquets(self):
        """
        Parse the node and gpu files for analysis
        :param dataset_path:
            selecting the following parquets:
                node_entropy_available_bytes, node_procs_running, node_procs_blocked,
                node_committedAS, node_commitLimit, node_filefd_alloc, node_filefd_maximum,
                node_disk_read_bytes, node_disk_write_bytes, node_disk_reads_completed, node_disk_writes_completed,
                node_load1, node_load5, node_load15
        :return:
        """

        new_node_parquets = self.__construct_new_data_parq_path(self.new_node_dir)
        return new_node_parquets

