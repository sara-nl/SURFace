Description of the Lisa system


GPU Nodes

    nr - processor - scratch - memory - sockets - cores - gpu
    23x - bronze_3104 - 1.5TB NVME - 256 GB UPI 10.4 GT/s - 2 - 12 - 4x GeForce 1080Ti, 11GB GDDR5X
    2x - bronze_3104 - 1.5TB NVME - 256 GB UPI 10.4 GT/s - 2 - 12 - 4x Titan V, 12GB HBM2
    29x  - gold_5118 - 1.5 TB NVME - 192 GB UPI 10.4 GT/s - 2 - 24 - 4x Titan RTX, 24GB GDDR6

CPU Nodes

    nr - processor - scratch - memory - sockets - cores
    192x - gold_6130 - 1.7TB - 96GB UPI 10.4 GT/s - 1 - 16
    96x - silver_4110 - 1.8TB - 96 GB UPI 9.6 GT/s -  2 - 16
    1x - e7_8857_v2 - 1TB QPI 8.00 GT/s - 4 - 48
    1x - gold_6126 - 2TB UPI 10.4 GT/s - 4 - 48
    
Processor information:
* bronze_3104:
  - nr of cores:                6
  - nr of threads:              6
  - Processor base frequency:   1.70GHz
  - Cache:                      8.25 MB L3 Cache
  - Bus Speed:                  10.4 GT/s
  - nr of UPI Links:            2
* gold_5118:
  - nr of cores:                12
  - nr threads:                 24
  - Processor base frequency:   2.30 GHz
  - Max turbo frequency:        3.20 GHz
  - Cache:                      16.5 MB L3 Cache
  - Bus Speed:                  10.4 GT/s
  - nr of UPI Links:            2
* gold_6130:
  - nr of cores:                16
  - nr of threads:              32
  - Processor base frequency:   2.10 GHz
  - Max turbo frequency:        3.70 GHz
  - Cache:                      22 MB L3 Cache
  - Bus Speed:                  10.4 GT/s
  - nr of UPI Links:            3
* silver_4110
  - nr of cores:                8
  - nr of threads:              16
  - Processor base frequency:   2.10 GHz
  - Max turbo frequency:        3.00 GHz
  - Cache:                      11 MB L3 Cache
  - Bus Speed:                  9.6 GT/s
  - nr of upi Links:            2
* e7_8857_v2:
  - nr of cores:                12
  - nr of threads:              12
  - Processor base frequency:   3.00 GHz
  - Max turbo frequency:        3.60 GHz
  - Cache:                      30 MB
  - Bus Speed:                  8 GT/s
  - nr of qpi Links:            3
* gold_6126:
  - nr of cores:                12
  - nr of threads:              24
  - Processor base frequency:   2.60 GHz
  - Max turbo frequency:        3.70 GHz
  - Cache:                      19.25 MB L3 Cache
  - Bus Speed:                  10.4 GT/s
  - nr of upi Links:            3
