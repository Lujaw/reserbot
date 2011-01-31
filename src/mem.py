"""
    This file is part of reserbot.

    reserbot is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    reserbot is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with reserbot.  If not, see <http://www.gnu.org/licenses/>.

    Copyright 2010 neuromancer
"""

import random
import ns, aux, numpy, Oger
import mdp

class Memory:
    
    maxstm = 1
    xindex = []
    yindex = []
    
    rx = []
    ry = []

    def __init__(self,*args):
        
        if (len(args) == 4          and
            isinstance(args[0],int) and 
	    isinstance(args[1],int) and 
	    isinstance(args[2],int) and
	    callable(args[3])):
	    
	    self.isize = args[0]
	    self.rsize = args[1]
	    self.osize = args[2]
	
	    self.net = Oger.nodes.ReservoirNode(self.isize, self.rsize, dtype='single', input_scaling=0.5)
	    self.last_state = self.net.initial_state
	       
	    self.f = args[3]
	    self.stm = [ns.Perceptron(self.rsize,self.osize)]
	    
            self.index = mdp.nodes.KNNClassifier()
            
	    # It is necessary to train index classifier, at least one.
	    x = numpy.random.random((1,self.rsize))
            self.index.train(x,0)
            self.index.stop_training()
            
	else:
	    assert(False)

    def freshmem(self, cphrases):
                
        self.maxstm = self.maxstm+1
        self.stm.append(ns.Perceptron(self.rsize,self.osize))
        
        self.index = mdp.nodes.KNNClassifier(k=1) # How to control this parameter?
        
        # Rebuilding index
        
        for vlist in cphrases:
            self.reset()
            
            x = numpy.empty((len(vlist), self.isize))
            
            for i in range(len(vlist)):
                x[i] = vlist[i]
            
            xr = self.__preprocess(x)
            self.xindex.append(xr)
            self.yindex.append(self.maxstm-1)

            
        for i in range(len(self.xindex)):
            self.index.train(self.xindex[i],self.yindex[i])
        
        self.index.stop_training()
        
    def train(self,x,y,lrate_delta, lrate_lambda): 
        
	xr = self.__preprocess(x)
	z  = self.__sse(x)     
        
        for r in numpy.random.permutation(range(len(x))):            
            t = y[r] - z[r]
            self.stm[-1].adjust_weigths(t,xr[r],lrate_delta,lrate_lambda)
	    z = self.__sse(x)
    
    def next(self,input, i = None): # not preserve(net.initial_state)
        
        t = self.net(input)
        t.shape = (1,self.rsize)
        
        if i == None:
            i = self.index.label(t)[0]    
            if (i >= len(self.stm)):
                i = -1
        
        self.last_state = t                                  #saving state
        self.net.initial_state = self.last_state             #restore state
            
        esnout = self.last_state.copy()
        esnout = self.stm[i].process(esnout)
        
        esnout = aux.normalize(esnout)
        return esnout
    
    """
    Reset internal state of neural sequencer to null vector
    """

    def reset(self): # not preserve(self.net.initial_state)
        self.net.initial_state = numpy.zeros((1,self.rsize))
        
#    def consolidate(self):
#	pass
#	ltmsize = 1000  # ltm samples size
#	stmsize = 2000  # stm samples size
#	its = 1000
#	
#	items_per_epoch = 5
#	
#	ex = []
#	ey = []
#	
#	# random extraction knowledge from stm
#        print "extracting knowledge from stm"
#	for i in range(stmsize): 
#	    z = numpy.random.random((1,self.rsize))
#	    ex.append(z)
#            ey.append(self.stm.process(z))
#	# -----------------------------
#	
#        #for i in range(len(ex)):
#        #    print ex[i]
#        #    print ey[i]
#        #
#        
#	# no pseudorehearsal (first time)
#	if self.rx == [] and self.ry == []: 
#	    
#	    max_lr = 0.1
#            min_lr = 0.001
#	    lrate_lambda = 0.0
#            
#            print "training ltm (no pseudorehearsal)"
#	    for i in range(1,its):
#		r = numpy.random.randint(0,stmsize)
#                
#                xr = ex[r]
#                t = ey[r] - self.ltm.process(ex[r]) 
#                
#                xr.shape = (self.rsize,)
#                t.shape = (self.osize,)
#                
#                self.trainLTM(t,xr,0.01, lrate_lambda)
#                #if (i % 100 == 0):
#                #    print self.__test(ex,ey,self.ltm)
#		
#	    
#	else: # pseudorehearsal   
#	    
#            max_lr = 0.1
#            min_lr = 0.001
#	    lrate_lambda = 0.0
#            
#            print "training ltm (pseudorehearsal)"
#            
#	    for i in range(1,its):
#		r = numpy.random.randint(0,stmsize)
#		
#                xr = ex[r]
#                t = ey[r] - self.ltm.process(ex[r]) 
#                
#                xr.shape = (self.rsize,)
#                t.shape = (self.osize,)
#                
#                #print numpy.linalg.norm(t)
#                
#                self.trainLTM(t,xr,0.01, lrate_lambda)
#                if (i % 30 == 0):
#                    print self.__test(ex,ey,self.ltm)
#		
#		for j in range(items_per_epoch):
#		    r = numpy.random.randint(0,ltmsize)
#                    
#                    xr = self.rx[r]
#                    t = self.ry[r] - self.ltm.process(self.rx[r]) 
#                
#                    xr.shape = (self.rsize,)
#                    t.shape = (self.osize,)
#                    
#		    self.trainLTM(t,xr,0.01, lrate_lambda)
#	
#        
#        self.rx = []
#        self.ry = []
#        
#	# extraction knowledge from ltm
#        print "extracting knowledge from ltm for next consolidation"
#	for i in range(ltmsize):
#	    z = numpy.random.random((1,self.rsize))
#	    self.rx.append(z)
#            self.ry.append(self.ltm.process(z))
#	    
#    def __train(self,x,y,lrate_delta, lrate_lambda, nn): 
#        xr = self.__preprocess(x)
#        (z,sse) = self.__sse(x,y)
#	
#        for r in numpy.random.permutation(range(len(x))):            
#            t = y[r] - z[r]    
#            nn.adjust_weigths(t,xr[r],lrate_delta,lrate_lambda)
#	    (z,sse) = self.__sse(x,y)
	
    def __preprocess(self,x): 
        """
	Properties: it preserves self.net.initial_state
	"""
	
        assert(x.shape == (len(x),self.isize))
        
        xr = numpy.empty((len(x),self.rsize))
        ls = self.net.initial_state.copy()  # save self.net.initial_state 
        
        for i in range(len(x)):
            tt = numpy.array([x[i]])
            t = self.net(tt)
            
            assert(t.shape == (1,self.rsize))
            
            self.last_state = t                                  #saving state
            self.net.initial_state = self.last_state             #restore state
            xr[i] = t
        
        self.net.initial_state = ls         # load self.net.initial_state
        return xr
    
    def __sse(self,x):
	
	ls = self.net.initial_state.copy()  # save self.net.initial_state  
        z = numpy.zeros((len(x),self.osize))
	
        for i in range(len(x)):
            t = numpy.array([x[i]])
            assert(t.shape == (1,self.isize))
            z[i] = self.next(t,-1)
            
        self.net.initial_state = ls        # load self.net.initial_state
	return z
    
    def __test(self,sx,sy,nn):
        acc = 0

        for i in range(len(sx)):
            acc = acc + numpy.linalg.norm(sy[i] - nn.process(sx[i]))

        acc = acc / len(sx)
    
        return acc