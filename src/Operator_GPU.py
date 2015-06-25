'''
Created on 2015. 1. 28.

@author: Ryuja
'''
# import stochpy

from __builtin__ import staticmethod
from collections import Counter
import random
from timeit import default_timer as timer

from DNATube_GPU import DNATube_GPU
from DataModule import DataModule
from SSAModule_GPU import SSA
from Tools_GPU import Tools_GPU
from Tube import Tube
import numpy as np


class Operator_GPU(object):


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
    def reactionSSA(tube, time, tag, isRecordReact):
        
#         print("\t\t\t\tCast Number of Chemical Species to Integer")
        Tools_GPU.integerize(tube)
#         print("\t\t\t\tAppending")
        Tools_GPU.appendProduct(tube)
        reverse = False
#         print("\t\t\t\tFinding Reaction")
        tube.R = Tools_GPU.findReactions(tube, reverse)
        
#         print("\t\t\t\tStart SSA")
        if tube.R.shape[0] > 0 :
            
            dm = DataModule()
            if isinstance(tube, DNATube_GPU) :
                molCountsList, spcsList, headList, timeCounts, rTimeEnd = SSA(tube, time)
                if isRecordReact :
                    for i in range(len(molCountsList)) :
                        molCounts = molCountsList[i]
                        spcs = spcsList[i]
                        head = headList[i]
                        dm.saveMolCounts(molCounts, spcs, head, tag, tube.lbl)
                    dm.saveMolCounts(timeCounts, ["time"], "time", tag, tube.lbl)
                
            elif isinstance(tube, Tube) :    
                molCounts, items, rTimeEnd = SSA(tube, time)
                if isRecordReact :
                    dm.saveMolCounts(molCounts, items, "All", tag, tube.lbl)
            
#             Tools_GPU.plotReactionProcess(molCountsList[0], timeCounts)
#             Tools_GPU.plotReactionProcess(molCountsList[1], timeCounts)
#             Tools_GPU.plotReactionProcess(molCountsList[2], timeCounts)
            
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
        if isinstance(tube, DNATube_GPU) :
            for spc, idx in tube.idxDS.items() :
                try :
                    sp[spc] = tube.chemCompDS[idx] * y
                except :
                    pass
#                     print len(tube.chemCompDS), idx
        
        elif isinstance(tube, Tube) :
            for spc in tube.chemComp.keys() :
                [oligo, pos] = spc.split("/")
                if pos == "D" :
                    sp[spc] = tube.chemComp[spc]*y

        #TODO: Subtractive separation        
        return sp
        
        
    #TODO: Test Required 
    @staticmethod
    def denaturationOnDNATube(D, pos, vol):
        
        tubeOut = DNATube_GPU()
        
        for spc in D.keys() :
            [top, bot] = spc.split("___")
            if pos == "T" :
                tubeOut.addSubstance(top, D[spc], pos)
            elif pos == "B" :
                tubeOut.addSubstance(bot, D[spc], pos)
            else :
                print "Error : Position error"
                
        tubeOut.addVolume(vol)
        
        return tubeOut
    
    
    @staticmethod
    def denaturationOnTube(D, pos, vol):
        
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
        
        for chemComp in tube.chemCompList :
            for i in range(len(chemComp)) :
                chemComp[i] *= time
    
    
    @staticmethod
    def PCR_DNA(D):
        
        Dp = Counter()
        
        for spc in D.keys() :
            [top, bot] = spc.split("___")
            pcrTop = top + "___" + top + "/D"
            pcrBot = bot + "___" + bot + "/D"
            Dp[pcrTop] = Dp.get(pcrTop, 0) + D[spc]
            Dp[pcrBot] = Dp.get(pcrBot, 0) + D[spc]
        
        return Dp
    
    
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
    def makeRandomLibraryOnDNATube(dim, conc, vol, thres, pos):
        
        E = [None] * 2 * dim**2
        
        for i in range(dim) :
            for j in range(dim) :
                E[2*(i*dim+j)+0] = str(i) + "_" + str(j) + "_0"
                E[2*(i*dim+j)+1] = str(i) + "_" + str(j) + "_1"
        
        randomTube = DNATube_GPU()
        random.seed()
        for e1 in E :
            for e2 in E :
                for e3 in E :
                    if e1[:-1] != e2[:-1] and e1[:-1] != e3[:-1] and e2[:-1] != e3[:-1] :
                        if random.random() > (1-thres) :
                            randomTube.addSubstance(e1 + "__" + e2 + "__" + e3, random.normalvariate(conc, conc/4), pos)
        
        randomTube.addVolume(vol)
        
        return randomTube
    
    @staticmethod
    def makeRandomLibraryOnTube(dim, conc, vol, thres):
        
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
#     Tools_GPU.appendProduct(rand.chemComp)
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
    