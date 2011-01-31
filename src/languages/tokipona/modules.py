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
            
        word = preprocess_word(word)
            
        for syl in silabizar(word,map (lambda s: filter(lambda l: l<>'-',s), syllables)): 
            syl = preprocess_syllable(syl)
            ys.append(st.seqLetterSyllable.process_input(list(syl)))
        
        #ys.append(st.seqLetterSyllable.process_input(list(" ")))  # last syllable
            
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
        
        while ( (not ("." in word)) and max_words > 0):
                
            vword = st.seqPhraseWords.next(vphrase)
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
                    letter = letters[t.argmax()]
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


    
def bootstrap(words, max_lr, min_lr, multiplier, use_test, debug):
    

    plotptest = []
    plotptrain = []

    pwords = random.permutation(words)
    
    # separation betewen test and train set (if use_test is True)
    
    if use_test:
        tsc = int((len(words)/100.0)*70)    
    
        trains = pwords[0:tsc]             # 70% is going to train
        tests  = pwords[tsc:len(words)]    # 30% is going to test
    else:
        tsc = len(words)          
        trains = range(tsc)                # 100% is going to train
        tests = []                         #   0% is going to test
        
    ys  = []
    its = multiplier*tsc
    
    for it in range(its):
        
        word = pwords[random.randint(0,len(pwords))]
        word=preprocess_word(word)
        
        #print "Using "+word
        
        if debug and (it % 50 == 0):
            print it
            print trains
            if use_test:
                (s,f) = test(tests, debug)
                print s
                plotptest.append(f)
            
            
            (s,f) = test(trains, debug)
            print s
            plotptrain.append(f)

        for syl in silabizar(word,map (lambda s: filter(lambda l: l<>'-',s), syllables)):
            
            
            syl = preprocess_syllable(syl)
            #print "Training with \""+syl+"\""    
            
            # use seqLetterSyllable to train seqSyllableLetters
                
            y = numpy.zeros((len(syl),st.letter_len))
        
            for i in range(len(syl)): 
                y[i] = process(syl[i],letters)
            
            x = numpy.zeros((len(syl),st.syllable_len))
            z = st.seqLetterSyllable.process_input(list(syl))
        
            for i in range(len(syl)): 
                x[i] = z
        
            ys.append(z.copy())
            # train seqSyllableLetters
            st.seqSyllableLetters.reset()
            lr = ((min_lr-max_lr)/its)*it + max_lr
            st.seqSyllableLetters.train(x,y,lr,0.0)
                
            # --------------------------------------------------
            
            
            if syl in extra_syllables: # end of word
                
                #print "Training with \""+word+"\""
                
                # use seqSyllableWord to train seqWordSyllables
                y = numpy.zeros((len(ys),st.syllable_len)) 
                
                for i in range(len(ys)):
                    y[i] = ys[i]
                    
                x = numpy.zeros((len(ys),st.word_len))
                z = st.seqSyllableWord.process_input(ys)
        
                for i in range(len(ys)): 
                    x[i] = z
                
                # train seqWordSyllables
                st.seqWordSyllables.reset()

                lr = ((min_lr-max_lr)/its)*it + max_lr
                st.seqWordSyllables.train(x,y,lr,0.0)
                ys = []
                #st.seqSyllableLetters.train(x,y,lr,0.0)
                
    #if debug: 
    #    import matplotlib.pylab
    #    testp = matplotlib.pylab.plot(range(0,its,50),plotptest)
    #    trainp = matplotlib.pylab.plot(range(0,its,50),plotptrain)
    #    matplotlib.pylab.show(testp+trainp)

def save():
    
    path = os.path.join("src","languages","tokipona","bootstrapped_data")
    
    r = ""
    
    r = r + "Saving seqLetterSyllable\n"
    st.seqLetterSyllable.save(os.path.join(path, "seqLetterSyllable"))
    r = r +  "Saving seqSyllableWord\n"
    st.seqSyllableWord.save(os.path.join(path, "seqSyllableWord"))
    #r = r + "Saving seqWordPhrase\n"
    #st.seqWordPhrase.save(os.path.join(path, "seqWordPhrase"))
    
    r = r + "Saving seqSyllableLetters\n"
    st.seqSyllableLetters.save(os.path.join(path, "seqSyllableLetters"))
    r = r +  "Saving seqWordSyllables\n"
    st.seqWordSyllables.save(os.path.join(path, "seqWordSyllables"))
    #r = r +  "Saving seqPhraseWords\n"
    #st.seqPhraseWords.save(os.path.join(path, "seqPhraseWords"))
    return r

