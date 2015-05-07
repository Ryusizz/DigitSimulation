'''
Created on 2015. 1. 5.

@author: Ryuja
'''
from array import array as pyarray
import os
import pickle
import scipy.misc
import struct

import matplotlib.pyplot as plt
import numpy as np


class DataModule:
    
    bwThres = None
    path = "./Data"
     
    def load_mnist(self, dataset, mode, imgSize, digits, path):
        """
        Loads MNIST files into 3D numpy arrays
     
        Adapted from: http://abel.ee.ucla.edu/cvxopt/_downloads/mnist.py
        """
     
        if dataset == "training":
            fname_img = os.path.join(path, 'train-images.idx3-ubyte')
            fname_lbl = os.path.join(path, 'train-labels.idx1-ubyte')
        elif dataset == "testing":
            fname_img = os.path.join(path, 't10k-images.idx3-ubyte')
            fname_lbl = os.path.join(path, 't10k-labels.idx1-ubyte')
        else:
            raise ValueError("dataset must be 'testing' or 'training'")
     
        flbl = open(fname_lbl, 'rb')
        magic_nr, size = struct.unpack(">II", flbl.read(8))
        lbl = pyarray("b", flbl.read())
        flbl.close()
     
        fimg = open(fname_img, 'rb')
        magic_nr, size, rows, cols = struct.unpack(">IIII", fimg.read(16))
        img = pyarray("B", fimg.read())
        fimg.close()
     
        ind = [ k for k in range(size) if lbl[k] in digits ]
        N = len(ind)
     
        images = np.zeros((N, imgSize, imgSize), dtype=np.uint8)
        labels = np.zeros((N, 1), dtype=np.int8)
        if mode == "BW" :
            for i in range(len(ind)) :
                images[i] = scipy.misc.imresize( np.array(img[ ind[i]*rows*cols : (ind[i]+1)*rows*cols ]).reshape((rows, cols)), (imgSize,imgSize), "bilinear" )
                images[i] = self.img2bw(images[i], self.bwThres)
                labels[i] = lbl[ind[i]]
        else :
            for i in range(len(ind)):
                images[i] = scipy.misc.imresize( np.array(img[ ind[i]*rows*cols : (ind[i]+1)*rows*cols ]).reshape((rows, cols)), (imgSize,imgSize) )
                labels[i] = lbl[ind[i]]
     
        return images, labels
     
     
    def img2bw(self, img, thres) :
         
        idx = np.where(img > thres)
         
        bwImg = np.zeros(img.shape)
        bwImg[idx] = 1
         
        return bwImg
    
    
    def saveImages(self, imgs, path, fname):
        
        try : 
            with open(path + "/" + fname, 'wb') as fout :
                pickle.dump(imgs, fout)
        except IOError as err :
            print("File error : " + str(err))
        except pickle.PickleError as perr :
            print("pickling error : " + str(perr))
            
    
    def loadImages(self, fname):

        try :
            with open(self.path + "/" + fname, 'rb') as fin :
                imgs = pickle.load(fin)
                return imgs
        except IOError as err :
            print("File error : " + str(err))
        except pickle.PickleError as perr :
            print("pickling error : " + str(perr))

    
    def display(self, img):
        
        plt.imshow(img, cmap='Greys')
        plt.show()
        
    
    def saveMolCounts(self, molCounts, items, head, expTag, fname):
        
        folder = self.path + "/Exp/" + expTag + "/" + fname
        if not os.path.exists(folder) :
            os.makedirs(folder)
            
        try :
            with open(folder + "/" + head + ".txt", 'w') as fout :
                fout.write('\t'.join(x for x in items) + '\n')
                for line in molCounts :
                    fout.write('\t'.join(str(x) for x in line) + '\n')
        except IOError as err :
            print("File error : " + str(err))
            
    
    def makeTrainSummaryFile(self, expTag):
        
        folder = self.path + "/Exp/" + expTag
        if not os.path.exists(folder) :
            os.makedirs(folder)
            
        f = open(folder + "/trainSummary.txt", 'w')
        return f
    
    def makeTestSummaryFile(self, expTag):
        
        folder = self.path + "/Exp/" + expTag
        if not os.path.exists(folder) :
            os.makedirs(folder)
            
        f = open(folder + "/testSummary.txt", 'w')
        return f
    
    def saveTrainSummaryLine(self, f, trainSummary):
        
        for item in trainSummary : 
            f.write('\t' + str(item))
        f.write('\n')
        f.flush()
        
    def saveTestSummaryLine(self, f, cyc, testSummary):
        
        f.write(str(cyc+1))
        m,n = testSummary.shape
        for i in range(m) :
            for j in range(n) :
                f.write('\t' + str(testSummary[i][j]))
        f.write('\n')
        f.flush()
    
    def saveParams(self, pm):
        
        expTag = pm.get("tag")
        folder = self.path + "/Exp/" + expTag
        if not os.path.exists(folder) :
            os.makedirs(folder)
            
        try :
            with open(folder + "/params.txt", 'wt') as f :
                for key in pm.prdic.keys() :
                    f.write(key + '\t' + str(pm.get(key)) + '\n')
        except IOError as err :
            print("Filer error : " + str(err))
        
#     def saveTotalConc(self, f, tube):
#         
#         f.writeline(str(tube.getTotalConc()))
#         
#     def saveSpcNum(self, f, tube):
#         
#         f.writeline(str(tube.getSpcNum()))
#         
#     def saveReactionTime(self, f, time):
#         
#         f.writeline(str(time))
#         
#     def saveClassificationScore(self, f, score):
#         
#         f.writeline(str(score))
#     
#     def saveClassification(self, f, predict, real):
#         
#         f.write(str(predict))
#         f.write(str(real))
#         f.write("/n")
        
    
if __name__ == '__main__' :
    
    dm = DataModule()
    digit = [6, 7]
    dm.bwThres = 75
    imgSize = 8
    
    trdata = [None]*len(digit)
    tsdata = [None]*len(digit)
    for i in range(len(digit)) :
        trdata[i] = dm.load_mnist("training", "BW", imgSize, [digit[i]], dm.path)
        tsdata[i] = dm.load_mnist("testing", "BW", imgSize, [digit[i]], dm.path)
     
    fdsc = "_c"
    for d in digit :
        fdsc += str(d)
    fdsc += "_sz" + str(imgSize) + "_bw" + str(dm.bwThres)
    
#     fdsc = "_sz" + str(imgSize) + "_bw" + str(dm.bwThres)
    
    dm.saveImages(trdata, dm.path, "bwtrain" + fdsc + ".dat")
    dm.saveImages(tsdata, dm.path, "bwtest" + fdsc + ".dat")
    
#     for i in range(len(digit)) :
#         dm.saveImages(trdata[i], dm.path, "bwtrain_" + "_c" + str(digit[i]) + fdsc + ".txt")
#         dm.saveImages(tsdata[i], dm.path, "bwtest_" + "_c" + str(digit[i]) + fdsc + ".txt")
     
#     trdata = dm.loadImages(path, "bwtrain_" + fdsc + ".txt")
#     tsdata = dm.loadImages(path, "bwtest_" + fdsc + ".txt")
#     for i in range(100) :
#         print trdata[1][1][i]
#         dm.display(trdata[1][0][i])