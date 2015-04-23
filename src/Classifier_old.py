'''
Created on 2014. 10. 7.

@author: Ryuja
'''

from array import array as pyarray
import os, struct
import random
from string import join
import time

import numpy as np

class MolecularCF :
    
    class1 = None
    class2 = None
    
    sizes_train = [10]    
    sizes_test = [10]
    sizes_sample = [10]
    nums_feature = [10]
    repeat = 3
    test_repeat = 1
    n_HE = 3
    
    isIncremental = True
    isDecremental = True
    isSelective = True
    increSelectThres = 2
    
    
    def setClass(self, classList):
        
        self.class1 = classList[0]
        self.class2 = classList[1]
        
    def setTrainSize(self, sizes_train):
        
        self.sizes_train = sizes_train
        
    def setTestSize(self, sizes_test):
        
        self.sizes_test = sizes_test
        
    def setSampleSize(self, sizes_sample):
        
        self.sizes_sample = sizes_sample
        
    def setFeatureNumber(self, nums_feature):
        
        self.nums_feature = nums_feature
        
    def setRepeat(self, repeat):
        
        self.repeat = repeat
        
    def setTestRepeat(self, test_repeat):
        
        self.test_repeat = test_repeat
        
    def setHyperEdgeNumber(self, n_HE):
        
        self.n_HE = n_HE
        
    def setIncremental(self, isIncremental):
        
        self.isIncremental = isIncremental
        
    def setDecremental(self, isDecremental):
        
        self.isDecremental = isDecremental
        
    def setSelective(self, isSelective):
        
        self.isSelective = isSelective
        
    def setIncreSelectThres(self, increSelectThres):
        
        self.increSelectThres = increSelectThres
        
            
    def simulation(self):
    
        print "-------------------Loading Data-------------------"
        tr_images_c1, _ = self.load_mnist("training", [self.class1], "./")
        tr_images_c2, _ = self.load_mnist("training", [self.class2], "./")
        ts_images, ts_labels = self.load_mnist("testing", [self.class1, self.class2], "./")

        print "-------------------Making Storage-------------------"
        outFileSummary, savePrefix = self.makeStorage()
        
        print "-------------------Running HyperNetwork-------------------"
        for r in range(self.repeat) :
            print "\n", r, "th Cycle"
            for n_feature in self.nums_feature :
                features = self.featureExtract(tr_images_c1, tr_images_c2, n_feature)
                print n_feature, "feature number"
                for n_train in self.sizes_train :
                
                    for n_test in self.sizes_test :
                        
                        for n_sample in self.sizes_sample :
                            # Make result file
                            outFileResult = "tr" + str(n_train) + "_tst" + str(n_test) + "_sp" + str(n_sample) + "_ft" + str(n_feature) + "_r" + str(r) + ".txt"
                            outFileResult = savePrefix + '/' + outFileResult
                            
                            # Run Hypernetwork for given parameter
                            accuracy1, accuracy2, precision_c1, recall_c1, precision_c2, recall_c2, n = \
                            self.classifier(tr_images_c1, tr_images_c2, ts_images, ts_labels, features, n_train, n_test, n_sample, outFileResult)
                            
                            # Save result in summary file
                            msg_root = '\t'.join([str(n_train), str(n_test), str(n_sample), str(n_feature)])

                            for t_r in range(self.test_repeat) :
                                msg = msg_root + '\t' + '\t'.join(["{0:.3f}".format(accuracy1[t_r]), 
                                                                   "{0:.3f}".format(accuracy2[t_r]), 
                                                                   "{0:.3f}".format(precision_c1[t_r]), 
                                                                   "{0:.3f}".format(recall_c1[t_r]), 
                                                                   "{0:.3f}".format(precision_c2[t_r]), 
                                                                   "{0:.3f}".format(recall_c2[t_r]), 
                                                                   str(n[t_r]), str(r), str(t_r)])
                                outFileSummary.write(msg + "\n"), outFileSummary.flush()
