# About the trace archive:

This archive uses parquet to store the data. Using parquet allows for easy interfacing with pandas through pyarrow as well as provides the ability to interface with the data through spark and tensorflow without needing any conversions.

Values in the metrics that are -1 mean no measurement, in nvidia metrics this is represented with a 0.

The nvidia metrics are packed 64 bit values, this means to get the values from them bit masking is required.

To retrieve the values the following python code would unpack a single value:

    gpu1 = 0xFFFF & (val >> 0)
    
    gpu2 = 0xFFFF & (val >> 16)
    
    gpu3 = 0xFFFF & (val >> 32)
    
    gpu4 = 0xFFFF & (val >> 48)
    
Wrapping this with some code that loops through all the values and unpacks in this way will allow the archive user to perform analysis on the gpu data.

Note that the NVIDIA power metric is in watts, not milliwatts. The naming is an artifact from the data collection and will be corrected in the near future.

This file will be expanded with further clarifications in the near future.
