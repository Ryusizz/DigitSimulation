'''
Created on 2015. 1. 28.

@author: Ryuja
'''
import stochpy

from Tube import Tube


class Operator(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
    
    @staticmethod
    def reactionSSA(tube, time, tag):
        
        try :
            tube.toPSC(tube.lbl, tag)
        except AttributeError :
            print "Error : tube doesn't have label"
                        
        smod = stochpy.SSA(IsInteractive=False)
        smod.Model(File=tube.lbl + "_reaction", 
                   dir="E:\Dropbox\DigitSimulation.ver3\src\Data\Exp\\"+ tag)
        smod.DoStochSim(end=time, mode="time")
        print smod.data_stochsim.species_means
        smod.PlotSpeciesDistributions(IsLegend=False)
        smod.PlotSpeciesTimeSeries(IsLegend=False)
        stochpy.plt.show()
        
    
    # Test required
    @staticmethod
    def separation(tube, pos, yd):
        
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
    def amplification(tube, time):
        
        for t in range(time) :
            for spcs in tube.chemCompTop :
                tube.chemCompTop[spcs] *= 2
            for spcs in tube.chemCompBot :
                tube.chemCompBot[spcs] *= 2
            for spcs in tube.chemCompDS :
                tube.chemCompDS[spcs] *= 2
    
    
    #TODO: implement mutation
    @staticmethod
    def mutation(tube, range):
        
        pass