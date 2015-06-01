'''
Created on 2015. 5. 12.

@author: Ryuja
'''
import random

from numba import cuda

from DNATube import DNATube
import numpy as np



outputFreq = 100
  
def SSA(tube, maxTime):
    
    if isinstance(tube, DNATube) :
        return __SSAOnDNATube_GPU(tube, maxTime)
#     else :
#         return __SSAOnTube(tube, maxTime)
    

def __SSAOnDNATube_GPU(tube, maxTime):
    
    random.seed()
    
    molCountsTop = np.zeros((0, len(tube.chemCompTop)))
    molCountsBot = np.zeros((0, len(tube.chemCompBot)))
    molCountsDS = np.zeros((0, len(tube.chemCompDS)))
    timeCounts = np.zeros((0,1))
    spcsTop = tube.chemCompTop.keys()
    spcsBot = tube.chemCompBot.keys()
    spcsDS = tube.chemCompDS.keys()
    time = 0.0
    iteration = 0
    
    while time < maxTime :
        
        """Temporary GPGPU Part"""
        threads_per_block = 128
        number_of_blocks = (len(tube.R)/threads_per_block) + 1
        P = np.empty(len(tube.R))
        a_i = np.ones((1, reactionNumber))
        a_i =  multiplyConc [ number_of_blocks, threads_per_block ] (tube.R, a_i, )
#             a_i = self.computePropensitiesDNA(tube.R, tube.chemCompTop, tube.chemCompBot, tube.chemCompDS)
        a_0 = sum(a_i)
        if a_0 <= 0.0 :
#                 print "All reactants are exhausted"
#                 print("Debugging : a_0 %5.4g" % a_0)
#                 print("a_i", a_i)
            break
        
        rand_1 = random.random()
        tau = 1.0/a_0 * math.log(1/rand_1)
        time += tau
        
        rand_2 = random.random()
        thres = a_0 * rand_2
        
        summation = 0
        count = 0
        while thres > summation :
            summation += a_i[count]
            count += 1
        
        self.updateDNA(tube.R, count-1, tube.chemCompTop, tube.chemCompBot, tube.chemCompDS)
        
        if (iteration % self.outputFreq) == 0 :
            
            molCountsTop = self.__writeCount(tube.chemCompTop, molCountsTop, spcsTop)
            molCountsBot = self.__writeCount(tube.chemCompBot, molCountsBot, spcsBot)
            molCountsDS = self.__writeCount(tube.chemCompDS, molCountsDS, spcsDS)
            timeCounts = np.vstack((timeCounts, np.array([time])))
#                 print("iteration %d    time %5.4g" % (iteration, time))
        
        iteration += 1

    molCountsList = [molCountsTop, molCountsBot, molCountsDS]
    spcsList = [spcsTop, spcsBot, spcsDS]
    headList = ["Top", "Bot", "Double"]
    return molCountsList, spcsList, headList, timeCounts, time

    
def __SSAOnDNATube(self, tube, maxTime):
    
    random.seed()
    molCountsTop = np.zeros((0, len(tube.chemCompTop)))
    molCountsBot = np.zeros((0, len(tube.chemCompBot)))
    molCountsDS = np.zeros((0, len(tube.chemCompDS)))
    timeCounts = np.zeros((0,1))
    spcsTop = tube.chemCompTop.keys()
    spcsBot = tube.chemCompBot.keys()
    spcsDS = tube.chemCompDS.keys()
    time = 0.0
    iteration = 0
    
    while time < maxTime :
        
        """Temporary GPGPU Part"""
        threads_per_block = 128
        number_of_blocks = (len(tube.R)/threads_per_block) + 1
        P = np.empty(len(tube.R))
        a_i = computePropentsitiesDNA_GPU [ number_of_blocks, threads_per_block ] (tube.R, len(tube.R), P, tube.chemCompTop, tube.chemCompBot, tube.chemCompDS)
#             a_i = self.computePropensitiesDNA(tube.R, tube.chemCompTop, tube.chemCompBot, tube.chemCompDS)
        a_0 = sum(a_i)
        if a_0 <= 0.0 :
#                 print "All reactants are exhausted"
#                 print("Debugging : a_0 %5.4g" % a_0)
#                 print("a_i", a_i)
            break
        
        rand_1 = random.random()
        tau = 1.0/a_0 * math.log(1/rand_1)
        time += tau
        
        rand_2 = random.random()
        thres = a_0 * rand_2
        
        summation = 0
        count = 0
        while thres > summation :
            summation += a_i[count]
            count += 1
        
        self.updateDNA(tube.R, count-1, tube.chemCompTop, tube.chemCompBot, tube.chemCompDS)
        
        if (iteration % self.outputFreq) == 0 :
            
            molCountsTop = self.__writeCount(tube.chemCompTop, molCountsTop, spcsTop)
            molCountsBot = self.__writeCount(tube.chemCompBot, molCountsBot, spcsBot)
            molCountsDS = self.__writeCount(tube.chemCompDS, molCountsDS, spcsDS)
            timeCounts = np.vstack((timeCounts, np.array([time])))
#                 print("iteration %d    time %5.4g" % (iteration, time))
        
        iteration += 1

    molCountsList = [molCountsTop, molCountsBot, molCountsDS]
    spcsList = [spcsTop, spcsBot, spcsDS]
    headList = ["Top", "Bot", "Double"]
    return molCountsList, spcsList, headList, timeCounts, time

    
    
@cuda.autojit
def multiplyConc(R, a_i, chemComp): # chemComp is numpy array
    
    tid = cuda.blockIdx.x * cuda.blockDim.x + cuda.threadIdx.x  # gpu index part
    a_i[R[tid][1]] *= chemComp[R[tid][2]]
    
def multiplyConst(a_i, K):
    
    pass