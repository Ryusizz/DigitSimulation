'''
Created on 2015. 4. 8.

@author: Ryuja
'''
import math
import os
import sys

from PyQt4.QtGui import QApplication, QWidget, QVBoxLayout, QDialog

from Tube import Tube
import matplotlib.pyplot as plt
import numpy as np


class Tools(object):

    h = 6.626e-34 #J*s
    kB = 1.380e-23 #J*K-1
    T = 298 #K
    dG = -115e3 #cal/mole
    R = 1.987 #calK-1mol-1

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
                
    
    @staticmethod
    def findReactions(chemComp, reverse):
        
        R = list()
        spcs = chemComp.keys()
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
                    c = Tools.match(spc1, spc2)
                    if c <= 0 :
                        continue
                    k = Tools.calK(spc1, spc2, 60, 15, c)
                    p = [spc1 + "___" + spc2 + "/D"]
                    R.append([ [spcs[i], spcs[j]], k, p ])
        
        return R
                        
                        
    @staticmethod
    def appendProduct(chemComp):
        spcs = chemComp.keys()
        for i in range(0, len(spcs)) :
            for j in range(0, len(spcs)) :
                [spc1, pos1] = spcs[i].split("/")
                [spc2, pos2] = spcs[j].split("/")
                if pos1 == "T" and pos2 == "B" :
                    c = Tools.match(spc1, spc2)
                    if c <= 0 :
                        continue
                    p = spc1 + "___" + spc2 + "/D"
                    if p not in spcs :
                        chemComp[p] = 0
                        
    
    @staticmethod
    def integerize(chemComp):
        for spc in chemComp.keys() :
            chemComp[spc] = int(chemComp[spc])        
        
        
    # Temporary kinetic constant calculator
    @staticmethod
    def calK(spc1, spc2, L, t, c):
        
        parts1 = spc1.split("__")
        l = (L-t) * c/float(len(parts1))
        k = 5 * (10**4) * math.sqrt(l+t)
        
        return k
    
    
    @staticmethod
    def match(spc1, spc2):
    
        parts1 = spc1.split("__")
        parts2 = spc2.split("__")
        
        c = 0
        for i in range(len(parts1)) :
            if parts1[i] == parts2[i] :
                c += 1
                
        return c
    
    
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
        
    
    @staticmethod
    def plotReactionProcess(X):
        
        n = np.size(X, axis=1)-1
        
        for i in range(n) :
            plt.plot(X[:, n], X[:, i])
#         plt.show()
        plt.draw()
        

if __name__ == '__main__' :
#     k = Tools.kB * Tools.T /Tools.h * math.exp(-(7.89 + 0.009*Tools.dG)/(Tools.R*Tools.T))
#     print k
#     kp = Tools.calK("1__2__3", "1__2__3", 8, 8)
#     print kp
    
    pass