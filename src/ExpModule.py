'''
Created on 2014. 12. 30.

@author: Ryuja
'''

class ExpModule :
    
    def __init__(self, params):
        
        self.params = params
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
        
        
    def experiment(self):
        
        for r in self.params.rp :
            for trt in self.params.trTimes :
                for tst in self.params.tsTimes :
                    for trExpt in self.params.trexpTimes :
                        for tsExpt in self.params.tsexpTimes :
                            self.expOne(r, trt, tst, trExpt, tsExpt)
        
                        
    def expOne(self, r, trt, tst, trExpt, tsExpt):
        
        tubes = self.train(trt, trExpt)
        self.test(tubes, tst, tsExpt)
    
    
    def train(self, trt, trExpt):
        
        pass
    
    def test(self, tubes, tst, tsExpt):
        
        pass                
        
        
    
    
if __name__ == '__main__':
    pass