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

from numpy import *

def list2vec(c,alphabet):
    try: 
        f = alphabet.index(c)
    except ValueError:
        f = -1
        print "#Warning \'",c,"\' is out of the alphabet \"",alphabet,"\""
        assert(False)
        
    r = repeat(0,len(alphabet))
    if (f>=0):
        r[f] = 1
    return r

def process(input,alphabet):
    x = zeros((len(input),len(alphabet)))
    for i in xrange(len(input)):
        x[i] = list2vec(input[i], alphabet)
    
    return x

"""
def select_class(input):
    
    if numpy.rank(input) == 2:
        input[0] = map(lambda x: (x+1)*(x+1), input[0])
        input[0] = input[0] / sum(input[0])  
        input.shape = (len(input[0]),)
    else:
        input = map(lambda x: (x+1)*(x+1), input)
        input = input / sum(input)  
        
    p = map (lambda i: sum(input[0:i+1]),range(len(input)))
    p = numpy.array(p)
    rv = numpy.repeat(numpy.random.rand(),len(input))
    
    t = rv - p
    for i in range(len(input)):
        if (t[i]<=0):
            return i
"""

identity = lambda x:x