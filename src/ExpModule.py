'''
Created on 2014. 12. 30.

@author: Ryuja
'''

import random
from string import join
import time

from DataModule import DataModule
from Operator import Operator
from ParaModule import ParaModule
from Tube import Tube
import numpy as np


class ExpModule :
    
    def __init__(self, pm):
        
        self.pm = pm
#         self.expParams.trTimes = params.trTimes
#         self.expParams.tsTimes = params.tsTimes
#         self.expParams.spSizes = params.spSizes
#         self.expParams.expRepeat = params.expRepeat
#         self.expParams.

#     def setClass(self, classList):
#         self.class1 = classList[0]
#         self.class2 = classList[1]
#     def setTrainSize(self, sizes_train):
#         self.sizes_train = sizes_train
#     def setTestSize(self, sizes_test):
#         self.sizes_test = sizes_test
#     def setSampleSize(self, sizes_sample):
#         self.sizes_sample = sizes_sample
#     def setFeatureNumber(self, nums_feature):
#         self.nums_feature = nums_feature
#     def setRepeat(self, repeat):
#         self.repeat = repeat
#     def setTestRepeat(self, test_repeat):
#         self.test_repeat = test_repeat
#     def setHyperEdgeNumber(self, n_HE):
#         self.n_HE = n_HE
#     def setIncremental(self, isIncremental):
#         self.isIncremental = isIncremental
#     def setDecremental(self, isDecremental):
#         self.isDecremental = isDecremental
#     def setSelective(self, isSelective):
#         self.isSelective = isSelective
#     def setIncreSelectThres(self, increSelectThres):
#         self.increSelectThres = increSelectThres

    def loadTrain(self, trainData):
        self.trainData = trainData
    def loadTest(self, testData):
        self.testData = testData
        
        
    def experimentIteration(self):
        
#         expTag = time.strftime("%yY%mM%dD_%Hhr%Mmin%Ssec", time.localtime())
        for r in self.pm.get("rp") :
            for cyc in self.pm.get("cyc") :
                for trt in self.pm.get("trTimes") :
                    for tst in self.pm.get("tsTimes") :
                        for trExpt in self.pm.get("trexpTimes") :
                            for tsExpt in self.pm.get("tsexpTimes") :
                                self.experiment(r, cyc, trt, tst, trExpt, tsExpt)
        
                        
    def experiment(self, r, cyc, trt, tst, trExpt, tsExpt):
        
#         clsNum = len(self.pm.get("cls"))
        
        trTubes, tsTubes = self.prepare(r, cyc, trt, tst, trExpt, tsExpt)
        self.run(trTubes, tsTubes, cyc)
        
#         tubegat = [Tube(), Tube()]
#         tubeMixed = Tube()
#         tubeMixed.addSubstance("1_1_0__0_6_0__5_2_0", 1000, 10, "Bot")            
#         for i in range(clsNum) :
#             for tube in trTubes[i] :
#                 tubegat[i].addTube(tube)
#             tubegat[i].setClass(tube.cls)
#             tubeMixed.addTube(tubegat[i])
#             tubegat[i].toPSC("TrainingTube_c" + str(tubegat[i].cls), "exp1")
#         tubeMixed.toPSC("TrainingTube_mixedTest", "exp1")
            
#         self.test(self.testData, tst, tsExpt)
        print "Testing", r, trt, tst, trExpt, tsExpt
    
    
    def prepare(self, r, cyc, trt, tst, trExpt, tsExpt):
        
        clsNum = len(self.pm.get("cls"))
        
        trTubes = [None] * clsNum
        for i in range(clsNum) :
            cls = self.trainData[i][1][0][0]
            lblPrf = "tr_c" + str(cls)
            trTubes[i] = self.makeTubesFromData(lblPrf, "Top", self.trainData[i][0], cls, cyc, trt, trExpt)
            Tube.recordTubes(trTubes[i], "TrainingTube_c" + str(cls), self.pm.get("tag"))
        
        tsTubes = [None] * clsNum    
        for i in range(clsNum) :
            cls = self.testData[i][1][0][0]
            lblPrf = "ts_c" + str(cls)
            tsTubes[i] = self.makeTubesFromData(lblPrf, "Bot", self.testData[i][0], cls, cyc, tst, tsExpt)
            Tube.recordTubes(tsTubes[i], "TestTube_c" + str(cls), self.pm.get("tag"))
            
        return trTubes, tsTubes

            
            
    def run(self, trTubes, tsTubes, cyc):

        cls = self.pm.get("cls")
        clsNum = len(cls)
        
        HN = [None] * clsNum
        for i in range(clsNum) :
            HN[i] = Tube()
            HN[i].setLabel("Hypernetwork" + str(cls[i]))
            
        for i in range(cyc) :
            tr = [None] * clsNum
            ts = [None] * clsNum
            subHN = [None] * clsNum
            
            for j in range(clsNum) :
                tr[j] = trTubes[j][i]
                ts[j] = tsTubes[j][i]
                
                Operator.mutation(tr[j], 1)
                HN[j].addTube(tr[j])
                subHN[j] = HN[j].divideTube(10)
                subHN[j].setLabel("classification_cycle" + str(i+1))
                subHN[j].addTube(ts[j])
                Operator.reactionSSA(subHN[j], 10, self.pm.get("tag")) #TODO: compensate arg time
            
        
    
        
    def makeTubesFromData(self, lblPrf, pos, data, cls, cyc, t, expt):
        
        dim = self.pm.get("dim")
        HEnum = self.pm.get("HEnum")
        
        random.seed()
        random.shuffle(data)
        
        tubes = [None] * cyc
        
        for i in range(cyc) :
            tubes[i] = Tube()
            for j in range(t) :
                d = data[i*cyc + j]
                for k in range(expt) :
                    idx = [ (p/dim, p%dim) for p in np.random.choice(dim**2, HEnum, replace=False) ]
                    HE = join([ str(idx[m][0]) + '_' + str(idx[m][1]) + '_' + str(d[idx[m]]) for m in range(HEnum) ], '__')
                    tubes[i].addSubstance(HE, 1000, 0, pos)
                    tubes[i].setClass(cls)
                tubes[i].addVolume(10)
            
            tubes[i].setLabel(lblPrf + "_cycle" + str(cyc+1))
                
        return tubes
    
if __name__ == '__main__':
    
    expTag = raw_input("\n\n\n\n---Input the tag of this experiment\n")
    if not expTag :
        expTag = str(time.time())
        
    params = ["cls", [6,7],
              "dim", 8,
              "rp", [1],
              "trTimes", [10],
              "tsTimes", [10],
              "trexpTimes", [10],
              "tsexpTimes", [10],
              "cyc", [1],
              "HEnum", 3,
              "tag", expTag
              ]
    
    pm = ParaModule(params)
    dm = DataModule()
    em = ExpModule(pm)
    
    em.loadTrain(dm.loadImages(DataModule.path, "bwtrain_c67_sz8_bw75.dat"))
    em.loadTest(dm.loadImages(DataModule.path, "bwtest_c67_sz8_bw75.dat"))
    em.experimentIteration()