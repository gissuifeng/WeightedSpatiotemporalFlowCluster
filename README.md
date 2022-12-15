# WeightedSpatiotemporalFlowCluster
Weighted origin-destination flow cluster method considering spatiotemporal continuity to reveal interregional association patterns

An algorithm for mining interzonal flow patterns from weighted spatio-temporal origin-destination(OD) flows. The algorithm is implemented in python.

1. Algorithm parameters

The input to the algorithm is OD flow data with spatial location, which can be provided in the form of a table. Each record of the table represents a flow unit and must contain the columns of location of the origin and destination (or provide foreign keys associated with basic areal unit), weights, time, and other attribute columns.The polygon-based spatial adjacent matrix also should be provided, or Area dataset consisting of specific spatial areal units can also be used as a proxy for the adjacency matrix, and the adjacency matrix can be constructed in GIS or other suppoted software based on this areal dataset. In addition, the merging threshold of the flow units, spatial adjacent rules and the time interval is also necessary parameters.

2. Folders and files

This repository contains two folders, the code in folder named 'WSTFP_AnyTime' can run synthetic dataset and real dataset as a input, but it is slower because the input data of real dataset has 2.6 million records. the code in 'WSTFP' has special processing for real dataset, constructing spatio-temporal index, and the calculation is faster. If you want to test the real dataset, it is recommended to use the code in folder 'WSTFP'. However, the algorithm logic is the same in both folders.

3. Output





