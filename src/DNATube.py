'''
Created on 2014. 12. 31.

@author: Ryuja
'''
from collections import Counter
import os

from bidict import bidict

from Tube import Tube


class DNATube(Tube):
    
    path = "E:/Dropbox/DigitSimulation.ver3/src/Data/Exp/"
    
    def __init__(self):
        
        self.chemCompTop = Counter()
        self.chemCompBot = Counter()
        self.chemCompDS = Counter()
        self.chemCompList = [self.chemCompTop, self.chemCompBot, self.chemCompDS]
        
        self.idxTop = bidict()
        self.idxBot = bidict()
        self.idxDS = bidict()
        
        self.newTop = list()
        self.newBot = list()
        self.newDS = list()
        
        self.R = list()
        
        self.vol = 0
        self.inConc = False
        
        
    def addSubstance(self, spcs, mol, pos):
        
        if pos == "T" :
            if spcs in self.chemCompTop :
                self.chemCompTop[spcs] += mol
            else :
                self.chemCompTop[spcs] = mol
                self.idxTop[spcs] = len(self.idxTop)
                self.newTop.append(spcs)
        elif pos == "B" :
            if spcs in self.chemCompBot :
                self.chemCompBot[spcs] += mol
            else :
                self.chemCompBot[spcs] = mol
                self.idxBot[spcs] = len(self.idxBot)
                self.newBot.append(spcs)
        elif pos == "DS" :
            if spcs in self.chemCompDS :
                self.chemCompDS[spcs] += mol
            else :
                self.chemCompDS[spcs] = mol
                self.idxDS[spcs] = len(self.idxDS)
                self.newDS.append(spcs)
        else :
            print "Error : Wrong Chemical Component Position"
            
        
    
    def addTube(self, tube):
        
        # Add chemical component concentration
        self.chemCompTop += tube.chemCompTop
        self.chemCompBot += tube.chemCompBot
        self.chemCompDS += tube.chemCompDS
        
        # Indexing chemical component
        for spcs in tube.idxTop :
            if spcs not in self.idxTop :
                self.idxTop[spcs] = len(self.idxTop)
        for spcs in tube.idxBot :
            if spcs not in self.idxBot :
                self.idxBot[spcs] = len(self.idxBot)
        for spcs in tube.idxDS :
            if spcs not in self.idxDS :
                self.idxDS[spcs] = len(self.idxDS)
                
        # Check new component
        self.newTop.extend(tube.newTop)
        self.newBot.extend(tube.newBot)
        self.newDS.extend(tube.newDS)
        for spcs in tube.chemCompTop :
            self.newTop.append(spcs)
        for spcs in tube.chemCompBot :
            self.newBot.append(spcs)
        for spcs in tube.chemCompDS :
            self.newDS.append(spcs)
        
        # add volume
        self.vol += tube.vol
        
    
    def divideTube(self, vol):
        
        if vol > self.vol :
            print "Error : Dividing volume is larger than original volume"
            return
        
        out = DNATube()
        ratio = vol/float(self.vol)

        for spcs, mol in self.chemCompTop.items() :
            self.chemCompTop[spcs] = mol * (1-ratio)
            out.chemCompTop[spcs] = mol * ratio
        for spcs, mol in self.chemCompBot.items() :
            self.chemCompBot[spcs] = mol * (1-ratio)
            out.chemCompBot[spcs] = mol * ratio
        for spcs, mol in self.chemCompDS.items() :
            self.chemCompDS[spcs] = mol * (1-ratio)
            out.chemCompDS[spcs] = mol * ratio
            
        out.idxTop = self.idxTop.copy()
        out.idxBot = self.idxBot.copy()
        out.idxDS = self.idxDS.copy()
        
        out.newTop = self.newTop[:]
        out.newBot = self.newBot[:]
        out.newDS = self.newDS[:]
        
        self.vol -= vol
        out.vol += vol
        
        return out
    
    
    def copyTube(self, vol):
        
        out = DNATube()
        ratio = vol/float(self.vol)
        
        for spcs, mol in self.chemCompTop.items() :
            out.chemCompTop[spcs] = mol * ratio
        for spcs, mol in self.chemCompBot.items() :
            out.chemCompBot[spcs] = mol * ratio
        for spcs, mol in self.chemCompDS.items() :
            out.chemCompDS[spcs] = mol * ratio
        
        out.idxTop = self.idxTop.copy()
        out.idxBot = self.idxBot.copy()
        out.idxDS = self.idxDS.copy()
        
        out.newTop = self.newTop[:]
        out.newBot = self.newBot[:]
        out.newDS = self.newDS[:]
        
        out.vol += vol
        
        return out
    
    
    def getConcSum(self, pos):
        if pos == "T" :
            return sum(self.chemCompTop.values())
        elif pos == "B" :
            return sum(self.chemCompBot.values())
        elif pos == "DS" :
            return sum(self.chemCompDS.values())
        
    def getSpcNum(self, pos):
        if pos == "T" :
            return len(self.chemCompTop)
        elif pos == "B" :
            return len(self.chemCompBot)
        elif pos == "DS" :
            return len(self.chemCompDS)
        elif pos == "All" :
            return len(self.chemCompTop) + len(self.chemCompBot) + len(self.chemCompDS)
        
    def getChemCompListAll(self):
        
        pass
    
    
    
                
