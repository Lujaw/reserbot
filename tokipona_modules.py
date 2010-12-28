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

from ns        import *
from structure import *
from tokipona  import *
from numpy     import *

import matplotlib.pylab
from aux import *
# input :: String -> (Vector, [Vector])
# effects: None

def input(inp):
    
    yss = []
        
    for word in inp.split(" "):
        ys = []
            
        for syl in silabizar(word,map (lambda s: filter(lambda l: l<>'-',s), syllable)): 
            ys.append( seqLetterSyllable.process_input(list(syl+"-")))
        ys.append(seqLetterSyllable.process_input(list(" ")))  # last syllable
            
        yss.append(seqSyllableWord.process_input(ys))
            
        vphrase = seqWordPhrase.process_input(yss)
    
    return (vphrase, yss)
    
    
# output :: Vector -> Int -> Int -> Int -> String
# effects: seqPhraseWords.net.initial_state is changed

def output(vphrase, max_words_, max_syls_, max_letters_):
    
        max_words = max_words_
        max_syls  = max_syls_
        max_letters = max_letters_
    
        phrase = ""
        word = ""
        
        while (word <> "." and max_words > 0):
            
            vword = seqPhraseWords.next(vphrase)  # it's magic !
            word = ""
            syl = ""
                
            max_syls  = max_syls_
            
            while (syl <> " " and syl <> "." and max_syls > 0):
                
                vsyl = seqWordSyllables.next(vword)
                syl = ""
                letter = ""
                
                max_letters = max_letters_
                
                while (letter <> " " and letter <> "." and letter <> "-" and max_letters > 0):
                    letter = ""
                    t = seqSyllableLetters.next(vsyl)
                    letter = abc[t.argmax()]
                    syl = syl+letter
                    max_letters = max_letters - 1
                    
                seqSyllableLetters.reset()
                word = word + syl
                if (syl[-1] <> "-"):
                    word = word + "-"
                max_syls = max_syls - 1
            
            seqWordSyllables.reset()
            phrase = phrase + word
            if (word[-1] <> " "):
                phrase = phrase + " "
            
            max_words = max_words - 1
            
        return phrase


    
def bootstrap(words, debug = False):
    
    plotptest = []
    plotptrain = []
    
    max_lr = 0.1
    min_lr = 0.001
    
    pwords = random.permutation(words)
    tsc = int((len(words)/100.0)*70)
    
    trains = pwords[0:tsc]
    tests  = pwords[tsc:len(words)]
    
    print "i: ",tsc
    
    ys  = []
    its = 50*tsc
    
    for it in range(its):
        
        word = pwords[random.randint(0,len(pwords)-1)]
        
        word=word+" "
        #print "using: ",word
        if (it % 50 == 0):
            print it
            plotptest.append(test(tests))
            plotptrain.append(test(trains))

        for syl in silabizar(word,map (lambda s: filter(lambda l: l<>'-',s), syllable)):
            
            if syl == ".": # end of phrase
                break
            
            elif syl == " ": # end of word
                ys.append(seqLetterSyllable.process_input(list(" ")))  # we add ' '
                # use seqSyllableWord to train seqWordSyllables
                y = numpy.zeros((len(ys),syllable_len)) 
                
                for i in range(len(ys)):
                    y[i] = ys[i]
                    #print z
                    
                x = numpy.zeros((len(ys),word_len))
                z = seqSyllableWord.process_input(ys)
        
                for i in range(len(ys)): 
                    x[i] = z
                
                # train seqWordSyllables
                seqWordSyllables.reset()
                #for i in range(2):
                #print ((min_lr-max_lr)/its)*it + max_lr
                lr = ((min_lr-max_lr)/its)*it + max_lr
                seqWordSyllables.train_delta(x,y,lr,0.0)
                ys = []
                
            else:
        
                #print "Training with "+syl 
    
                # use seqLetterSyllable to train seqSyllableLetters
                syl = syl + "-"
                y = numpy.zeros((len(syl),letter_len))
        
                for i in range(len(syl)): 
                    y[i] = process(syl[i],abc)
            
                x = numpy.zeros((len(syl),syllable_len))
                z = seqLetterSyllable.process_input(list(syl))
        
                for i in range(len(syl)): 
                    x[i] = z
        
                ys.append(z.copy())
                seqSyllableLetters.reset()
                lr = ((min_lr-max_lr)/its)*it + max_lr
                seqSyllableLetters.train_delta(x,y,lr,0.0)
                
    if debug:
        testp = matplotlib.pylab.plot(range(0,its,50),plotptest)
        trainp = matplotlib.pylab.plot(range(0,its,50),plotptrain)
        matplotlib.pylab.show(testp+trainp)
    

