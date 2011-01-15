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

from ns       import *
from aux      import *
from tokipona import *

# initialization
    
nres         = 200
letter_len   = len(letters)
syllable_len = 100
word_len     = 100
phrase_len   = 30

# input  sequencers
                                #input         #size  #output
seqLetterSyllable  = NeuralSeq( letter_len,    nres,  syllable_len,    (lambda i: process(i,letters)))
seqSyllableWord    = NeuralSeq( syllable_len,  nres,  word_len,        identity)
seqWordPhrase      = NeuralSeq( word_len,      nres,  phrase_len,      identity) # non textual input coming soon!

# output sequencers

seqWordSyllables   = NeuralSeq( word_len,      nres, syllable_len,     identity)
seqSyllableLetters = NeuralSeq( syllable_len,  nres, letter_len,       identity)    

# asociator 
seqPhraseWords     = NeuralSeq( phrase_len,    nres, word_len,         identity) # non textual output coming soon!