'''
Created on 2015. 4. 17.

@author: Ryuja
'''
import random

from Tools import Tools


class Classifier(object):

    def thresholdClassify(self, D, cls, th):
        
        weight = [0,0,1,1000]
        score = [0] * len(cls)
        for i in range(len(cls)) :
            for ds in D[i].keys() :
            
                [oligo, pos] = ds.split("/")
                [t, b] = oligo.split("___")
                c = Tools.match(t, b)
            
                score[i] += weight[c]*D[i][ds]
        
        m = max(score)
        predict = [ j for j, k in enumerate(score) if k == m ]
        
#         print("score is %s" % '\t'.join(map(str, score)))
        if len(predict) >= 2 :
            return score, random.choice(cls)
        else :
            return score, cls[predict[0]]