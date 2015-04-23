from Classifier import Classifier
from Operator import Operator
from SSAModule import SSAModule
from Tools import Tools
from Tube import Tube


def test_compute_propensities():
    
    R = [ 
         [["a", "b"], 3, ["p"]],
         [["a", "c"], 4, ["p"]],
         [["p"], 10, ["a", "b"]]
         ]
    
    chemComp = {"a":1, "b":2, "c":3, "p":5}
    
    sm = SSAModule()
    print sm.compute_propensities(R, chemComp)
    

def test_update():
    
    R = [ 
         [["a", "b"], 3, ["p"]],
         [["a", "c"], 4, ["p"]],
         [["p"], 10, ["a", "b"]]
         ]
    
    chemComp = {"a":1, "b":2, "c":3, "p":5}
    
    sm = SSAModule()
    sm.update(R, 2, chemComp)
    print chemComp


def test_lottkaVolterraSSA():
    
    R = [
         [["R0"], 10, ["R0", "R0"]],
         [["R0", "W0"], 0.01, ["W0", "W0"]],
         [["W0"], 10, []]
         ]
    
    maxTime = 30
    chemComp = {"R0":1000, "W0":2000}
    
    tube = Tube()
    
    tube.chemComp = chemComp
    tube.R = R
    
    sm = SSAModule()
    molCounts = sm.lottkaVolterraSSA(tube, maxTime)
    
    Tools.plotReactionProcess(molCounts)
    
    
def test_append_and_find():
    
    chemComp = {"a/T":1, "b/B":2, "c/T":3, "d/B":0}
    Tools.appendProduct(chemComp)
    print chemComp
    print Tools.findReactions(chemComp, True)
    
    
def test_separation():
    
    tube = Tube()
    chemComp = {"a/D":3, "b/T":2, "c/B":1, "d/D":5}
    tube.chemComp = chemComp
    r = Operator.separation(tube, 0.5)
    print r
    
    
def test_thresholdClassify():
    
    D1 = {"1__2__3___1__2__3/D" : 3, "1__2__3___1__2__4/D" : 4}
    D2 = {"1__2__3___1__2__3/D" : 3, "1__2__3___1__2__4/D" : 4, "1__2__3___1__3__4/D" : 4}
    D = [D1, D2]
    cls = [6, 7]
    th = 2
    
    cf = Classifier()
    print cf.thresholdClassify(D, cls, th) 
    
test_thresholdClassify()