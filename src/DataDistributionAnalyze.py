'''
Created on 2015. 5. 21.

@author: Ryuja
'''
import random
from string import join

from DNATube_GPU import DNATube_GPU
from DataModule import DataModule
import numpy as np


def analyze(data, num, sample, dim, HEnum, conc, pos):

    random.seed()
    random.shuffle(data)
    
    tube = DNATube_GPU()
    for j in range(num) :
        d = data[num]
        for k in range(sample) :
            idx = [ (p/dim, p%dim) for p in np.random.choice(dim**2, HEnum, replace=False) ]
            HE = join([ str(idx[m][0]) + '_' + str(idx[m][1]) + '_' + str(d[idx[m]]) for m in range(HEnum) ], '__')
            tube.addSubstance(HE, conc, pos)
        
#         tubes[i].setLabel(lblPrf + "_cycle" + str(cyc+1))
        
    tube.plotDistribution("T", 1)


if __name__ == '__main__':
    
    dm = DataModule()
    train = dm.loadImages("bwtrain_c67_sz8_bw75.dat")
    test = dm.loadImages("bwtest_c67_sz8_bw75.dat")
    analyze(train[1][0], 5000, 500, 8, 3, 1, "T")