
# Computational exploration of molecular receptive fields in the olfactory bulb reveals a glomerulus-centric chemical map

This repository contains *ALL* code that is required to precisely replicate *every figure* in the manuscript [1] and the supplement. It also contains all code that was used to process the raw imaging data. 

[1] J. Soelter, J. Schumacher, H. Spors, and M. Schmuker, “Computational exploration of molecular receptive fields in the olfactory bulb reveals a glomerulus-centric chemical map,” bioRxiv, vol. 73, p. 489666, Dec. 2018. https://doi.org/10.1101/489666 



## Recreate the figures from the manuscript
1. Clone this repository.
2. Set up a suitable python environment. Required packages and versions are documented in `soelteretal.yml` (an anaconda environment file).  
3. Download the data (5 GB) from zenodo: http://doi.org/10.5281/zenodo.1297377 . 
4. extract the data and place the directory on the same level as this repository (not inside it).
5. Use the notebooks that start with `MOB_Fig_...` to replicate the figures.
6. Report any problems, errors, suggestions for improvement as issues in this repository.

In case of errors, please check first that you are using the correct python packages and the correct versions. 


## Recreate the preprocessed data set from the raw data

**Warning:** Recreating the preprocessed data set from raw data is a considerable effort, quite time-consuming and requires substantial computing resources. The notebooks have not been revised for easy replicability. You can't just "shift-enter" through the notebooks and expect everything to work. You will have to adjust paths. You might run into errors due to wrong package versions and be able to detect and fix those. In some cases you will have to figure out a sensible sequence in which cells have to be run; some cells will not have to be run at all. You need to understand the steps involved in the process and infer what's being done from reading the code. It requires a deep familiarity with the packages used, including the ones provided by us.

You have been warned! If you still want to go forward with the raw data:

1. Ask for the raw data set (135 GB).
2. preprocessMOB.ipynb: prepare data.
3. visualizeMOB.ipynb get an overview of data.
4. decomposeMOB.ipynb perform matrix factorisation.
5. MOR18-2spectrum.ipynb extract MOR18-2spectrum.
7. HierachicalClustering.ipynb: Do Clustering, extract spectra of fingerprinted glomeruli.
8. MOBPredict.ipynb: Analyze chemical spectra.

 