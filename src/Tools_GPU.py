'''
Created on 2015. 4. 8.

@author: Ryuja
'''
import math
import os
import sys

from PyQt4.QtGui import QApplication, QWidget, QVBoxLayout, QDialog

from DNATube_GPU import DNATube_GPU
from DataModule import DataModule
from Tools import Tools
from Tube import Tube
import matplotlib.pyplot as plt
import numpy as np


class Tools_GPU(Tools):

    h = 6.626e-34 #J*s
    kB = 1.380e-23 #J*K-1
    T = 298 #K
    dG = -115e3 #cal/mole
    R = 1.987 #calK-1mol-1


    #FIXME: move this method to DataModule
    @staticmethod
    def recordTubes(tubes, fn, expTag):
        
        folder = DataModule.path + expTag + "/"
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
                
    
    @staticmethod
    def findReactions(tube, reverse):
        
        if isinstance(tube, DNATube_GPU) :
            R = Tools_GPU.__findReactionsOnDNATube(tube, reverse)
        elif isinstance(tube, Tube) :
            R = Tools_GPU.__findReactionsOnTube(tube, reverse)
            
        return R
    
    
    @staticmethod
    def findReactionMatrix(tube, reverse):
        
        if isinstance(tube, DNATube_GPU) :
            return Tools_GPU.__findReactionMatrixOnDNATube(tube, reverse)
                
    
    @staticmethod
    def __findReactionMatrixOnDNATube(tube, reverse):
        
        R = tube.R
        
        
        
        
    @staticmethod
    def __findReactionsOnTube(tube, reverse):
        
        R = list()
        spcs = tube.chemComp.keys()
        for i in range(0, len(spcs)) :
            [spc1, pos1] = spcs[i].split("/")
            
            if reverse and pos1 == "D" :
                k = 100
                p = spc1.split("___")
                p[0] = p[0] + "/T"; p[1] = p[1] + "/B"
                R.append([ [spcs[i]], k, p ])
                
            for j in range(0, len(spcs)) :
                [spc2, pos2] = spcs[j].split("/")
                if pos1 == "T" and pos2 == "B" :
                    c = Tools_GPU.match(spc1, spc2)
                    if c <= 0 :
                        continue
                    k = Tools_GPU.calK(spc1, spc2, 60, 15, c)
                    p = [spc1 + "___" + spc2 + "/D"]
                    R.append([ [spcs[i], spcs[j]], k, p ])
        
        return R
    
    
    @staticmethod
    def __findReactionsOnDNATube(tube, reverse):
        
        R = tube.R
        # R = [ reactantNum1, reactantNum2, reaction rate constant(k), productNum ]
        # If reaction is first order, reactantNum2 = 0
        # that redirect to concentration 1 
        
        for spcTop in tube.newTop :
            for spcBot in tube.idxBot :
                c = Tools_GPU.match(spcTop, spcBot)
                if c <= 0 :
                    continue
                k = Tools_GPU.calK(spcTop, spcBot, 60, 15, c)
                spcDS = spcTop + "___" + spcBot
                if spcDS not in tube.RList :
                    tube.RList.append(spcDS)
                    r = [ tube.idxTop[spcTop], tube.idxBot[spcBot], k, tube.idxDS[spcDS] ]
                    R = np.vstack((R,r))
                else :
                    print("A")
        tube.newTop[:] = [] #empty new component list
                
        for spcBot in tube.newBot :
            for spcTop in tube.idxTop :
                c = Tools_GPU.match(spcTop, spcBot)
                if c <= 0 :
                    continue
                k = Tools_GPU.calK(spcTop, spcBot, 60, 15, c)
                spcDS = spcTop + "___" + spcBot
                if spcDS not in tube.RList :
                    tube.RList.append(spcDS)
                    r = [ tube.idxTop[spcTop], tube.idxBot[spcBot], k, tube.idxDS[spcDS] ]
                    R = np.vstack((R,r))
                else :
                    print("B")
        tube.newBot[:] = []
        
        #FIXME: fit to new data structure
        if reverse :
            for spcDS in tube.newDS :
                k = 100
                p = spcDS
                r = [ [spcDS], k, p]
                if r not in R :
                    R.append(r)
            tube.newDS[:] = []
        
        return R
    
    
    @staticmethod
    def appendProduct(tube):
        
        if isinstance(tube, DNATube_GPU) :
            Tools_GPU.__appendProductOnDNATube(tube)
        elif isinstance(tube, Tube) :
            Tools_GPU.__appendProductOnTube(tube)
                        
                        
    @staticmethod
    def __appendProductOnTube(tube):
        spcs = tube.chemComp.keys()
        for i in range(0, len(spcs)) :
            for j in range(0, len(spcs)) :
                [spc1, pos1] = spcs[i].split("/")
                [spc2, pos2] = spcs[j].split("/")
                if pos1 == "T" and pos2 == "B" :
                    c = Tools_GPU.match(spc1, spc2)
                    if c <= 0 :
                        continue
                    p = spc1 + "___" + spc2 + "/D"
                    if p not in spcs :
                        tube.chemComp[p] = 0
                        
    
    @staticmethod
    def __appendProductOnDNATube(tube):
        
        for spcTop in tube.newTop :
            for spcBot in tube.idxBot :
                c = Tools_GPU.match(spcTop, spcBot)
                if c <= 0 :
                    continue
                spcDS = spcTop + "___" + spcBot
                tube.addSubstance(spcDS, 0, "DS")
        
        for spcBot in tube.newBot :
            for spcTop in tube.idxTop :
                c = Tools_GPU.match(spcTop, spcBot)
                if c <= 0 :
                    continue
                spcDS = spcTop + "___" + spcBot
                tube.addSubstance(spcDS, 0, "DS")
    
    
    @staticmethod
    def integerize(tube):
        for chemComp in tube.chemCompList :
            chemComp[:] = [ int(i) for i in chemComp ]
        
        
    
#     @staticmethod
#     def QDisplayTubes(tubes, maxNum):
#     
#         app = QApplication(sys.argv)
#         
#         w = QWidget()
#         
#         l = QVBoxLayout().addWidget(w)
#         
#         d = QDialog()
#         d.resize(500, 500)
#         d.setLayout(l)
#         
#         sys.exit(app.exec_())
#         app.exec_()
        

    #FIXME: don't stop when this method is called 
    @staticmethod
    def plotReactionProcess(X):
        
        n = np.size(X, axis=1)-1
        
        for i in range(n) :
            plt.plot(X[:, n], X[:, i])
        plt.show()
        

if __name__ == '__main__' :
#     k = Tools_GPU.kB * Tools_GPU.T /Tools_GPU.h * math.exp(-(7.89 + 0.009*Tools_GPU.dG)/(Tools_GPU.R*Tools_GPU.T))
#     print k
#     kp = Tools_GPU.calK("1__2__3", "1__2__3", 8, 8)
#     print kp
    
    tube = DNATube_GPU()
    if isinstance(tube, Tube) :
        print("Tube")
    elif isinstance(tube, DNATube_GPU) :
        print("Tube")