#                                 print msg
                        
        return
    
    
    def classifier(self, tr_images_c1, tr_images_c2, ts_images, ts_labels, features, n_train, n_test, n_sample, outFileResult) :
        
        print "train :", n_train, ", test :", n_test, ", n_sample :", n_sample 
        outFile = open(outFileResult, 'w')
        
        # Training HN
        HN_c1 = self.training(tr_images_c1, features, n_train, n_sample, self.n_HE)
        HN_c2 = self.training(tr_images_c2, features, n_train, n_sample, self.n_HE) 
    
        # Testing HN
        results = self.testing([], ts_images, ts_labels, features, HN_c1, HN_c2, n_test, n_sample, self.n_HE, self.test_repeat)
    
        accuracy = []
        accuracy2 = []
        precision_c1 = []
        recall_c1 = []
        precision_c2 = []
        recall_c2 = []
        n = []
        
        for result in results :
        
            size_testing_without_n = 0
            tp_c1, actual_c1, predict_c1 = 0, 0, 0
            tp_c2, actual_c2, predict_c2 = 0, 0, 0
            
            for oneResult in result :
                outFile.write("\t".join([str(item) for item in oneResult]) + "\n")
    #             print oneResult
                if oneResult[-2] != "n" : size_testing_without_n += 1
                
                if oneResult[-3] == self.class1 : actual_c1 += 1
                elif oneResult[-3] == self.class2 : actual_c2 += 1
                
                if oneResult[-2] == self.class1 : predict_c1 += 1
                elif oneResult[-2] == self.class2 : predict_c2 += 1
                
                if oneResult[-3] == self.class1 and oneResult[-2] == self.class1 : tp_c1 += 1
                elif oneResult[-3] == self.class2 and oneResult[-2] == self.class2 : tp_c2 += 1
                
    #         print actual_c1, actual_c2
            
            accuracy_one = (tp_c1+tp_c2)/float(n_test)
            if size_testing_without_n :
                accuracy2_one = (tp_c1+tp_c2)/float(size_testing_without_n)
            else :
                accuracy2_one = 0
                
            if predict_c1 == 0 : precision_c1_one = 0
            else : precision_c1_one = tp_c1/float(predict_c1)
            
            if actual_c1 == 0 : recall_c1_one = 0
            else : recall_c1_one = tp_c1/float(actual_c1)
            
            if predict_c2 == 0 : precision_c2_one = 0
            else : precision_c2_one = tp_c2/float(predict_c2)
            
            if actual_c2 == 0 : recall_c2_one = 0
            else : recall_c2_one = tp_c2/float(actual_c2)
            
            accuracy.append(accuracy_one), accuracy2.append(accuracy2_one)
            precision_c1.append(precision_c1_one), recall_c1.append(recall_c1_one)
            precision_c2.append(precision_c2_one), recall_c2.append(recall_c2_one)
            n.append(size_testing_without_n/float(n_test))
            
        outFile.close()       
        
        return accuracy, accuracy2, precision_c1, recall_c1, precision_c2, recall_c2, n
        
    
    def training(self, images, features, n_train, n_sample, n_HE, image_thres=100):
        
        HN = {}
    
        img_idxs = np.random.choice(len(images), n_train, replace=False)
        images_train = [ images[img_idx] for img_idx in img_idxs ]
        
        for image in images_train :
            image_bw = self.img2bw(image, image_thres)
            for i in range(n_sample) :
                idx = [ features[j] for j in np.random.choice(len(features), n_HE, replace=False) ]
                HE = join([join([str(idx[k][0]), str(idx[k][1]), str(int(image_bw[idx[k]]))], ',') for k in range(n_HE)], '|')
    #             HE = ( (idx[j], image(idx[j])) for j in range(n_HE) )
                HN[HE] = HN.get(HE, 0) + 1
                
        return HN
    
    
    def testing(self, results, images, labels, features, HN_c1, HN_c2, n_test, n_sample, n_HE, test_repeat, image_thres=100, thres=1) :
        
        # index preparing
        idxss = np.random.choice(len(images), n_test*test_repeat, replace=False)
        idx_idx = 0
        for r in range(test_repeat) :
