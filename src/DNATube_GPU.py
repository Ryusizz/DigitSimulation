'''
Created on 2015. 5. 18.

@author: Ryuja
'''
from bidict import bidict

from DNATube import DNATube
import numpy as np
import matplotlib.pyplot as plt

class DNATube_GPU(DNATube):

    def __init__(self):

        self.chemCompTop = []
        self.chemCompBot = []
        self.chemCompDS = []
        self.chemCompList = [self.chemCompTop, self.chemCompBot, self.chemCompDS]
        
        self.idxTop = bidict()
        self.idxBot = bidict()
        self.idxDS = bidict()
        self.idxList = [self.idxTop, self.idxBot, self.idxDS]
        
        self.newTop = []
        self.newBot = []
        self.newDS = []
        self.newList = [self.newTop, self.newBot, self.newDS]
        
        self.R = np.zeros((0,4), float)
        self.RList = []
        
        self.vol = 0
        self.spcsNum = 0
        self.inConc = False
        
        
    def addSubstance(self, spcs, mol, pos):
        
        if pos == "T" :
            if spcs in self.idxTop :
                self.chemCompTop[self.idxTop[spcs]] += mol
            else :
                self.chemCompTop.append(0)
                self.chemCompBot.append(0)
                self.chemCompDS.append(0)
                self.idxTop[spcs] = self.spcsNum
                self.spcsNum += 1
                self.chemCompTop[self.idxTop[spcs]] += mol
                self.newTop.append(spcs)
                
        elif pos == "B" :
            if spcs in self.idxBot :
                self.chemCompBot[self.idxBot[spcs]] += mol
            else :
                self.chemCompTop.append(0)
                self.chemCompBot.append(0)
                self.chemCompDS.append(0)
                self.idxBot[spcs] = self.spcsNum
                self.spcsNum += 1
                self.chemCompBot[self.idxBot[spcs]] += mol
                self.newBot.append(spcs)
                
        elif pos == "DS" :
            if spcs in self.idxDS :
                self.chemCompDS[self.idxDS[spcs]] += mol
            else :
                self.chemCompTop.append(0)
                self.chemCompBot.append(0)
                self.chemCompDS.append(0)
                self.idxDS[spcs] = self.spcsNum
                self.spcsNum += 1
                self.chemCompDS[self.idxDS[spcs]] += mol
                self.newDS.append(spcs)
                
        else :
            print("Error : Wrong Chemical Component Position")
            
            
    def addTube(self, tube):
        
        # adjust index of chemical components between tubes
        # stack newly observed species on newlist
        # add concentrations
        for i in range(len(self.chemCompList)) :
            chemComp1 = self.chemCompList[i]
            chemComp2 = tube.chemCompList[i]
            idx1 = self.idxList[i]
            idx2 = tube.idxList[i]
            new1 = self.newList[i]
            new2 = tube.newList[i]

            for spcs in idx2 :
                if spcs not in idx1 :
                    idx1[spcs] = self.spcsNum
                    new1.append(spcs)
                    self.spcsNum += 1
            
            chemComp2_new = [0]*self.spcsNum
            for spcs in idx2 :
                chemComp2_new[idx1[spcs]] = chemComp2[idx2[spcs]]
            
            self.adjustChemCompLen()
            self.chemCompList[i] = (np.array(chemComp1) + np.array(chemComp2_new)).tolist()
            
        # Replace chemComp object
        self.chemCompTop = self.chemCompList[0]
        self.chemCompBot = self.chemCompList[1]
        self.chemCompDS = self.chemCompList[2]
 
