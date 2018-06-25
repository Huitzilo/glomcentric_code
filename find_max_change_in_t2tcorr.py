from configobj import ConfigObj
import os
import numpy as np
import sys
import regnmf.ImageAnalysisComponents as ia
from scipy.spatial.distance import pdist

basepath = os.path.abspath(sys.argv[1])
datafilename =  'ios_meas'
response_window = (3,5) #define frames to calculate odor response; ios:(3,5) sph:(8,12


#from config file nnmf_150_sm2_convex.ini
config_dict = {
'num_components':150,
'sparse_fct':'global_sparse',
'smooth_param':2,
'init':'convex',
'neg_time':False,
'verbose':0,
'maxcount':50#,
#'sparse_param':sparseness
}

print("analysing files in {}".format(basepath))
with open(os.path.join(basepath, 'sourcecorrs.dat'),'w') as f:
  f.write("# animal {}\n".format(os.path.basename(basepath))) 
  f.write("# sparseness\tcorr\n")
  for sparseness in np.arange(0.1,1.000001,0.1):
    ts_path = os.path.join(basepath, '_'.join(["nnmf", 
                                               str(config_dict['num_components']), 
                                               "sm{}".format(config_dict['smooth_param']), 
                                               config_dict['init'],
                                               'sp{:02.0f}'.format(sparseness*10),
                                               datafilename]))
    
    decomposition = ia.TimeSeries()
    decomposition.load(ts_path)
    signal = ia.TrialMean()(ia.CutOut(response_window)(decomposition))
    mode_cor = ia.CalcStimulusDrive()(signal)
    mask = mode_cor._series.squeeze()<0.5
    if np.sum(mask) > 1: #if there are stimulus driven components  
      selected_modes = ia.SelectObjects()(decomposition, mask)   
      cor = np.nanmax(1-pdist(selected_modes.base._series, 'correlation'))
    else:
      cor = np.nanmax(1-pdist(decomposition.base._series, 'correlation'))
    f.write("{}\t{}\n".format(sparseness, cor))