#             print r, "th cycle of testing with", n_test, "images"
    
            idxs = idxss[idx_idx:idx_idx+n_test]
            idx_idx += n_test
            #images = images[idx], labels = labels[idx]
            images_thistest = [ images[idx] for idx in idxs ]
            labels_thistest = [ labels[idx] for idx in idxs ]
            
            result_one = []
            for i in range(n_test) :
                image = self.img2bw(images_thistest[i], image_thres)
                label = labels_thistest[i]
                
                dist_c1, dist_c2, predict, correct = self.testOne(HN_c1, HN_c2, image, label, features, n_sample, n_HE, thres)
                
                if dist_c1[3] > 0 : cc1 = 3
                elif dist_c1[2] > 0 : cc1 = 2
                elif dist_c1[1] > 0 : cc1 = 1
                else : cc1 = 0
                
                if dist_c2[3] > 0 : cc2 = 3
                elif dist_c2[2] > 0 : cc2 = 2
                elif dist_c2[1] > 0 : cc2 = 1
                else : cc2 = 0
                
                result_one.append([cc1, cc2, dist_c1, dist_c2, int(label), predict, correct]) # casting label(int8) to int
                
            results.append(result_one)
        
        return results
    
    
    """
    def testOne(HN, image, features, n_sample, n_HE) : 
        
        distances = {0:0, 1:0, 2:0, 3:0}
        
        all_HE = HN.keys()
        
        for i in range(n_sample) :
            idx = [ features[j] for j in np.random.choice(len(features), n_HE, replace=False) ]
            this_HE = join([join([str(idx[k][0]), str(idx[k][1]), str(int(image[idx[k]]))], ',') for k in range(n_HE)], '|')
            for HE in all_HE :
                distances[compareHE(HE, this_HE)] += HN[HE]
        
        return distances
    """
    
    def testOne(self, HN_c1, HN_c2, image, label, features, n_sample, n_HE, thres) :
        
        distances_c1, distances_c2 = {0:0, 1:0, 2:0, 3:0}, {0:0, 1:0, 2:0, 3:0}
    
        all_HE_c1 = HN_c1.keys()
        all_HE_c2 = HN_c2.keys()
        
#         this_HEs = []
        selectedHEs_c1 = list()
        selectedHEs_c2 = list()
        for i in range(n_sample) :
            idx = [ features[j] for j in np.random.choice(len(features), n_HE, replace=False) ]
            this_HE = join([join([str(idx[k][0]), str(idx[k][1]), str(int(image[idx[k]]))], ',') for k in range(n_HE)], '|')
            
            for HE_c1 in all_HE_c1 :
                dist_c1 = self.compareHE(HE_c1, this_HE)
                distances_c1[dist_c1] += HN_c1[HE_c1]
                if self.isSelective :
                    if dist_c1 >= self.increSelectThres :
                        selectedHEs_c1.append(this_HE)
                else :
                    selectedHEs_c1.append(this_HE)

            for HE_c2 in all_HE_c2 :
                dist_c2 = self.compareHE(HE_c2, this_HE)
                distances_c2[dist_c2] += HN_c2[HE_c2]
                if self.isSelective :
                    if dist_c2 >= self.increSelectThres :
                        selectedHEs_c2.append(this_HE)
                else :
                    selectedHEs_c2.append(this_HE)
            