#         # Check new component
#         # If speed is slow, move this part to adjustBwTubes
#         for i in range(len(self.idxList)) :
#             for spcs in tube.idxList[i] :
#                 if spcs not in self.idxList[i] :
#                     self.newList[i].append(spcs)
        
        # add volume
        self.vol += tube.vol
    
    
    def divideTube(self, vol):
        
        if vol > self.vol :
            print "Error : Dividing volume is larger than original volume"
            return
        
        out = DNATube_GPU()
        ratio = vol/float(self.vol)

        out.chemCompTop[:] = [ i*ratio for i in self.chemCompTop ]
        out.chemCompBot[:] = [ i*ratio for i in self.chemCompBot ]
        out.chemCompDS[:] = [ i*ratio for i in self.chemCompBot ]
        self.chemCompTop[:] = [ i*(1-ratio) for i in self.chemCompTop ]
        self.chemCompBot[:] = [ i*(1-ratio) for i in self.chemCompBot ]
        self.chemCompDS[:] = [ i*(1-ratio) for i in self.chemCompDS ]
        out.spcsNum = self.spcsNum
            
        out.idxTop = self.idxTop.copy()
        out.idxBot = self.idxBot.copy()
        out.idxDS = self.idxDS.copy()
        out.idxList = [out.idxTop, out.idxBot, out.idxDS]
        
        out.newTop[:] = self.newTop[:]
        out.newBot[:] = self.newBot[:]
        out.newDS[:] = self.newDS[:]
        
        self.vol -= vol
        out.vol += vol
        
        return out
    
    
    def copyTube(self, vol):
        
        out = DNATube_GPU()
        ratio = vol/float(self.vol)
        
        out.chemCompTop[:] = [ i*ratio for i in self.chemCompTop ]
        out.chemCompBot[:] = [ i*ratio for i in self.chemCompBot ]
        out.chemCompDS[:] = [ i*ratio for i in self.chemCompBot ]
        out.spcsNum = self.spcsNum
        
        out.idxTop = self.idxTop.copy()
        out.idxBot = self.idxBot.copy()
        out.idxDS = self.idxDS.copy()
        out.idxList = [out.idxTop, out.idxBot, out.idxDS]
        
        out.newTop[:] = self.newTop[:]
        out.newBot[:] = self.newBot[:]
        out.newDS[:] = self.newDS[:]
        
        out.vol += vol
        
        return out
    
            
    def adjustChemCompLen(self):
        
        for chemComp in self.chemCompList :
            while len(chemComp) < self.spcsNum :
                chemComp.append(0)
                
                
    def getConcSum(self, pos):
        if pos == "T" :
            return sum(self.chemCompTop)
        elif pos == "B" :
            return sum(self.chemCompBot)
        elif pos == "DS" :
            return sum(self.chemCompDS)
        elif pos == "All" :
            return sum(self.chemCompTop) + sum(self.chemCompBot) + sum(self.chemCompDS)
        else :
            print("Error : Wrong Chemical Component Position")
        
    def getSpcNum(self, pos):
        if pos == "T" :
            return len(self.chemCompTop)
        elif pos == "B" :
            return len(self.chemCompBot)
        elif pos == "DS" :
            return len(self.chemCompDS)
        elif pos == "All" :
            return len(self.chemCompTop) + len(self.chemCompBot) + len(self.chemCompDS)
        else :
            print("Error : Wrong Chemical Component Position")
            
    def getTotalChemComp(self):
        
        return (np.array(self.chemCompTop) + np.array(self.chemCompBot) + np.array(self.chemCompDS)).tolist()
    
    def plotDistribution(self, pos, binsize):
        
        if pos == "T" :
            sel = 0
        elif pos == "B" :
            sel = 1
        elif pos == "DS" :
            sel = 2
        elif pos == "All" :
            self.plotDistributionAll()
        else :
            print("Error : Wrong Chemical Component Position")
        
        chemComp = self.chemCompList[sel]
        n,b,p = plt.hist(chemComp, bins=range(min(chemComp), max(chemComp)+binsize, binsize), normed=True)
        print n
        print b
        print p
        plt.show()
        
        
        
if __name__ == '__main__' :
    
    a = DNATube_GPU()
    a.addSubstance("1_2_3", 50, "T")
    a.addSubstance("1_2_3", 50, "B")
    b = DNATube_GPU()
    b.addSubstance("2_3_4", 50, "T")
    b.addSubstance("1_2_3", 50, "B")
    b.addSubstance("2_3_4", 50, "B")
    
    a.addVolume(50)
    b = a.divideTube(20)
#     a.plotDistribution("T", 6)
   
    a = [10, 20]
    print sum(a)