from configobj import ConfigObj
import os
import glob
import numpy as np
import regnmf.ImageAnalysisComponents as ia
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt
import sys
from PIL import Image

# this script should be called in the directory where the data is. 
# results are saved to that same directory.

basepath = os.path.abspath(sys.argv[1])
print basepath
datapath = basepath #os.path.join(basepath, 'MOBconverted') #where to get the data
savepath = basepath #os.path.join(basepath, 'MOBdecomposed') #where to save decompostion
savepath_vis = basepath # '/home/jan/Dokumente/MOBData/Vis/Factorizations' #where to save visualization of decomposition
datafile = os.path.join(basepath, 'ios_meas')
response_window = (3,5) #define frames to calculate odor response; ios:(3,5) sph:(8,12

#animal = sys.argv[1]

sparse_start = 0.1 #inital sparseness strength
sparse_increase = 0.1 #sparsness increase
redo = False# redo factorization if it already exists
#assert 'nnmf' in cfgfile

#from config file nnmf_150_sm2_convex.ini
config_dict = {
'num_components':150,
'sparse_fct':'global_sparse',
'smooth_param':2,
'init':'convex',
'neg_time':False,
'verbose':0,
'maxcount':50
}

#load config
cfg = ConfigObj(config_dict, unrepr=True)

#check if computation is already performed
# savelocation = os.path.join(savepath, animal)
# savename_mask = os.path.splitext(os.path.basename(cfgfile))[0] + '_sp*_' + datafile + '.npy'
# if os.path.exists(savelocation):
#     if len(glob.glob(os.path.join(savelocation, savename_mask)))>0 and not(redo):
#         print '%s already done'%animal
#         continue
# else:
#     os.makedirs(savelocation)
    
ts = ia.TimeSeries()
ts.load(datafile)

# perform decomposition. increase sparseness until spatial component correlation is below 0.5
cor = 1
while cor>0.5:
    # set sparsness level
    if 'sparse_param' in cfg:
        cfg['sparse_param'] += sparse_increase
    else:
        cfg['sparse_param'] = sparse_start
    print("sparseness {}".format(cfg['sparse_param']))
    
    # perform decomposition
    decomposer = ia.NNMF(**cfg)
    decomposition = decomposer(ts)
    decomposition.base._series[np.isnan(decomposition.base._series)] = 0 #clear nans
        
    # calc spatial cor of stimulus driven components
    signal = ia.TrialMean()(ia.CutOut(response_window)(decomposition))
    mode_cor = ia.CalcStimulusDrive()(signal)
    mask = mode_cor._series.squeeze()<0.5
    if np.sum(mask) > 1: #if there are stimulus driven components  
        selected_modes = ia.SelectObjects()(decomposition, mask)   
        cor = np.nanmax(1-pdist(selected_modes.base._series, 'correlation'))
    else:
        cor = np.nanmax(1-pdist(decomposition.base._series, 'correlation'))

#save results
saveloc = os.path.join(savepath, '_'.join(["nnmf", 
											str(config_dict['num_components']), 
											"sm{}".format(config_dict['smooth_param']), 
											config_dict['init'],
											'sp{:02.0f}'.format(cfg['sparse_param']*10),
											datafile]))
decomposition.save(saveloc)
print 'done'