#     def toPSC(self, fn, expTag):
#         
#         folder = Tube.path + expTag + "/"
#         if not os.path.exists(folder) :
#             os.makedirs(folder)
#             
#         with open(folder + fn + "_reaction.psc", 'w') as f :
#             
#             f.write("# Keywords\n")
#             keywords = ""
#             keywords += "Output_In_Conc: True\n"
#             if self.inConc :
#                 keywords += "Species_In_Conc: True\n"
#             else :
#                 keywords += "Species_In_Conc: False\n"
#             f.write(keywords + "\n")
#             del keywords
#                 
#             f.write("# Variable species\n")
#             varSpcs = ""
#             for spcs in self.chemCompTop :
#                 varSpcs += "T" + spcs + " = " + str(self.chemCompTop[spcs]) + "\n"
#             for spcs in self.chemCompBot :
#                 varSpcs += "B" + spcs + " = " + str(self.chemCompBot[spcs]) + "\n"
#             for spcs1 in self.chemCompTop :
#                 for spcs2 in self.chemCompBot :
#                     varSpcs += "D" + spcs1 + "___" + spcs2 + " = 0\n"
#             f.write(varSpcs + "\n")
#             del varSpcs
#             
#             f.write("# Parameter\n")
#             params = ""
#             for spcsTop in self.chemCompTop :
#                 for spcsBot in self.chemCompBot :
#                     paramTag = str(self.idxTop[spcsTop]) + "_" + str(self.idxBot[spcsBot])
#                     params += "K" + paramTag + " = "
#                     params += str(Tools.calK(spcsTop, spcsBot, 60, 15)) + "\n"
#             f.write(params + "\n")
#             del params
#                     
#             f.write("# Reactions\n")
#             reacts = ""
#             for spcsTop in self.chemCompTop :
#                 for spcsBot in self.chemCompBot :
#                     reactTag = str(self.idxTop[spcsTop]) + "_" + str(self.idxBot[spcsBot])
#                     reacts += "R" + reactTag + ":\n"
#                     reacts += "\t" + "T" + spcsTop + " + " + "B" + spcsBot + " > " + "D" + spcsTop + "___" + spcsBot + "\n"
#                     reacts += "\t" + "K" + reactTag + "*" + "T" + spcsTop + "*" + "B" + spcsBot + "\n"
#             f.write(reacts)
#             del reacts
        
        

if __name__ == '__main__' :
    
    pass