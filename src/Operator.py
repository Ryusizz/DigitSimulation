'''
Created on 2015. 1. 28.

@author: Ryuja
'''
# import stochpy

from collections import Counter
import random

from DataModule import DataModule
from SSAModule import SSAModule
from Tools import Tools
from Tube import Tube


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
        
        Tools.appendProduct(tube.chemComp)
        reverse = True
        tube.R = Tools.findReactions(tube.chemComp, reverse)
        
        if tube.R :
            ssam = SSAModule()
            dm = DataModule()

            molCounts, items = ssam.lottkaVolterraSSA(tube, time)
            dm.saveMolCounts(molCounts, items, tag, tube.lbl)
            Tools.plotReactionProcess(molCounts)
            
        else :
            print "Error : Tube doesn't have reactions"
            
    
    
    @staticmethod
    def reactionODE(tube, time, tag):
        
        pass
        
            
    
    @staticmethod
    def separation_old(tube, pos, yd):
        
        tubeOut = Tube()
        
        if pos == "Top" :
            for spcs in tube.chemCompDS :
                [top, bot] = spcs.split('/')
                tubeOut.chemCompTop[top] += tube.chemCompDS[spcs]
                tube.chemCompBot[bot] += tube.chemCompDS[spcs]
                del tube.chemCompDS[spcs]
        elif pos == "Bot" :
            for spcs in tube.chemCompDS :
                [top, bot] = spcs.split('/')
                tube.chemCompTop[top] += tube.chemCompDS[spcs]
                tubeOut.chemCompBot[bot] += tube.chemCompDS[spcs]
                del tube.chemCompDS[spcs]
        else :
            print "Error : Wrong Chemical Component Position"
            
        #TODO: volume control
        
        return tubeOut
        
    
    @staticmethod
    def separation(tube, y):
        
        sp = Counter()
                
        for spc in tube.chemComp.keys() :
            [oligo, pos] = spc.split("/")
            if pos == "D" :
                sp[spc] = tube.chemComp[spc]*y

        #TODO: Volume Control
        #TODO: Subtractive separtion        
        return sp
        
        
    #TODO: Test Required 
    @staticmethod
    def denaturation(d, pos, vol):
        
        tubeOut = Tube()
        
        for spc in d.keys() :
            [oligo, _] = spc.split("/")
            [top, bot] = oligo.split("___")
            if pos == "T" :
                tubeOut.addSubstance(top + "/T", d[spc])
            elif pos == "B" :
                tubeOut.addSubstance(bot + "/B", d[spc])
            else :
                print "Error : Position error"
                
        tubeOut.addVolume(vol)
        
        return tubeOut
    
        
    @staticmethod
    def amplification(tube, time):
        
        for t in range(time) :
            for spcs in tube.chemComp :
                tube.chemComp[spcs] *= 2
    
    
    #TODO: implement mutation
    @staticmethod
    def mutation(tube, range):
        
        pass
    
    
    #TODO: Test
    @staticmethod
    def makeRandomLibrary(dim, conc, vol):
        
        E = [None] * 2 * dim**2
        
        for i in range(dim) :
            for j in range(dim) :
                E[2*(i*dim+j)+0] = str(i) + "_" + str(j) + "_0"
                E[2*(i*dim+j)+1] = str(i) + "_" + str(j) + "_1"
        
        randomTube = Tube()
        
        for e1 in E :
            for e2 in E :
                for e3 in E :
                    if e1[:-1] != e2[:-1] and e1[:-1] != e3[:-1] and e2[:-1] != e3[:-1] :
                        randomTube.addSubstance(e1 + "__" + e2 + "__" + e3 + "/T", random.normalvariate(conc, conc/4))
        
        randomTube.addVolume(vol)
        
        return randomTube


if __name__ == '__main__' :
    
    tube = Operator.makeRandomLibrary(8, 100, 50)
    print len(tube.chemComp)
    print tube.getTotalConc()