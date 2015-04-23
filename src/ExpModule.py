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
from Classifier import Classifier


class ExpModule :
    
    def __init__(self, pm):
        
        self.pm = pm


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
        print "--Prepare Training & Test Tube"
        trTubes, tsTubes = self.prepare(r, cyc, trt, tst, trExpt, tsExpt)
        print("--Run %d cycle" % cyc)
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
    
    
#     def prepare(self, r, cyc, trt, tst, trExpt, tsExpt):
#          
#         clsNum = len(self.pm.get("cls"))
#          
#         trTubes = [None] * clsNum
#         for i in range(clsNum) :
#             cls = self.trainData[i][1][0][0]
#             lblPrf = "tr_c" + str(cls)
#             trTubes[i] = self.makeTubesFromData(lblPrf, "Top", self.trainData[i][0], cls, cyc, trt, trExpt)
#             Tube.recordTubes(trTubes[i], "TrainingTube_c" + str(cls), self.pm.get("tag"))
#          
#         tsTubes = [None] * clsNum    
#         for i in range(clsNum) :
#             cls = self.testData[i][1][0][0]
#             lblPrf = "ts_c" + str(cls)
#             tsTubes[i] = self.makeTubesFromData(lblPrf, "Bot", self.testData[i][0], cls, cyc, tst, tsExpt)
#             Tube.recordTubes(tsTubes[i], "TestTube_c" + str(cls), self.pm.get("tag"))
#              
#         return trTubes, tsTubes

    
    def prepare(self, r, cyc, trt, tst, trExpt, tsExpt):
         
        clsNum = len(self.pm.get("cls"))
         
        trTubes = [None] * clsNum
        for i in range(clsNum) :
            cls = self.trainData[i][1][0][0]
            lblPrf = "tr_c" + str(cls)
            trTubes[i] = self.makeTubesFromData(lblPrf, "T", self.trainData[i][0], cls, cyc, trt, trExpt)
         
        tsTubes = [None] * clsNum    
        for i in range(clsNum) :
            cls = self.testData[i][1][0][0]
            lblPrf = "ts_c" + str(cls)
            tsTubes[i] = self.makeTubesFromData(lblPrf, "B", self.testData[i][0], cls, cyc/2, tst, tsExpt)
        
        tsTubesShuffle = list()
        for tubes in tsTubes :
            tsTubesShuffle.extend(tubes)
        random.shuffle(tsTubesShuffle)
        
        return trTubes, tsTubesShuffle
            
            
            
    def run(self, trTubes, tsTubes, cyc):

        cls = self.pm.get("cls")
        clsNum = len(cls)
        
        HN = [None] * clsNum
        for i in range(clsNum) :
            HN[i] = Tube()
            HN[i].setLabel("Hypernetwork" + str(cls[i]))
        
        for i in range(cyc) :
            print("--%dth Cycle" % (i+1))
            tr = [None] * clsNum
            ts = [None]
            subHN = [None] * clsNum
            D = [None] * clsNum
            
            for j in range(clsNum) :
                print("-For Class %d Hypernetwork" % cls[j])
                tr[j] = trTubes[j][i]
                ts = tsTubes[i]
                
                Operator.mutation(tr[j], 1)
                HN[j].addTube(tr[j])
                print HN[j].chemComp, HN[j].vol
                subHN[j] = HN[j].divideTube(10)
                print HN[j].chemComp, HN[j].vol
                subHN[j].setLabel("learningcycle" + str(i+1))
                print "Pour test tube..."
                subHN[j].addTube(ts)
                print "Reacting..."
                Operator.reactionSSA(subHN[j], 1e-9, self.pm.get("tag")) #TODO: compensate arg time
                print "Electrophoresis..."
                D[j] = Operator.separation(subHN[j], 0.5)
                
            csf = Classifier()
            predict = csf.thresholdClassify(D, cls, 2) #TODO: Use threshold parameter
            print predict, ts.cls
            
#             update = [None] * clsNum
#             for j in range(clsNum) :
#                 update[j] = Operator.denaturation(D[j], "T", 10) #TODO: Use Volume parameter
#             
#             if predict == ts.cls :
#                 for j in range(clsNum) :
#                     if cls[j] == predict :
#                         Operator.amplification(update[j], 2)
#                         HN[j].addTube(update[j]) #TODO: Tune multiply number
#                     else :
#                         HN[j].addVolume(10)
#             else :
#                 for j in range(clsNum) :
#                     if cls[j] == predict :
#                         Operator.amplification(update[j], 1/2)
#                         HN[j].addTube(update[j])
#                     else :
#                         HN[j].addVolume(10)
            
            for hn in HN :
                print hn.getTotalConc()   
        
    
        
#     def makeTubesFromData(self, lblPrf, pos, data, cls, cyc, t, expt):
#         
#         dim = self.pm.get("dim")
#         HEnum = self.pm.get("HEnum")
#         
#         random.seed()
#         random.shuffle(data)
#         
#         tubes = [None] * cyc
#         
#         for i in range(cyc) :
#             tubes[i] = Tube()
#             for j in range(t) :
#                 d = data[i*cyc + j]
#                 for k in range(expt) :
#                     idx = [ (p/dim, p%dim) for p in np.random.choice(dim**2, HEnum, replace=False) ]
#                     HE = join([ str(idx[m][0]) + '_' + str(idx[m][1]) + '_' + str(d[idx[m]]) for m in range(HEnum) ], '__')
#                     tubes[i].addSubstance(HE, 1000, 0, pos)
#                     tubes[i].setClass(cls)
#                 tubes[i].addVolume(10)
#             
#             tubes[i].setLabel(lblPrf + "_cycle" + str(cyc+1))
#                 
#         return tubes
    
    
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
                    HE += "/" + pos
#                     print HE
                    tubes[i].addSubstance(HE, 1000)
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
              "trTimes", [5],
              "tsTimes", [5],
              "trexpTimes", [5],
              "tsexpTimes", [5],
              "cyc", [2],
              "HEnum", 3,
              "tag", expTag
              ]
    
    pm = ParaModule(params)
    dm = DataModule()
    em = ExpModule(pm)
    
    print "---Data loading"
    em.loadTrain(dm.loadImages("bwtrain_c67_sz8_bw75.dat"))
    em.loadTest(dm.loadImages("bwtest_c67_sz8_bw75.dat"))
    
    print "---Start Experiment"
    em.experimentIteration()