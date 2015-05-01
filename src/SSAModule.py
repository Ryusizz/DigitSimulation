'''
Created on 2015. 4. 9.

@author: Ryuja
'''
from collections import Counter
import math
import random
import numpy as np

from DataModule import DataModule


class SSAModule(object):


    def __init__(self):

        pass
    

    def lottkaVolterraSSA(self, tube, maxTime):
        
        random.seed()
        molCounts = np.zeros((0, len(tube.chemComp)+1))
        time = 0.0
        iteration = 0
        outputFreq = 100
        
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
            
            if (iteration % outputFreq) == 0 :
                d = [ tube.chemComp[spc] for spc in spcs ]
                d.append(time)
                molCounts = np.vstack((molCounts, np.array(d)))
#                 print("iteration %d    time %5.4g" % (iteration, time))
            
            iteration += 1
    
        spcs.append("time")
        return molCounts, spcs, time
    
    
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