def save():
    
    print "Saving seqLetterSyllable"
    seqLetterSyllable.save("seqLetterSyllable")
    print "Saving seqSyllableWord"
    seqSyllableWord.save("seqSyllableWord")
    print "Saving seqWordPhrase"
    seqWordPhrase.save("seqWordPhrase")
    
    print "Saving seqSyllableLetters"
    seqSyllableLetters.save("seqSyllableLetters")
    print "Saving seqWordSyllables"
    seqWordSyllables.save("seqWordSyllables")
    print "Saving seqPhraseWords"
    seqPhraseWords.save("seqPhraseWords")

def load():

    global seqLetterSyllable, seqSyllableWord, seqWordPhrase, seqWordSyllables, seqSyllableLetters, seqPhraseWords

    name = "seqLetterSyllable"
    print "Loading "+name
    try:
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'",name,".npz\' is not a file or directory"
        
    seqLetterSyllable = NeuralSeq(name, (lambda i: process(i,abc)))
    nsf.close()
    
    name = "seqSyllableWord"
    print "Loading "+name
    try:
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'",name,".npz\' is not a file or directory"
        
    seqSyllableWord = NeuralSeq(name, identity)
    nsf.close()
    
    name = "seqWordPhrase"
    print "Loading "+name
    try: 
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'",name,".npz\' is not a file or directory"
        
    seqWordPhrase = NeuralSeq(name, identity)
    nsf.close()
    
    name = "seqWordSyllables"
    print "Loading "+name
    try: 
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'",name,".npz\' is not a file or directory"
        
    seqWordSyllables = NeuralSeq(name, identity)
    nsf.close()
    
    name = "seqSyllableLetters"
    print "Loading "+name 
    try: 
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'",name,".npz\' is not a file or directory"
        
    seqSyllableLetters = NeuralSeq(name, identity)
    nsf.close()
    
    name = "seqPhraseWords"
    print "Loading "+name
    try: 
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'",name,".npz\' is not a file or directory"
        
    seqPhraseWords = NeuralSeq(name, identity)
    nsf.close()
    

def test(con, debug = False):
    err = 0
    for inp in con:
	
        #print "Output: ",
        
        ys = []
        
        for syl in silabizar(inp,map (lambda s: filter(lambda l: l<>'-',s), syllable)): 
            ys.append( seqLetterSyllable.process_input(list(syl+"-")) )
            
        
        ys.append( seqLetterSyllable.process_input(list(" ")))
        z = seqSyllableWord.process_input(ys)
        
        seqWordSyllables.reset()
        
        if debug:
            print ""
            print inp, "-> ",
        
        for i in range(len(ys)):
            t = seqWordSyllables.next(z)
            
            err = err+numpy.linalg.norm(t-ys[i])
            c = ''
            r = ''
            
            seqSyllableLetters.reset()
            
            for j in range(4):
            
                if (c == '-' or c == ' '):
                    break
                
                tt = seqSyllableLetters.next(t)
                c = abc[tt.argmax()] 
                r = r+c
            
            if debug:
                print r+"_",
            #print "-",
    
    #print ""
    return err / len(con)
    
    