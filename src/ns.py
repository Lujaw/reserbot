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
import numpy, Oger
import aux


class NeuralSeq:
    
    """
    Initialize a neural sequencer
    """
    def __init__(self,*args):
	if (len(args) == 2          and
	    isinstance(args[0],str) and
	    callable(args[1])):
	    
	    """
	    Initialization of a Neural Sequencer using:
	     * A filename as string. This file contains every numpy object used in the initialization.
	     * A function as a callable procedure.
	    """
	    
	    filename = args[0]
	    f = args[1]
	    
	    nsf = open(filename+".npz", "r")
	    
	    p = numpy.load(nsf)
	    self.isize = p[0]
	    self.rsize = p[1]
	    self.osize = p[2]
	    
	    w = numpy.load(nsf)
	    w_in = numpy.load(nsf)
	    initial_state = numpy.load(nsf)
	    
	    self.net = Oger.nodes.ReservoirNode(self.isize, self.rsize, dtype='single', w_in=w_in, w=w, w_bias=None, input_scaling=0.5)
	    self.net.initial_state = initial_state
	    
	    self.last_state = self.net.initial_state
	    self.f = f
	    self.Out = Perceptron(numpy.load(nsf))
	    
	    nsf.close()
	
	elif (len(args) == 4          and
	      isinstance(args[0],int) and
	      isinstance(args[1],int) and
	      isinstance(args[2],int) and
	      callable(args[3])):
	    
	    """
	    Initialization of a Neural Sequencer using:
	     * Input size as integer.
	     * Reservoir size as integer.
	     * Output size as integer.
	     * A function as a callable procedure.
	    """
	
	    self.isize = args[0]
	    self.rsize = args[1]
	    self.osize = args[2]
	
	    self.net = Oger.nodes.ReservoirNode(self.isize, self.rsize, dtype='single', input_scaling=0.5)
	    self.last_state = self.net.initial_state
        
	    self.f = args[3]
	    self.Out = Perceptron(self.rsize,self.osize)
	else:
	    """
	    EPIC FAIL!
	    """
	    
	    assert(False)
	    

    """
    Do an iteration of the neural sequencer model train (a perceptron) using:
     * Input as a numpy array.
     * Desired output as a numpy array.
     * Learning rate as a float.
     * Lambda (parameter using in weight regularization) as a float.
    """
    
    def train(self,x,y,lrate_delta, lrate_lambda): 
        	
	xr = self.__preprocess(x)
	z  = self.__sse(x) 
	
        for r in numpy.random.permutation(range(len(x))):            
            t = y[r] - z[r]    
            self.Out.adjust_weigths(t,xr[r],lrate_delta,lrate_lambda)
	    z = self.__sse(x)

    """
    Reset internal state of neural sequencer to null vector
    """

    def reset(self): # not preserve(self.net.initial_state)
        self.net.initial_state = numpy.zeros((1,self.rsize))
        
    
    """
    Encode a sequence in R^n using:
     * Input as a list
    """
        
    def process_input(self,input):
        
	# Formal parameters
	eps = 0.001
	M   = 1000
	
        pinput = self.f(input)
        
        last_esnout = numpy.empty(self.osize,dtype=numpy.double)
        esnout = numpy.empty(self.osize,dtype=numpy.double)
    
        self.reset()
        
        for i in xrange(len(input)):
            
            v = pinput[i]
            v.shape = (1,self.isize)
            last_esnout = self.next(v)
        
	
	for i in range(M):
	    for i in xrange(len(input)):
                v = pinput[i]
                v.shape = (1,self.isize)
                esnout = self.next(v)
                
            if (numpy.linalg.norm(esnout-last_esnout) < eps):
                break
            else:
		last_esnout = esnout
		if (i==M-1):
		    print "warning, "+str(input) +" is not stable at "+str(M)+" iteration"
		    
        return esnout.copy()
	
    def next(self,input): # not preserve(net.initial_state)
        
        t = self.net(input)
        t.shape = (1,self.rsize)
        self.last_state = t                                  #saving state
        self.net.initial_state = self.last_state             #restore state
            
        esnout = self.last_state.copy()
        esnout = self.Out.process(esnout)                    #compute esnout
        esnout = aux.normalize(esnout)
        return esnout
    
    def save(self,name):
	nsf = open(name+".npz", "wa")
	
	numpy.save(nsf,numpy.array([self.isize,self.rsize, self.osize]))
	numpy.save(nsf,self.net.w)
	numpy.save(nsf,self.net.w_in)
	numpy.save(nsf,self.net.initial_state)
	numpy.save(nsf,self.Out.Wout)
	
	nsf.close()
	
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
            z[i] = self.next(t)
        self.net.initial_state = ls        # load self.net.initial_state
	return z


class Perceptron:
    """ A linear perceptron """
    def __init__(self, *args):
	""""""
	
	if (len(args) == 1 and isinstance(args[0],numpy.ndarray)):
	    self.Wout = args[0]
	elif (len(args) == 2):
	    self.Wout = (numpy.random.random((args[0],args[1]))-0.5)*0.001 # we set some small weights in output
	else:
	    assert(False)
	    
    def process(self, input):
	""" Process an input using weight matrix """
	return numpy.dot(input,self.Wout)
	
    def adjust_weigths(self, t, xr, lrate_delta, lrate_lambda):
	""""""

	(a,b) = self.Wout.shape
	delta_w = numpy.empty((a,b))
	for i in range(a):
            for k in range(b): 
                delta_w[i,k] = lrate_delta*t[k]*xr[i] -lrate_lambda*delta_w[i,k]  # not so optimal
	
	self.Wout = self.Wout + delta_w