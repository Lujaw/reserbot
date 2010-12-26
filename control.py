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

from tokipona         import *
from tokipona_modules import *

bootstrap(corpus)


#lastp = numpy.repeat(0,phrase_len) # null phrase, at the beggining of conversation 

while (True):
    print "--> ",
    inp = raw_input()
    (p, ws) =  input(inp)
    
    response = output(p,3,3,3)
    print "<== "+response
    #learn(lastp,ws)
    
    #lastp = p