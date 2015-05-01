'''
Created on 2015. 1. 28.

@author: Ryuja
'''
# import stochpy

from collections import Counter
import random
from timeit import default_timer as timer

from numba import cuda

from DataModule import DataModule
from SSAModule import SSAModule
from Tools import Tools
from Tube import Tube
import numpy as np
from __builtin__ import staticmethod


class Operator(object):
    '''
    classdocs
    '''


    def __init__(self, params):

        pass
    
#     @staticmethod
#     def reactionSSA(tube, time, tag):
#         
#         try :
#             tube.toPSC(tube.lbl, tag)
#         except AttributeError :
#             print "Error : tube doesn't have label"
#                         
#         smod = stochpy.SSA(IsInteractive=False)
#         smod.Model(File=tube.lbl + "_reaction", 
#                    dir="E:\Dropbox\DigitSimulation.ver3\src\Data\Exp\\"+ tag)
#         smod.DoStochSim(end=time, mode="time")
#         print smod.data_stochsim.species_means
#         smod.PlotSpeciesDistributions(IsLegend=False)
#         smod.PlotSpeciesTimeSeries(IsLegend=False)
#         stochpy.plt.show()
    
    
    @staticmethod
    def reactionSSA(tube, time, tag):
        
        print("\t\t\t\tCast Number of Chemical Species to Integer")
        Tools.integerize(tube.chemComp)
        print("\t\t\t\tAppending")
        Tools.appendProduct(tube.chemComp)
        reverse = False
        print("\t\t\t\tFinding Reaction")
        tube.R = Tools.findReactions(tube.chemComp, reverse)
        
        print("\t\t\t\tStart SSA")
        if tube.R :
            ssam = SSAModule()
            dm = DataModule()

            molCounts, items, rTimeEnd = ssam.lottkaVolterraSSA(tube, time)
            dm.saveMolCounts(molCounts, items, tag, tube.lbl)
#             Tools.plotReactionProcess(molCounts)
            
            return rTimeEnd
        
        else :
            print "Error : Tube doesn't have reactions"
            
    
    
    @staticmethod
    def reactionODE(tube, time, tag):
        
        pass
        
            
    
#     @staticmethod
#     def separation_old(tube, pos, yd):
#         
#         tubeOut = Tube()
#         
#         if pos == "Top" :
#             for spcs in tube.chemCompDS :
#                 [top, bot] = spcs.split('/')
#                 tubeOut.chemCompTop[top] += tube.chemCompDS[spcs]
#                 tube.chemCompBot[bot] += tube.chemCompDS[spcs]
#                 del tube.chemCompDS[spcs]
#         elif pos == "Bot" :
#             for spcs in tube.chemCompDS :
#                 [top, bot] = spcs.split('/')
#                 tube.chemCompTop[top] += tube.chemCompDS[spcs]
#                 tubeOut.chemCompBot[bot] += tube.chemCompDS[spcs]
#                 del tube.chemCompDS[spcs]
#         else :
#             print "Error : Wrong Chemical Component Position"
#             
#         
#         return tubeOut
        
    
    @staticmethod
    def separation(tube, y):
        
        sp = Counter()
                
        for spc in tube.chemComp.keys() :
            [oligo, pos] = spc.split("/")
            if pos == "D" :
                sp[spc] = tube.chemComp[spc]*y

        #TODO: Subtractive separation        
        return sp
        
        
    #TODO: Test Required 
    @staticmethod
    def denaturation(D, pos, vol):
        
        tubeOut = Tube()
        
        for spc in D.keys() :
            [oligo, _] = spc.split("/")
            [top, bot] = oligo.split("___")
            if pos == "T" :
                tubeOut.addSubstance(top + "/T", D[spc])
            elif pos == "B" :
                tubeOut.addSubstance(bot + "/B", D[spc])
            else :
                print "Error : Position error"
                
        tubeOut.addVolume(vol)
        
        return tubeOut
    
        
    @staticmethod
    def amplification(tube, time):
        
        for spcs in tube.chemComp :
            tube.chemComp[spcs] *= time
    
    
    @staticmethod
    def PCR(D):
        
        Dp = Counter()
        
        for spc in D.keys() :
            [oligo, _] = spc.split("/")
            [top, bot] = oligo.split("___")
            pcrTop = top + "___" + top + "/D"
            pcrBot = bot + "___" + bot + "/D"
            Dp[pcrTop] = Dp.get(pcrTop, 0) + D[spc]
            Dp[pcrBot] = Dp.get(pcrBot, 0) + D[spc]
        
        return Dp
    
    
    @staticmethod
    def makeRandomLibrary(dim, conc, vol, thres):
        
        E = [None] * 2 * dim**2
        
        for i in range(dim) :
            for j in range(dim) :
                E[2*(i*dim+j)+0] = str(i) + "_" + str(j) + "_0"
                E[2*(i*dim+j)+1] = str(i) + "_" + str(j) + "_1"
        
        randomTube = Tube()
        random.seed()
        for e1 in E :
            for e2 in E :
                for e3 in E :
                    if e1[:-1] != e2[:-1] and e1[:-1] != e3[:-1] and e2[:-1] != e3[:-1] :
                        if random.random() > (1-thres) :
                            randomTube.addSubstance(e1 + "__" + e2 + "__" + e3 + "/T", random.normalvariate(conc, conc/4))
        
        randomTube.addVolume(vol)
        
        return randomTube
    
    
    @staticmethod
    def discardTube(tube):
        
        del tube


if __name__ == '__main__' :
    
#     start = timer()
#     tube = Operator.makeRandomLibrary[100, 100](8, 100, 50, 0.01)
#     dt = timer() - start
#     print len(tube.chemComp)
#     print tube.getTotalConc()
#     print("time elapsed %f s" % dt)
    
#     rand = Operator.makeRandomLibrary(8, 100, 50, 0.005)
#     print len(rand.chemComp)
#     Tools.appendProduct(rand.chemComp)
#     print len(rand.chemComp)

#     tube = Tube()
#     d = Counter({"1__2__3___1__2__42323/D" : 3})
#     tube.chemComp = d
#     Operator.discardTube(tube)
#     print tube
    
    a = np.zeros((2,2))
    a[0][1] = 1
    print a
    print a[0][0]
    