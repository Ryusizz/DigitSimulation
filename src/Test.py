import theano
import theano.tensor as T
import time
from timeit import default_timer as timer

from Classifier import Classifier
from Operator import Operator
from SSAModule import SSAModule
from Tools import Tools
from Tube import Tube
import numpy as np


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
    
    
def test_theanoGPU():
    
    A = np.random.rand(1000,10000).astype(theano.config.floatX)
    B = np.random.rand(10000,1000).astype(theano.config.floatX)
    np_start = time.time()
    AB = A.dot(B)
    np_end = time.time()
    X,Y = theano.tensor.matrices('XY')
    mf = theano.function([X,Y],X.dot(Y))
    t_start = time.time()
    tAB = mf(A,B)
    t_end = time.time()
    print "NP time: %f[s], theano time: %f[s] (times should be close when run on CPU!)" %(
                                               np_end-np_start, t_end-t_start)
    print "Result difference: %f" % (np.abs(AB-tAB).max(), )
    
    
def test_theanoMethod():
    
    A = T.dvector('A')
    B = T.dvector('B')
    C = A * B
    f = theano.function([A,B], C)
    print f(np.ones(5), np.array(range(5)))
    

def test_theanoElementwiseMult():
    
    N = 5000000
    A = np.asarray(np.random.rand(N), dtype=theano.config.floatX)
    B = np.asarray(np.random.rand(N), dtype=theano.config.floatX)
    np_start = time.time()
    for i in range(1000) :
        AB = np.multiply(A,B)
    np_end = time.time()
    X = theano.shared(A, borrow=True)
    Y = theano.shared(B, borrow=True)
    for i in range(1000) :
        mf = theano.function([], X*Y)
    t_start = time.time()
    tAB = mf()
    t_end = time.time()
    print "NP time: %f[s], theano time: %f[s] (times should be close when run on CPU!)" %(
                                               np_end-np_start, t_end-t_start)
    print "Result difference: %f" % (np.abs(AB-tAB).max(), )
    
    
def addOneElementTheano():
    
    Cs = theano.shared(np.asarray(np.ones((5,5))))
    row = T.iscalar("row")
    col = T.iscalar("col")
    
    update = [(Cs[row][col], Cs[row][col]+1)]
    addConc = theano.function([row, col], updates=update)
    addConc(2,3)
    print Cs.get_value()

addOneElementTheano()
print theano.config.floatX