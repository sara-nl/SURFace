import pandas as pd

"""
    Split the metrics in terms of:
        1. Plot the entire set of nodes, which means no partition in nodes
        2. Split the nodes, CPU vs GPU
        3. Break down number of cores for both CPU and GPU
        4. Split from types of processors, there are 5 to 10 types.
        5. COVID vs NON-COVID
"""

# # The CPU racks
# CPU_RACKS = [
#     'r1899', 'r1898', 'r1897', 
#     'r1896', 'r1903', 'r1902', 'r1128', 
#     'r1134', 'r1133', 'r1132'
# ]

GPU_NODES = {
    "r28n1", "r28n2", "r28n3", "r28n4", "r28n5",
    "r29n1", "r29n2", "r29n3", "r29n4", "r29n5",
    "r30n1", "r30n2", "r30n3", "r30n4", "r30n5", "r30n6", "r30n7",
    "r31n1", "r31n2", "r31n3", "r31n4", "r31n5", "r31n6"
    "r32n1", "r32n2", "r32n3", "r32n4", "r32n5", "r32n6", "r32n7",
    "r33n2", "r33n3", "r33n5", "r33n6",
    "r34n1", "r34n2", "r34n3", "r34n4", "r34n5", "r34n6", "r34n7",
    "r35n1", "r35n2", "r35n3", "r35n4", "r35n5",
    "r36n1", "r36n2", "r36n3", "r36n4", "r36n5",
    "r38n1", "r38n2", "r38n3", "r38n4", "r38n5",
}

CPU_RACKS = {
    "r10", "r11", "r12", "r13", "r14", "r15", "r23", "r25", "r26", "r27"
}

GPU_RACKS = {
    "r28", "r29", "r30", "r31", "r32", "r33",
    "r34", "r35", "r36", "r38"
}

class ParseMetric:

    @staticmethod
    def covid_non_covid(df):
        """
        INIT STEP: 
        Split data for COVID vs NON-COVID
        Return covid non covid dfs
        """

        # Convert df index to TimeStamp if the index is just seconds
        if df.index.dtype == "int64":
            df.index = pd.to_datetime(df.index, unit='s')
            
        covid_df = df.loc['2020-02-27 00:00:00' :, :]
        non_covid_df = df.loc[: '2020-02-26 23:59:45', :]

        # Reset index 
        covid_df.reset_index()
        non_covid_df.reset_index()
        
        return covid_df, non_covid_df

    @staticmethod
    def user_period_split(df, start_period, end_period):
        """
        Parse the period of the df according to the user's desire
        """
        # Convert df index to TimeStamp if the index is just seconds
        if df.index.dtype == "int64":
            df.index = pd.to_datetime(df.index, unit='s')
            
        user_df = df.loc[start_period : end_period, :]

        return user_df

    @staticmethod 
    def cpu_gpu(df):
        """
        SECOND STEP:
        Split the nodes, CPU vs GPU
        Return the cpu, and gpu partitioned dfs
        """

        cpu_nodes = [cpu_node for cpu_node in df.columns if cpu_node.split("n")[0] not in GPU_RACKS]
        gpu_nodes = [gpu_node for gpu_node in df.columns if gpu_node.split("n")[0] in GPU_RACKS]

        return df[cpu_nodes], df[gpu_nodes]

    @staticmethod
    def get_rack_nodes(df, my_rack):
        rack_nodes = set()

        for node in df.columns:
            rack = node.split("n")[0]
            if rack == my_rack:
                rack_nodes.add(node)

        return df.loc[: , rack_nodes]

    @staticmethod
    def nr_cores(self):
        """
        Break down number of cores for both CPU and GPU
        This function should be used inside the cpu_gpu. 
        Becuase, number of cores should be identified after splitting the nodes.
        Although, vice versa is also possible.
        """
        pass

    @staticmethod
    def type_of_procs(self):
        """
        Split from types of processors, there are 5 to 10 types.
        """
        pass