def load():

    path = os.path.join("src","languages","tokipona","bootstrapped_data")
    r = ""
    name = "seqLetterSyllable"
    name = os.path.join(path, name)
    r = r + "Loading "+name+"\n"
    try:
        nsf = open(name+".npz", "r")
    except IOError:
        r = r +  "#Warning \'"+name+".npz\' is not a file or directory"+"\n"
        return r
        
    st.seqLetterSyllable = NeuralSeq(name, (lambda i: process(i,letters)))
    nsf.close()
    
    name = "seqSyllableWord"
    name = os.path.join(path, name)
    r = r +  "Loading "+name+"\n"
    try:
        nsf = open(name+".npz", "r")
    except IOError:
        r = r +  "#Warning \'"+name+".npz\' is not a file or directory"+"\n"
        return r
        
    st.seqSyllableWord = NeuralSeq(name, identity)
    nsf.close()
    
    #name = "seqWordPhrase"
    #name = os.path.join(path, name)
    #r = r +  "Loading "+name+"\n"
    #try: 
    #    nsf = open(name+".npz", "r")
    #except IOError:
    #    r = r +  "#Warning \'"+name+".npz\' is not a file or directory"+"\n"
    #    return r
        
    st.seqWordPhrase = NeuralSeq(name, identity)
    nsf.close()
    
    name = "seqWordSyllables"
    name = os.path.join(path, name)
    r = r +  "Loading "+name+"\n"
    try: 
        nsf = open(name+".npz", "r")
    except IOError:
        print "#Warning \'"+name+".npz\' is not a file or directory"+"\n"
        return r
        
    st.seqWordSyllables = NeuralSeq(name, identity)
    nsf.close()
    
    name = "seqSyllableLetters"
    name = os.path.join(path, name)
    r = r + "Loading "+name +"\n"
    try: 
        nsf = open(name+".npz", "r")
    except IOError:
        r = r +  "#Warning \'"+name+".npz\' is not a file or directory"+"\n"
        return r
        
    st.seqSyllableLetters = NeuralSeq(name, identity)
    nsf.close()
    
    #name = "seqPhraseWords"
    #name = os.path.join(path, name)
    #r = r +  "Loading "+name+"\n"
    #try: 
    #    nsf = open(name+".npz", "r")
    #except IOError:
    #    r = r +  "#Warning \'"+name+".npz\' is not a file or directory"+"\n"
    #    return r
    #    
    #st.seqPhraseWords = NeuralSeq(name, identity)
    #nsf.close()
    return r
    

def test(con, debug = False):
    err = 0
    acc = ""
    for inp in con:
        
        ys = []
        
        inp = preprocess_word(inp)
        
        for syl in silabizar(inp,map (lambda s: filter(lambda l: l<>'-',s), syllables)):
            syl = preprocess_syllable(syl)
            ys.append( st.seqLetterSyllable.process_input(list(syl)))
            
        #ys.append( st.seqLetterSyllable.process_input(list(" ")))
        z = st.seqSyllableWord.process_input(ys)
        
        st.seqWordSyllables.reset()
        
        for i in range(len(ys)):
            t = st.seqWordSyllables.next(z)
            
            err = err+numpy.linalg.norm(t-ys[i])
            c = ''
            r = ''
            
            st.seqSyllableLetters.reset()
            
            for j in range(5): # How to adjust this parameter ?
            
                if (c == '-' or c == ' '):
                    break
                
                tt = st.seqSyllableLetters.next(t)
                c = letters[tt.argmax()] 
                r = r+c
            
            acc = acc + r 
            if debug:
                if  r[-1]<>"-":
                    acc = acc + "-"
            else:
                acc = filter(lambda c: c <> "-", acc)
                
        acc = acc + "\n"
    #if debug:
    #    print ""
    return (acc, err / len(con))
    
    
def learn(lp, ws):
    
    x = numpy.zeros((len(ws),st.phrase_len))
    y = numpy.zeros((len(ws),st.word_len))
    
    for i in range(len(ws)):
        x[i] = lp
        y[i] = ws[i]
    
    st.seqPhraseWords.train(x,y,0.01,0.0)
    
def freshmem(clist):
    st.seqPhraseWords.freshmem(clist)
    
def reset():
    st.seqLetterSyllable.reset()
    st.seqSyllableWord.reset()
    st.seqWordPhrase.reset()
    st.seqSyllableLetters.reset()
    st.seqWordSyllables.reset()
    st.seqPhraseWords.reset()

