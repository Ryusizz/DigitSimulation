'''
Created on 2015. 4. 9.

@author: Ryuja
'''
from collections import Counter
import math
import random

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
        molCounts = np.zeros((0, len(tube.chemCompTop) + 
                              len(tube.chemCompBot) + 
                              len(tube.chemComDS) + 1 ))
        time = 0.0
        iteration = 0
        
        while time < maxTime :
            
            a_i = self.computePropensitiesDNA(tube.R, tube.chemCompTop, tube.chemCompBot, tube.chemComDS)
            a_0 = sum(a_i)
            if a_0 <= 0.0 :
                print "All reactants are exhausted"
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
                d = [ tube.chemComp[spc] for spc in spcs ]
                d.append(time)
                molCounts = np.vstack((molCounts, np.array(d)))
#                 print("iteration %d    time %5.4g" % (iteration, time))
            
            iteration += 1
    
        spcs.append("time")
        return molCounts, spcs, time
    
    
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
                print "All reactants are exhausted"
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
            
            p = rate
            if len(subs) == 2 :
                subTop = subs[0]
                subBot = subs[1]
                p *= chemCompTop[subTop] * chemCompBot[subBot]
            elif len(subs) == 1 :
                subDS = subs[0]
                p *= chemCompDS[subDS]
            
            P[i] = p
        
        return P
    
    def compute_propensities(self, R, chemComp):
        
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


if __name__ == '__main__' :
    
    a = [1,2,3]
    a.append(4)