'''
Created on 2015. 5. 12.

@author: Ryuja
'''
import math
import random
import theano

from DNATube_GPU import DNATube_GPU
import numpy as np
import theano.tensor as T


outputFreq = 100000
  
def SSA(tube, maxTime):
    
    if isinstance(tube, DNATube_GPU) :
        return __SSAOnDNATube_GPU(tube, maxTime)
#     else :
#         return __SSAOnTube(tube, maxTime)
    

def __SSAOnDNATube_GPU(tube, maxTime):
    
    random.seed()
    
#     molCountsTop = np.zeros((0, len(tube.chemCompTop)))
#     molCountsBot = np.zeros((0, len(tube.chemCompBot)))
#     molCountsDS = np.zeros((0, len(tube.chemCompDS)))
    #spcsTop = tube.chemCompTop.keys()
    #spcsBot = tube.chemCompBot.keys()
    #spcsDS = tube.chemCompDS.keys()
    time = 0.0
    iteration = 0
    chemComp = np.asarray(tube.getTotalChemComp(), dtype=theano.config.floatX)
    molCounts = np.zeros((0, len(chemComp)))
    timeCounts = np.zeros((0,1))
    
    #build theano function
    Rs = theano.shared(np.asarray(tube.R, dtype=theano.config.floatX), borrow=True)
    Pi = np.asarray(np.ones(len(tube.R)))
    Ps = theano.shared(Pi)
    Cs = theano.shared(chemComp)
    row = T.iscalar("row")
    col = T.iscalar("col")
    
    initializePropentiy = theano.function([], updates=[(Ps, Pi)])
    propensityUpdate = [(Ps, Ps*Cs[T.cast(Rs[:,0], 'int64')]*Cs[T.cast(Rs[:,1], 'int64')]*Rs[:,2])]
    calPropensity = theano.function([], updates=propensityUpdate)
    sumPropensity = theano.function([], T.sum(Ps))
    addConc = theano.function([row, col], updates=[(Cs, T.set_subtensor(Cs[T.cast(Rs[row][col], 'int64')], Cs[T.cast(Rs[row][col], 'int64')]+1))])
    subConc = theano.function([row, col], updates=[(Cs, T.set_subtensor(Cs[T.cast(Rs[row][col], 'int64')], Cs[T.cast(Rs[row][col], 'int64')]-1))])
    
    while time < maxTime :
        
        initializePropentiy()
        computePropensitiesDNA(calPropensity)
        a_0 = sumPropensity()
#         P = elementwiseMult(P, chemComp[tube.R[:,0].astype(int)])
#         P = elementwiseMult(P, chemComp[tube.R[:,1].astype(int)])
#         P = elementwiseMult(P, tube.R[:,2])

#         a_0 = sum(P)
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
        
        P = Ps.get_value()
        summation = 0
        count = 0
        while thres > summation :
            summation += P[count]
            count += 1
        
        updateDNA(addConc, subConc, count)
        
        
        
        if (iteration % outputFreq) == 0 :
            
            chemComp = Cs.get_value()
            molCounts = writeCount(chemComp, molCounts)
            timeCounts = np.vstack((timeCounts, np.array([time])))
#                 print("iteration %d    time %5.4g" % (iteration, time))
        
        iteration += 1

    # feedback concentration after reaction
    chemComp = Cs.get_value()
    chemCompTop = np.zeros(tube.spcsNum)
    chemCompBot = np.zeros(tube.spcsNum)
    chemCompDS = np.zeros(tube.spcsNum)
    chemCompTop[tube.idxTop.values()] = chemComp[tube.idxTop.values()]
    chemCompBot[tube.idxBot.values()] = chemComp[tube.idxBot.values()]
    chemCompDS[tube.idxDS.values()] = chemComp[tube.idxDS.values()]
    tube.chemCompTop = chemCompTop.tolist()
    tube.chemCompBot = chemCompBot.tolist()
    tube.chemCompDS = chemCompDS.tolist()

    # make output
    molCountsTop = molCounts[:,tube.idxTop.values()]
    molCountsBot = molCounts[:,tube.idxBot.values()]
    molCountsDS = molCounts[:,tube.idxDS.values()]
    spcsTop = tube.idxTop.keys()
    spcsBot = tube.idxBot.keys()
    spcsDS = tube.idxDS.keys()
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

    
def computePropensitiesDNA(function):
    
    function()
    
    
def updateDNA(addConc, subConc, count):
    
    subConc(count-1,0)
    subConc(count-1,1)
    addConc(count-1,3)
    
    
    
def writeCount(chemComp, molCounts):
        
    return np.vstack((molCounts, chemComp))
    
