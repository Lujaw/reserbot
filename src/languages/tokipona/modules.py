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
import os

from ns        import *
from tokipona  import *
from numpy     import *
from aux       import *

import structure as st


# initial_phrase :: Vector

initial_phrase = numpy.repeat(0,st.phrase_len) # null phrase, at the beggining of conversation

# input :: String -> (Vector, [Vector])
# effects: None

def input(inp):
    
    yss = []
        
    for word in inp.split(" "):
        ys = []
            
        for syl in silabizar(word,map (lambda s: filter(lambda l: l<>'-',s), syllable)): 
            ys.append(st.seqLetterSyllable.process_input(list(syl+"-")))
        ys.append(st.seqLetterSyllable.process_input(list(" ")))  # last syllable
            
        yss.append(st.seqSyllableWord.process_input(ys))
            
        vphrase = st.seqWordPhrase.process_input(yss)

    return (vphrase, yss)
    
    
# output :: Vector -> Int -> Int -> Int -> String
# effects: st.seqPhraseWords.net.initial_state is changed

def output(vphrase, max_words_, max_syls_, max_letters_):
    
        max_words = max_words_
        max_syls  = max_syls_
        max_letters = max_letters_
    
        phrase = ""
        word = ""
        
        while (word <> "." and max_words > 0):
            
            vword = st.seqPhraseWords.next(vphrase)  # it's magic !
            word = ""
            syl = ""
                
            max_syls  = max_syls_
            
            while (syl <> " " and syl <> "." and max_syls > 0):
                
                vsyl = st.seqWordSyllables.next(vword)
                syl = ""
                letter = ""
                
                max_letters = max_letters_
                
                while (letter <> " " and letter <> "." and letter <> "-" and max_letters > 0):
                    letter = ""
                    t = st.seqSyllableLetters.next(vsyl)
                    letter = abc[t.argmax()]
                    syl = syl+letter
                    max_letters = max_letters - 1
                    
                st.seqSyllableLetters.reset()
                word = word + syl
                if (syl[-1] <> "-"):
                    word = word + "-"
                max_syls = max_syls - 1
            
            st.seqWordSyllables.reset()
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
    its = 30*tsc
    
    for it in range(its):
        
        word = pwords[random.randint(0,len(pwords)-1)]
        
        word=word+" "
        #print "using: ",word
        if (it % 50 == 0):
            print it
            plotptest.append(test(tests, debug))
            plotptrain.append(test(trains, debug))

        for syl in silabizar(word,map (lambda s: filter(lambda l: l<>'-',s), syllable)):
            
            if syl == " ": # end of word
                ys.append(st.seqLetterSyllable.process_input(list(" ")))  # we add ' '
                # use seqSyllableWord to train seqWordSyllables
                y = numpy.zeros((len(ys),st.syllable_len)) 
                
                for i in range(len(ys)):
                    y[i] = ys[i]
                    #print z
                    
                x = numpy.zeros((len(ys),st.word_len))
                z = st.seqSyllableWord.process_input(ys)
        
                for i in range(len(ys)): 
                    x[i] = z
                
                # train seqWordSyllables
                st.seqWordSyllables.reset()
                #for i in range(2):
                #print ((min_lr-max_lr)/its)*it + max_lr
                lr = ((min_lr-max_lr)/its)*it + max_lr
                st.seqWordSyllables.train(x,y,lr,0.0)
                ys = []
                
            else:
        
                #print "Training with "+syl 
    
                # use seqLetterSyllable to train seqSyllableLetters
                syl = syl + "-"
                y = numpy.zeros((len(syl),st.letter_len))
        
                for i in range(len(syl)): 
                    y[i] = process(syl[i],abc)
            
                x = numpy.zeros((len(syl),st.syllable_len))
                z = st.seqLetterSyllable.process_input(list(syl))
        
                for i in range(len(syl)): 
                    x[i] = z
        
                ys.append(z.copy())
                st.seqSyllableLetters.reset()
                lr = ((min_lr-max_lr)/its)*it + max_lr
                st.seqSyllableLetters.train(x,y,lr,0.0)
                
    if debug:
        
        import matplotlib.pylab
        testp = matplotlib.pylab.plot(range(0,its,50),plotptest)
        trainp = matplotlib.pylab.plot(range(0,its,50),plotptrain)
        matplotlib.pylab.show(testp+trainp)
    

