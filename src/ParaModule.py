'''
Created on 2015. 1. 26.

@author: Ryuja
'''
from _collections import defaultdict


class ParaModule :
    '''
    classdocs
    '''
    
    prdic = defaultdict(list)

    def __init__(self, params):
        '''
        Constructor
        '''
        
        if len(params) % 2 != 0 :
            print "Error : Wrong Parameter Input"
            print "Input :", params
        else : 
            for i in range(len(params)/2) :
                self.prdic[params[2*i]] = params[2*i+1]
                
    
    def get(self, key):
        
        if key in self.prdic :
            return self.prdic[key]
        else :
            print "Error : " + key + "is not in the Parameter Dictionary"
            return None