#             if not self.isSelective :
#                 this_HEs.append(this_HE)              
                
        predict = self.makeDecision(distances_c1, distances_c2, thres)
        
        amp_size = 50
        if label == predict : 
            correct = 1
            if self.isIncremental :
                if predict == self.class1 :
                    for this_HE in selectedHEs_c1 :
                        HN_c1[this_HE] = HN_c1.get(this_HE, 0) + amp_size
                elif predict == self.class2 :
                    for this_HE in selectedHEs_c2 :
                        HN_c2[this_HE] = HN_c2.get(this_HE, 0) + amp_size
                    
        else : 
            correct = 0
            if self.isDecremental :
                if predict == self.class1 :
                    for this_HE in selectedHEs_c1 :
                        if HN_c1.get(this_HE, 0) >= amp_size :
                            HN_c1[this_HE] = HN_c1.get(this_HE) - amp_size
                elif predict == self.class2 :
                    for this_HE in selectedHEs_c2 :
                        if HN_c2.get(this_HE, 0) >= amp_size :
                            HN_c2[this_HE] = HN_c2.get(this_HE) - amp_size
                            
        return distances_c1, distances_c2, predict, correct
                
    
    
    def makeDecision(self, dist_c1, dist_c2, thres) : 
        
        decision = "n"
        
        for i in range(3, 1, -1) :
            if dist_c1[i] > dist_c2[i] * thres :
                decision = self.class1
                break
            elif dist_c2[i] > dist_c1[i] * thres :
                decision = self.class2
                break
            
        return decision
        
    
    def compareHE(self, HE1, HE2) :
        
        distance = 0
        
        HE1 = HE1.split('|')
        HE2 = HE2.split('|')
        
        for i in range(0, 3) :
            if HE1[i] == HE2[i] : distance += 1
        
        return distance
    
    
    def img2bw(self, image, thres) :
        
        idx = np.where(image > thres)
        
        bw_image = np.zeros(image.shape)
        bw_image[idx] = 1
        
        return bw_image
        
            
    def featureExtract(self, c1_images, c2_images, n_feature):
    
    #     row, col = c1_images[0].shape
        
        c1_mean = c1_images.mean(axis=0)
        c2_mean = c2_images.mean(axis=0)
        distance = np.abs(c1_mean - c2_mean)
        features = self.n_max(distance, n_feature)
    
        return features
    
        
    def n_max(self, arr, n):
        
        indices = arr.ravel().argsort()[-n:]
        indices = (np.unravel_index(i, arr.shape) for i in indices)
    
        return [i for i in indices]
    
    
    def load_mnist(self, dataset, digits, path):
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
    
        images = np.zeros((N, rows, cols), dtype=np.uint8)
        labels = np.zeros((N, 1), dtype=np.int8)
        for i in range(len(ind)):
            images[i] = np.array(img[ ind[i]*rows*cols : (ind[i]+1)*rows*cols ]).reshape((rows, cols))
            labels[i] = lbl[ind[i]]
    
        return images, labels
    
    
    def makeStorage(self):
        
        folder = "Data/"
        if not os.path.isdir(folder) :
            os.mkdir(folder)
            
        savePrefix = folder + time.strftime("%y%m%d %H%M%S", time.localtime())
        if not os.path.isdir(savePrefix) :
            os.mkdir(savePrefix)
            
        file_summary = savePrefix + "_result_molecular_summary.txt"
        outFile = open(file_summary, 'w')
        outFile.write("Incremental : " + str(self.isIncremental) + 
                      "\tDecremental : " + str(self.isDecremental) + 
                      "\tSelective : " + str(self.isSelective) + "\n")
        outFile.write("train\ttest\tsample\tfeat\taccu\taccu_n\tprec_c1\trec_c1\tprec_c2\trec_c2\tn\tr\tt_r\n")
    
        return outFile, savePrefix

        

#classifier.simulation(sizes_train, sizes_test, sizes_sample, nums_feature, repeat, test_repeat, n_HE)


if __name__ == '__main__' :
    
    classifier = MolecularCF()

    classList = [6, 7]
    classifier.setClass(classList)
    
#     sizes_train = [25]
    sizes_train = [100,200,300,400,500,600,700,800,900,1000]
#     sizes_train = [2]
    classifier.setTrainSize(sizes_train)
    
    sizes_test = [1000]
    classifier.setTestSize(sizes_test)
    
#     sizes_sample = [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50]
#     sizes_sample = [80,90,100,125,150,175,200,225,250,275,300,325,350,375,400,425,450,475,500]
    sizes_sample = [10]
    classifier.setSampleSize(sizes_sample)
    
    nums_feature = [3,10,25]
    classifier.setFeatureNumber(nums_feature)
    
    repeat = 100
    classifier.setRepeat(repeat)
    
#     test_repeat = 1
    test_repeat = 1
    classifier.setTestRepeat(test_repeat)
    
    classifier.setIncremental(False)
    classifier.setDecremental(False)
    classifier.setSelective(False)
    classifier.setIncreSelectThres(2)
    
#     n_HE = 3
    
    classifier.simulation()
    
    
