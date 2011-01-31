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

class Conversation:
    
    def __init__(self):
        self.conversation          = []
        self.started               = False
        self.last_processed_phrase = None
    
    def start(self):
        if not self.started:
            self.started = True
    def end(self):
        if self.started:
            self.started = False
            
    def add_processed_phrase(self,processed_phrase):
        
        if self.last_processed_phrase == None:
            #print "adding phrase "
            #print processed_phrase
            self.last_processed_phrase = processed_phrase.copy()
        else:
            print "#Error processed phrase already setted."
            assert(False)
    
    def add_processed_words(self,processed_words):
        
        if self.last_processed_phrase <> None:
            #print "last phrase"
            #print self.last_processed_phrase
            #print "adding words "
            #print #processed_words
            self.conversation.append((self.last_processed_phrase, processed_words[:]))
            self.last_processed_phrase = None
        else:
            print "#Error processed words not setted."
            
    def processed_words_phrases(self):
        r = self.conversation[:]
        return r    
    
    def processed_phrases(self):
        r = []
        
        for (processed_phrase,processed_words) in self.conversation:
            r.append(processed_phrase)
            
        return r    
    
    def processed_words(self):
        r = []
        
        for (processed_phrase,processed_words) in self.conversation:
            r.append(processed_phrase)
        
        return r    
    

#convs = []
#
#for i in range(3):
#
#    c = Conversation()
#    c.add_processed_phrase(0)
#    
#    for j in range(3):
#        c.add_processed_words(['x'+str(i)+str(j),'y'+str(i)+str(j)])
#        c.add_processed_phrase(j+1)
#    
#    convs.append(c)
#    
#for c in convs:
#    print c.processed_words_phrases()
#    print "..."
