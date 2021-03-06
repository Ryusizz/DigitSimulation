'''
Created on 2014. 12. 30.

@author: Ryuja
'''

import random
from string import join
import time
from timeit import default_timer as timer

from Classifier import Classifier
from DNATube_GPU import DNATube_GPU
from DataModule import DataModule
from Operator_GPU import Operator_GPU 
from ParaModule import ParaModule
from Tube import Tube
import numpy as np


# from guppy import hpy
class ExpModule_GPU :
    
    def __init__(self, pm, isChasing):
        
        self.pm = pm
        self.isChasing = isChasing


    def loadTrain(self, trainData):
        self.trainData = trainData
    def loadTest(self, testData):
        self.testData = testData
        
        
    def experimentIteration(self):
#         hp = hpy()
#         print("Heap at the beginning of the function\n", hp.heap())
        for r in self.pm.get("rp") :
            for cyc in self.pm.get("cyc") :
                for trt in self.pm.get("trTimes") :
                    for tst in self.pm.get("tsTimes") :
                        for trExpt in self.pm.get("trexpTimes") :
                            for tsExpt in self.pm.get("tsexpTimes") :
                                self.experiment(r, cyc, trt, tst, trExpt, tsExpt)
#         print("Heap at the end of the function\n", hp.heap())
                        
    def experiment(self, r, cyc, trt, tst, trExpt, tsExpt):
        
        print "\tPrepare Training & Test Tube..."
        trTubes = self.prepare(r, cyc, trt, tst, trExpt, tsExpt)
        print("\tRun %d cycle..." % cyc)
        self.run(trTubes, cyc, tst, tsExpt)
        
        
        
        
        
        
        
    
    
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
        isDNATube = self.pm.get("isDNATube")
         
        trTubes = [None] * clsNum    
        for i in range(clsNum) :
            cls = self.trainData[i][1][0][0]
            lblPrf = "tr_c" + str(cls)
            if isDNATube :
                trTubes[i] = self.makeDNATubesFromData(lblPrf, "B", self.trainData[i][0], cls, cyc/2, trt, trExpt)
            else :
                trTubes[i] = self.makeTubesFromData(lblPrf, "B", self.trainData[i][0], cls, cyc/2, trt, trExpt)
        
        trTubesShuffle = list()
        for tubes in trTubes :
            trTubesShuffle.extend(tubes)
        random.shuffle(trTubesShuffle) # Training data is shuffled
        
