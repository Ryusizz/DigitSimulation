'''
Created on 2015. 4. 8.

@author: Ryuja
'''
from collections import Counter

import Tube


class Tube(object):
    
#     path = "E:/Dropbox/DigitSimulation.ver3/src/Data/Exp/"
    R = None

    def __init__(self):
        
        self.chemComp = Counter()
        self.chemCompList = [self.chemComp]
        self.vol = 0
        self.inConc = False
     
        
    def setGlobalReactions(self, R):
        Tube.R = R
    
    def setLocalReactions(self, R):
        self.R = R
        
    def addSubstance(self, spcs, mol):
        
        if spcs in self.chemComp :
            self.chemComp[spcs] = self.chemComp[spcs] + mol
        else :
            self.chemComp[spcs] = mol
#             self.idxTop[spcs] = len(self.idxTop)

    
    def addVolume(self, vol):
        self.vol += vol
    
    def addTube(self, tube):
        
        self.chemComp += tube.chemComp
#         for spcs in tube.idxTop :
#             if spcs not in self.idxTop :
#                 self.idxTop[spcs] = len(self.idxTop)
        self.vol += tube.vol
       
        
    def divideTube(self, vol):
        
        if vol > self.vol :
            print "Error : Dividing volume is larger than original volume"
            return
        
        out = Tube()
        
        ratio = vol/float(self.vol)
        
        for spcs, mol in self.chemComp.items() :
            self.chemComp[spcs] = mol * (1-ratio)
            out.chemComp[spcs] = mol * ratio
            
#         out.idxTop = self.idxTop.copy()
#         out.idxBot = self.idxBot.copy()
        
        self.vol -= vol
        out.vol += vol
        
        return out
    
    
    def copyTube(self, vol):
        
        out = Tube()
        ratio = vol/float(self.vol)
        
        for spcs, mol in self.chemComp.items() :
            out.chemComp[spcs] = mol * ratio
        out.vol += vol
        
        return out
            
    
    
    def setLabel(self, lbl):
        self.lbl = lbl
    def setClass(self, cls):
        self.cls = cls
    def setExpTag(self, expTag):
        self.expTag = expTag
    def getConcSum(self):
        return sum(self.chemComp.values())
    def getSpcNum(self):
        return len(self.chemComp)


if __name__ == '__main__' :
    
#     t1 = Tube()
#     t2 = Tube()
#     R = {'r1' : 1}
#     Rp = {'r2' : 2}
#     t1.setGlobalReactions(R)
#     t2.setLocalReactions(Rp)
#     print t1.R
#     print t2.R
    

    pass