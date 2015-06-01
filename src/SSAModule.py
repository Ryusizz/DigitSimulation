'''
Created on 2015. 4. 9.

@author: Ryuja
'''
from collections import Counter
import math
import random

from numba import cuda

from DNATube import DNATube
from DataModule import DataModule
import numpy as np


class SSAModule(object):


    def __init__(self):

        self.outputFreq = 100
    

    def SSA(self, tube, maxTime):
        
        if isinstance(tube, DNATube) :
            return self.__SSAOnDNATube(tube, maxTime)
        else :
            return self.__SSAOnTube(tube, maxTime)
            
            
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
    
    
    def __writeCount(self, chemComp, molCounts, spcs):
        
        d = [ chemComp[spc] for spc in spcs ]
        return np.vstack((molCounts, np.array(d)))
        
    
    def __SSAOnTube(self, tube, maxTime):
        
        random.seed()
        molCounts = np.zeros((0, len(tube.chemComp)+1))
        time = 0.0
        iteration = 0
        
        spcs = tube.chemComp.keys()
        while time < maxTime :
            
            a_i = self.compute_propensities(tube.R, tube.chemComp)
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
            
            self.update(tube.R, count-1, tube.chemComp)
            
            if (iteration % self.outputFreq) == 0 :
                d = [ tube.chemComp[spc] for spc in spcs ]
                d.append(time)
                molCounts = np.vstack((molCounts, np.array(d)))
#                 print("iteration %d    time %5.4g" % (iteration, time))
            
            iteration += 1
    
        spcs.append("time")
        return molCounts, spcs, time
    
    
    def computePropensitiesDNA(self, R, chemCompTop, chemCompBot, chemCompDS):
        
        P = [None] * len(R)
                
        for i in range(len(R)) :
            r = R[i]
            subs = r[0]
            rate = r[1]
            
#             p = rate
            if len(subs) == 2 :
#                 subTop = subs[0]
#                 subBot = subs[1]
                P[i] = rate * chemCompTop[subs[0]] * chemCompBot[subs[1]]
            elif len(subs) == 1 :
#                 subDS = subs[0]
                P[i] = rate * chemCompDS[subs[0]]
            
#             P[i] = p
        
        return P
    
    
    def computePropensities(self, R, chemComp):
        
        P = [None] * len(R)
                
        for i in range(len(R)) :
            r = R[i]
            subs = r[0]
            rate = r[1]
            
            p = rate
            for sub in subs :
                p *= chemComp[sub]
            
            P[i] = p
        
        return P
    
    
    def updateDNA(self, R, idx, chemCompTop, chemCompBot, chemCompDS):
        
        r = R[idx]
        subs = r[0]
        prods = r[2]
        
        if len(subs) == 2 :
            subTop = subs[0]
            subBot = subs[1]
            prodDS = prods[0]
            chemCompTop[subTop] -= 1
            chemCompBot[subBot] -= 1
            chemCompDS[prodDS] += 1
        
        elif len(subs) == 1 :
            subDS = subs[0]
            prodTop = prods[0]
            prodBot = prods[1]
            chemCompDS[subDS] -= 1
            chemCompTop[subTop] += 1
            chemCompBot[subBot] += 1
    
    
    def update(self, R, idx, chemComp):
        
        r = R[idx]
        subs = r[0]
        prods = r[2]
        
        for sub in subs :
            chemComp[sub] -= 1
        for prod in prods :
            chemComp[prod] += 1        


@cuda.autojit
def computePropentsitiesDNA_GPU(R, Rsize, P, chemCompTop, chemCompBot, chemCompDS):
    
    tid = cuda.blockIdx.x * cuda.blockDim.x + cuda.threadIdx.x    # gpu index part
    
    if tid < Rsize :
        r = R[tid]
        subs = r[0]
        rate = r[1]
    
        if len(subs) == 2 :
            P[tid] = rate * chemCompTop[subs[0]] * chemCompBot[subs[1]]
        elif len(subs) == 1 :
            P[tid] = rate * chemCompDS[subs[0]]
                
                
if __name__ == '__main__' :
    
    a = [1,2,3]
    a.append(4)