#         tsTubes = [None] * clsNum
#         for i in range(clsNum) :
#             cls = self.testData[i][1][0][0]
#             lblPrf = "ts_c" + str(cls)
#             tsTubes[i] = self.makeTubesFromData(lblPrf, "B", self.testData[i][0], cls, cyc, trt, trExpt)
        
        return trTubesShuffle #, tsTubes
    
            
            
            
    def run(self, trTubes, cyc, tst, tsExpt):

        cls = self.pm.get("cls")
        dim = self.pm.get("dim")
        conc = self.pm.get("conc")
        vol = self.pm.get("vol")
        dvol = self.pm.get("dvol")
        dThres = self.pm.get("dThres")
        tag = self.pm.get("tag")
        sepY = self.pm.get("sepY")
        rThres = self.pm.get("rThres")
        rTime = self.pm.get("rTime")
        isDNATube = self.pm.get("isDNATube")
        isRecordReact = self.pm.get("isRecordReact")
        clsNum = len(cls)

        dm = DataModule()
        ftrain = dm.makeTrainSummaryFile(tag)
        ftest = dm.makeTestSummaryFile(tag)
        
        HN = [None] * clsNum
        print("\t\tMaking Initial Random Hypernetworks...")
        for i in range(clsNum) :
            if isDNATube :
                HN[i] = Operator_GPU.makeRandomLibraryOnDNATube(dim, conc, vol, rThres, "T")
            else :
                HN[i] = Operator_GPU.makeRandomLibraryOnTube(dim, conc, vol, rThres)
            HN[i].setLabel("Hypernetworks" + str(cls[i]))
        
        
        print("\t\tStart Learning Cycle...")
        for i in range(cyc) :
            
            start = timer()
            
            summaryCycle = list()
            summaryCycle.append(i+1)
            for j in range(clsNum) :
                if isDNATube :
                    summaryCycle.append(HN[j].getSpcNum("T"))
                    summaryCycle.append(HN[j].getConcSum("T"))
                else :
                    summaryCycle.append(HN[j].getSpcNum())
                    summaryCycle.append(HN[j].getConcSum())
                
            print("\t\t%dth Cycle" % (i+1))
            subHN = [None] * clsNum
            DList = [None] * clsNum
            
            for j in range(clsNum) :
                print("\t\t\tFor Class %d Hypernetwork" % cls[j])
                tr = trTubes[i]
                
                subHN[j] = HN[j].divideTube(dvol)
                subHN[j].setLabel("HN" + str(cls[j]) + "_learningcycle" + str(i+1))
                print "\t\t\tPour training tube..."
                subHN[j].addTube(tr)
                print "\t\t\tReacting..."
                rTimeEnd = Operator_GPU.reactionSSA(subHN[j], rTime, tag, isRecordReact)
                summaryCycle.append(rTimeEnd)
                print "\t\t\tElectrophoresis..."
                DList[j] = Operator_GPU.separation(subHN[j], sepY)
                
            csf = Classifier()
            if isDNATube :
                score, predict = csf.thresholdClassifyOnDNATube(DList, cls, dThres)
            else :
                score, predict = csf.thresholdClassifyOnTube(DList, cls, dThres)
                
            for j in range(clsNum) :
                summaryCycle.append(score[j])
            summaryCycle.append(predict)
            summaryCycle.append(tr.cls)
            
            print("\t\t\tFeedback...")
            update = [None] * clsNum
            for j in range(clsNum) :
                if isDNATube :
                    DList[j] = Operator_GPU.PCR_DNA(DList[j])
                    update[j] = Operator_GPU.denaturationOnDNATube(DList[j], "T", dvol)
                else :
                    DList[j] = Operator_GPU.PCR(DList[j])
                    update[j] = Operator_GPU.denaturationOnTube(DList[j], "T", dvol)
                
             
            if predict == tr.cls :
                for j in range(clsNum) :
                    if cls[j] == predict :
                        Operator_GPU.amplification(update[j], 8) #TODO: Tune multiply number
                        HN[j].addTube(update[j]) 
                    else :
                        Operator_GPU.amplification(update[j], 1)
                        HN[j].addTube(update[j])
            else :
                for j in range(clsNum) :
                    if cls[j] == predict :
                        Operator_GPU.amplification(update[j], 0)
                        HN[j].addTube(update[j])
                    else :
                        Operator_GPU.amplification(update[j], 1)
                        HN[j].addTube(update[j])
            
            # Test with test data
            # don't update Hypernetwork
            print("\t\t\tTesting...")
            self.test(i, HN, tst, tsExpt, ftest)
            
            trTubes[i] = None   # Discard used tube
            end = timer()
            dt = end-start
            print("\t\t\ttime elapsed %f s" % dt)
            summaryCycle.append(dt)
            
            dm.saveTrainSummaryLine(ftrain, summaryCycle)
            
        ftrain.close()
        ftest.close()
    
    
    
    def test(self, cyc, HN, tst, tsExpt, ftest):
        
        tsPerCyc = self.pm.get("tsPerCyc")
        cls = self.pm.get("cls")
        dvol = self.pm.get("dvol")
        tag = self.pm.get("tag")
        rTime = self.pm.get("rTime")
        sepY = self.pm.get("sepY")
        dThres = self.pm.get("dThres")
        isRecordReact = self.pm.get("isRecordReact")
        isDNATube = self.pm.get("isDNATube")
        clsNum = len(cls)
        
        # Prepare test Tubes
        tsTubes = list()
        for i in range(clsNum) :
            c = self.testData[i][1][0][0]
            lblPrf = "ts_cyc" + str(cyc)
            if isDNATube :
                tsTubes.extend(self.makeDNATubesFromData(lblPrf, "B", self.testData[i][0], c, tsPerCyc/2, tst, tsExpt))
            else :
                tsTubes.extend(self.makeTubesFromData(lblPrf, "B", self.testData[i][0], c, tsPerCyc/2, tst, tsExpt))
        random.shuffle(tsTubes)
        
        # Run Test
#         print("\t\t\t\tRunning test reaction...")
        testSummary = np.zeros((clsNum,clsNum))
        for i in range(tsPerCyc) :
            print("\t\t\t\t%dth test" % (i+1))
            subHN = [None]*clsNum
            DList = [None]*clsNum
            
            for j in range(clsNum) :
                ts = tsTubes[i]
                subHN[j] = HN[j].copyTube(dvol)
                subHN[j].setLabel("HN" + str(cls[j]) + "_Cycle" + str(cyc+1) + "_test" + str(i+1))
#                 print "\t\t\t\tPour test tube..."
                subHN[j].addTube(ts)
