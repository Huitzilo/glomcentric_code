from configobj import ConfigObj
import os
import numpy as np
import sys
import regnmf.ImageAnalysisComponents as ia
#from scipy.spatial.distance import pdist
#import matplotlib.pyplot as plt
#from PIL import Image

# this script should be called in the directory where the data is. 
# results are saved to that same directory.

basepath = os.path.abspath(sys.argv[1])
sparseness = float(sys.argv[2])
redo = False# redo factorization if it already exists
datafilename =  'ios_meas'

datafilepath = os.path.join(basepath, datafilename)
response_window = (3,5) #define frames to calculate odor response; ios:(3,5) sph:(8,12


#assert 'nnmf' in cfgfile

#from config file nnmf_150_sm2_convex.ini
config_dict = {
'num_components':150,
'sparse_fct':'global_sparse',
'smooth_param':2,
'init':'convex',
'neg_time':False,
'verbose':0,
'maxcount':50,
'sparse_param':sparseness
}

#load config
cfg = ConfigObj(config_dict, unrepr=True)

saveloc = os.path.join(basepath, '_'.join(["nnmf", 
                                           str(config_dict['num_components']), 
                                           "sm{}".format(config_dict['smooth_param']), 
                                           config_dict['init'],
                                           'sp{:02.0f}'.format(cfg['sparse_param']*10),
                                           datafilename])) + '.npy'

#check if computation is already performed
if os.path.exists(saveloc) and not(redo):
    print '%s already done'%animal
    sys.exit(0)
    
ts = ia.TimeSeries()
ts.load(datafile)
    
# perform decomposition
decomposer = ia.NNMF(**cfg)
decomposition = decomposer(ts)
decomposition.base._series[np.isnan(decomposition.base._series)] = 0 #clear nans

# # calc spatial cor of stimulus driven components
# signal = ia.TrialMean()(ia.CutOut(response_window)(decomposition))
# mode_cor = ia.CalcStimulusDrive()(signal)
# mask = mode_cor._series.squeeze()<0.5
# if np.sum(mask) > 1: #if there are stimulus driven components  
#     selected_modes = ia.SelectObjects()(decomposition, mask)   
#     cor = np.nanmax(1-pdist(selected_modes.base._series, 'correlation'))
# else:
#     cor = np.nanmax(1-pdist(decomposition.base._series, 'correlation'))
    
#save results
decomposition.save(saveloc)
sys.exit(0)

