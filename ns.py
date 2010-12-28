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
import numpy, Oger, mdp
import aux

class NeuralSeq:    
    #def __init__(self,isize = None, rsize = None, osize = None ,f = None):
    def __init__(self,*args):
	
	if (len(args) == 2 and isinstance(args[0],str)):
	    filename = args[0]
	    f = args[1]
	    
	    nsf = open(filename+".npz", "r")
	    
	    p = numpy.load(nsf)
	    self.isize = p[0]
	    self.rsize = p[1]
	    self.osize = p[2]
	    
	    w = numpy.load(nsf)
	    print w.shape
	    w_in = numpy.load(nsf)
	    print w_in.shape
	    initial_state = numpy.load(nsf)
	    print initial_state
	    
	    self.net = Oger.nodes.ReservoirNode(self.isize, self.rsize, dtype='single', w_in=w_in, w=w, w_bias=None)
	    self.net.initial_state = initial_state
	    
	    self.last_state = self.net.initial_state
	    self.f = f
	    self.Wout = numpy.load(nsf)
	    
	    nsf.close()
	
	elif (len(args) == 4):	    
	    self.isize = args[0]
	    self.rsize = args[1]
	    self.osize = args[2]
	
	    self.net = Oger.nodes.ReservoirNode(self.isize, self.rsize, dtype='single')
	    self.last_state = self.net.initial_state
        
	    self.f = args[3]
	    self.Wout = (numpy.random.random((self.rsize,self.osize))-0.5)*0.001 # we set some small weights in output
	else:
	    assert(False)
	    
	    
    
    def train_delta(self,x,y,lrate_delta, lrate_lambda): # good parameters: lrate_delta = 0.1, lrate_lambda = 0.01
	"Train Wout using stochastic gradient descent"
        xr = self.preprocess(x)
        
        (z,sse) = self.sse(x,y)
        delta_w = numpy.empty((self.rsize,self.osize))
 
        for r in numpy.random.permutation(range(len(x))):        
            
            t = y[r] - z[r]
            
            for i in range(self.rsize):
                for k in range(self.osize):
                    delta_w[i,k] = lrate_delta*t[k]*xr[r][i] -lrate_lambda*delta_w[i,k] 
            
            self.Wout = self.Wout + delta_w
            (z,sse) = self.sse(x,y)

    def preprocess(self,x): # preserve(self.net.initial_state)
        
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
        
    def sse(self,x,y): 	# preserve(self.net.initial_state)
        
        ls = self.net.initial_state.copy()  # save self.net.initial_state  
        z = numpy.zeros((len(x),self.osize))
        
        sse = 0
        
        for i in range(len(x)):
            t = numpy.array([x[i]])
            assert(t.shape == (1,self.isize))
            
            z[i] = self.next(t)
            
            sse = sse + numpy.linalg.norm(z[i] - y[i])
            
        self.net.initial_state = ls        # load self.net.initial_state
        
        return (z,sse)
        
        
    def reset(self): # not preserve(self.net.initial_state)
        self.net.initial_state = numpy.zeros((1,self.rsize))
        
        
    def process_input(self,input):
        
        pinput = self.f(input)
        
        last_esnout = numpy.empty(self.osize,dtype=numpy.double)
        esnout = numpy.empty(self.osize,dtype=numpy.double)
    
        self.reset()
        eps = 0.001
        
        # ESN simulation
        
        for i in xrange(len(input)):
            
            v = pinput[i]
            v.shape = (1,self.isize)
            #print v, last_esnout
            last_esnout = self.next(v)
            
        maxi = 1000
        while(maxi>0):
            for i in xrange(len(input)):
                v = pinput[i]
                v.shape = (1,self.isize)
                #print v, last_esnout
                esnout = self.next(v)
                
            if (numpy.linalg.norm(esnout-last_esnout) < eps):
                break
            
            last_esnout = esnout
            maxi = maxi - 1
        
        if (maxi<0):
            sys.stdout.write("warning, " +str(input) +" is not stable at 1000 iters (" + str(numpy.linalg.norm(esnout-last_esnout)) +"\n")
            
        return esnout.copy()
    def next(self,input): # not preserve(net.initial_state)
        
        t = self.net(input)
        t.shape = (1,self.rsize)
        self.last_state = t                                  #saving state
        self.net.initial_state = self.last_state             #restore state
            
        esnout = self.last_state.copy()
        esnout = numpy.dot(esnout,self.Wout)                 #compute esnout
        esnout = aux.normalize(esnout)
        return esnout
    
    def save(self,name):
	nsf = open(name+".npz", "wa")
	
	numpy.save(nsf,numpy.array([self.isize,self.rsize, self.osize]))
	numpy.save(nsf,self.net.w)
	numpy.save(nsf,self.net.w_in)
	numpy.save(nsf,self.net.initial_state)
	numpy.save(nsf,self.Wout)
	
	nsf.close()
	