#                 print "\t\t\t\tReacting..."
                Operator_GPU.reactionSSA(subHN[j], rTime, tag, isRecordReact)
#                 print "\t\t\t\tElectrophoresis..."
                DList[j] = Operator_GPU.separation(subHN[j], sepY)
                
            csf = Classifier()
            if isDNATube :
                score, predict = csf.thresholdClassifyOnDNATube(DList, cls, dThres)
            else :
                score, predict = csf.thresholdClassifyOnTube(DList, cls, dThres)

            testSummary[cls.index(predict)][cls.index(ts.cls)] += 1
            tsTubes[i] = None
            
        # Save Result
        dm.saveTestSummaryLine(ftest, cyc, testSummary)
                        
            
            
    def makeDNATubesFromData(self, lblPrf, pos, data, cls, cyc, t, expt):
        
        dim = self.pm.get("dim")
        HEnum = self.pm.get("HEnum")
        conc = self.pm.get("conc")
        
        random.seed()
        random.shuffle(data)
        
        tubes = [None] * cyc
        
        for i in range(cyc) :
            tubes[i] = DNATube_GPU()
            for j in range(t) :
                d = data[i*t + j]
                for k in range(expt) :
                    idx = [ (p/dim, p%dim) for p in np.random.choice(dim**2, HEnum, replace=False) ]
                    HE = join([ str(idx[m][0]) + '_' + str(idx[m][1]) + '_' + str(d[idx[m]]) for m in range(HEnum) ], '__')
                    tubes[i].addSubstance(HE, conc, pos)
                    tubes[i].setClass(cls)
            
            tubes[i].setLabel(lblPrf + "_cycle" + str(cyc+1))
            
        return tubes
    
            
    def makeTubesFromData(self, lblPrf, pos, data, cls, cyc, t, expt):
        
        dim = self.pm.get("dim")
        HEnum = self.pm.get("HEnum")
        
        random.seed()
        random.shuffle(data)
        
        tubes = [None] * cyc
        
        for i in range(cyc) :
            tubes[i] = Tube()
            for j in range(t) :
                d = data[i*t + j]
                for k in range(expt) :
                    idx = [ (p/dim, p%dim) for p in np.random.choice(dim**2, HEnum, replace=False) ]
                    HE = join([ str(idx[m][0]) + '_' + str(idx[m][1]) + '_' + str(d[idx[m]]) for m in range(HEnum) ], '__')
                    HE += "/" + pos
#                     print HE
                    tubes[i].addSubstance(HE, self.pm.get("conc"))
                    tubes[i].setClass(cls)
#                 tubes[i].addVolume(self.pm.get("dvol"))
            
            tubes[i].setLabel(lblPrf + "_cycle" + str(cyc+1))
                
        return tubes
    
    
if __name__ == '__main__':
    
#     expTag = raw_input("\n\n\n---Input the tag of this experiment\n")
#     if not expTag :
#         expTag = str(time.time())
        
    expTag = str(time.time())
    params = ["cls", [6,7],     # Class
              "dim", 8,         # Dimension of Digit
              "rp", [1],        # Repeat number of whole experiment
              "tsPerCyc", 10,   # Number of test tubes per cycle
              "trTimes", [1],   # Number of training image per tube
              "tsTimes", [1],   # Number of test image per tube
              "trexpTimes", [20],  # Number of Hyperedges per training image
              "tsexpTimes", [20],  # Number of Hyperedges per test image
              "cyc", [4],      # Number of cycle per one experiment
              "HEnum", 3,       # Order of Hyperedge
              "conc", 10000,    # Random Hypernetworks concentration
              "vol", 100,       # Hypernetworks volume
              "dvol", 1,        # Volume Delta while cycle 
              "dThres", 2,      # Determination Threshold
              "rThres", 0.001,  # Random Hypernetworks Threshold
              "rTime", 1,    # Reaction Time
              "sepY", 1,        # Separation yield
              "isRecordReact", True,   # Whether record reactions or not
              "isDNATube", True,        # Whether use DNATube of Tube
              "tag", expTag     # Experiment tag
              ]
    
    pm = ParaModule(params)
    dm = DataModule()
    em = ExpModule_GPU(pm, isChasing=False)
    
    dm.saveParams(pm)
    print "Data loading..."
    em.loadTrain(dm.loadImages("bwtrain_c67_sz8_bw75.dat"))
    em.loadTest(dm.loadImages("bwtest_c67_sz8_bw75.dat"))
    
    print "Start Experiment..."
    em.experimentIteration()
    