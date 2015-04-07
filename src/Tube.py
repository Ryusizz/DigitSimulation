'''
Created on 2014. 12. 31.

@author: Ryuja
'''
from collections import Counter
import math
import os
import sys

from PyQt4.QtGui import *
from bidict import bidict


class Tube(object):
    
    path = "E:/Dropbox/DigitSimulation.ver3/src/Data/Exp/"
    
    def __init__(self):
        
        self.chemCompTop = Counter()
        self.chemCompBot = Counter()
        self.chemCompDS = Counter()
        self.idxTop = bidict()
        self.idxBot = bidict()
#         self.idxDS = bidict()
        self.vol = 0
        self.inConc = False
        
    def addSubstance(self, spcs, mol, vol, pos):
        
        if pos == "Top" :
            if spcs in self.chemCompTop :
                self.chemCompTop[spcs] = self.chemCompTop[spcs] + mol
            else :
                self.chemCompTop[spcs] = mol
                self.idxTop[spcs] = len(self.idxTop)
        elif pos == "Bot" :
            if spcs in self.chemCompBot :
                self.chemCompBot[spcs] = self.chemCompBot.get(spcs, 0) + mol
            else :
                self.chemCompBot[spcs] = mol
                self.idxBot[spcs] = len(self.idxBot)
        else :
            print "Error : Wrong Chemical Component Position"
            
        self.vol += vol
        
        
    def addVolume(self, vol):
        
        self.vol += vol
    
    
    def addTube(self, tube):
        
        self.chemCompTop += tube.chemCompTop
        self.chemCompBot += tube.chemCompBot
        
        for spcs in tube.idxTop :
            if spcs not in self.idxTop :
                self.idxTop[spcs] = len(self.idxTop)
        for spcs in tube.idxBot :
            if spcs not in self.idxBot :
                self.idxBot[spcs] = len(self.idxBot)
        self.vol += tube.vol
        
    
    def divideTube(self, vol):
        
        if vol > self.vol :
            print "Error : Dividing volume is larger than original volume"
            return
        
        out = Tube()
        
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
        
        self.vol -= vol
        out.vol += vol
        
        return out
        
        
    def toPSC(self, fn, expTag):
        
        folder = Tube.path + expTag + "/"
        if not os.path.exists(folder) :
            os.makedirs(folder)
            
        with open(folder + fn + "_reaction.psc", 'w') as f :
            
            f.write("# Keywords\n")
            keywords = ""
            keywords += "Output_In_Conc: True\n"
            if self.inConc :
                keywords += "Species_In_Conc: True\n"
            else :
                keywords += "Species_In_Conc: False\n"
            f.write(keywords + "\n")
            del keywords
                
            f.write("# Variable species\n")
            varSpcs = ""
            for spcs in self.chemCompTop :
                varSpcs += "T" + spcs + " = " + str(self.chemCompTop[spcs]) + "\n"
            for spcs in self.chemCompBot :
                varSpcs += "B" + spcs + " = " + str(self.chemCompBot[spcs]) + "\n"
            for spcs1 in self.chemCompTop :
                for spcs2 in self.chemCompBot :
                    varSpcs += "D" + spcs1 + "___" + spcs2 + " = 0\n"
            f.write(varSpcs + "\n")
            del varSpcs
            
            f.write("# Parameter\n")
            params = ""
            for spcsTop in self.chemCompTop :
                for spcsBot in self.chemCompBot :
                    paramTag = str(self.idxTop[spcsTop]) + "_" + str(self.idxBot[spcsBot])
                    params += "K" + paramTag + " = "
                    params += str(Tube.calK(spcsTop, spcsBot, 60, 15)) + "\n"
            f.write(params + "\n")
            del params
                    
            f.write("# Reactions\n")
            reacts = ""
            for spcsTop in self.chemCompTop :
                for spcsBot in self.chemCompBot :
                    reactTag = str(self.idxTop[spcsTop]) + "_" + str(self.idxBot[spcsBot])
                    reacts += "R" + reactTag + ":\n"
                    reacts += "\t" + "T" + spcsTop + " + " + "B" + spcsBot + " > " + "D" + spcsTop + "___" + spcsBot + "\n"
                    reacts += "\t" + "K" + reactTag + "*" + "T" + spcsTop + "*" + "B" + spcsBot + "\n"
            f.write(reacts)
            del reacts
        
    def setLabel(self, lbl):
        
        self.lbl = lbl
        
    def setClass(self, cls):
        
        self.cls = cls
        
    @staticmethod
    def recordTubes(tubes, fn, expTag):
        
        folder = Tube.path + expTag + "/"
        if not os.path.exists(folder) :
            os.makedirs(folder)
            
        with open(folder + fn + ".txt", 'w') as f :
            idx = 0
            for tube in tubes :
                idx += 1
                line = "--------- Tube " + str(idx) + " ---------\n"
                line += "## Volume : " + str(tube.vol) + " microliter\n"
                
                chemCompTop = tube.chemCompTop
                line += "## Top chemical component :\n"
                for spcs in chemCompTop :
                    line += spcs + '\t' + str(chemCompTop[spcs]) + '\n' 
                line += "\n"
                
                chemCompBot = tube.chemCompBot
                line += "## Bot chemical component :\n"
                for spcs in chemCompBot :
                    line += spcs + '\t' + str(chemCompBot[spcs]) + '\n'
                line += "\n"
                
                f.write(line)
                
    # Temporary kinetic constant calculator
    @staticmethod
    def calK(spcs1, spcs2, L, t):
        
        parts1 = spcs1.split("__")
        parts2 = spcs2.split("__")
        
        c = 0
        for i in range(len(parts1)) :
            if parts1[i] == parts2[i] :
                c += 1
                
        l = (L-t) * c/float(len(parts1))
        k = 5 * (10**4) * math.sqrt(l+t)
        
        return k
    
    
    @staticmethod
    def QDisplayTubes(tubes, maxNum):
    
        app = QApplication(sys.argv)
        
        w = QWidget()
        
        l = QVBoxLayout().addWidget(w)
        
        d = QDialog()
        d.resize(500, 500)
        d.setLayout(l)
        
        sys.exit(app.exec_())
        app.exec_()
        

if __name__ == '__main__' :
    
    print Tube.calK("0_0_0", "1_2_4", 60)