def save():
    
    path = os.path.join("src","languages","tokipona","bootstrapped_data")
    
    print "Saving seqLetterSyllable"
    st.seqLetterSyllable.save(os.path.join(path, "seqLetterSyllable"))
    print "Saving seqSyllableWord"
    st.seqSyllableWord.save(os.path.join(path, "seqSyllableWord"))
    print "Saving seqWordPhrase"
    st.seqWordPhrase.save(os.path.join(path, "seqWordPhrase"))
    
    print "Saving seqSyllableLetters"
    st.seqSyllableLetters.save(os.path.join(path, "seqSyllableLetters"))
    print "Saving seqWordSyllables"
    st.seqWordSyllables.save(os.path.join(path, "seqWordSyllables"))
    print "Saving seqPhraseWords"
    st.seqPhraseWords.save(os.path.join(path, "seqPhraseWords"))
    

def load():

    path = os.path.join("src","languages","tokipona","bootstrapped_data")
    
    name = "seqLetterSyllable"
    name = os.path.join(path, name)
    print "Loading "+name
    try:
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'"+name+".npz\' is not a file or directory"
        
    st.seqLetterSyllable = NeuralSeq(name, (lambda i: process(i,abc)))
    nsf.close()
    
    name = "seqSyllableWord"
    name = os.path.join(path, name)
    print "Loading "+name
    try:
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'"+name+".npz\' is not a file or directory"
        
    st.seqSyllableWord = NeuralSeq(name, identity)
    nsf.close()
    
    name = "seqWordPhrase"
    name = os.path.join(path, name)
    print "Loading "+name
    try: 
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'"+name+".npz\' is not a file or directory"
        
    st.seqWordPhrase = NeuralSeq(name, identity)
    nsf.close()
    
    name = "seqWordSyllables"
    name = os.path.join(path, name)
    print "Loading "+name
    try: 
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'"+name+".npz\' is not a file or directory"
        
    st.seqWordSyllables = NeuralSeq(name, identity)
    nsf.close()
    
    name = "seqSyllableLetters"
    name = os.path.join(path, name)
    print "Loading "+name 
    try: 
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'"+name+".npz\' is not a file or directory"
        
    st.seqSyllableLetters = NeuralSeq(name, identity)
    nsf.close()
    
    name = "seqPhraseWords"
    name = os.path.join(path, name)
    print "Loading "+name
    try: 
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'"+name+".npz\' is not a file or directory"
        
    st.seqPhraseWords = NeuralSeq(name, identity)
    nsf.close()
    

def test(con, debug = False):
    err = 0
    for inp in con:
        
        ys = []
        
        for syl in silabizar(inp,map (lambda s: filter(lambda l: l<>'-',s), syllable)): 
            ys.append( st.seqLetterSyllable.process_input(list(syl+"-")) )
            
        
        ys.append( st.seqLetterSyllable.process_input(list(" ")))
        z = st.seqSyllableWord.process_input(ys)
        
        st.seqWordSyllables.reset()
        
        for i in range(len(ys)):
            t = st.seqWordSyllables.next(z)
            
            err = err+numpy.linalg.norm(t-ys[i])
            c = ''
            r = ''
            
            st.seqSyllableLetters.reset()
            
            for j in range(4):
            
                if (c == '-' or c == ' '):
                    break
                
                tt = st.seqSyllableLetters.next(t)
                c = abc[tt.argmax()] 
                r = r+c
            
            if debug:
                print r,
            #print "-",
    
    if debug:
        print ""
    return err / len(con)
    
    
def learn(lp, ws):
    
    x = numpy.zeros((len(ws),st.phrase_len))
    y = numpy.zeros((len(ws),st.word_len))
    
    for i in range(len(ws)):
        x[i] = lp
        y[i] = ws[i]
    
    st.seqPhraseWords.train(x,y,0.01,0.0)   
    
def reset():
    st.seqLetterSyllable.reset()
    st.seqSyllableWord.reset()
    st.seqWordPhrase.reset()
    st.seqSyllableLetters.reset()
    st.seqWordSyllables.reset()
    st.seqPhraseWords.reset()

