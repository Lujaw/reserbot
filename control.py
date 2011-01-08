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

import tokipona_modules as modules
import structure as st
import numpy, cmd, readline, sys, random

# Global variables
conversation_started = False
lastp = None
conversations = []
conversation = []
debug = False
version = "Alpha 0"

def process(inp):
    global lastp, conversation
    
    (p, ws) =  modules.input(inp)
    out = modules.output(p,3,3,3)
    conversation.append((lastp,ws))
    lastp = p
    return out

def rest():
    
    its = 100
    
    for it in range(its):
        perm = numpy.random.permutation(range(len(conversations)))
        for i in perm:
            c = conversations[i]
            modules.reset()
            for (lp,ws) in c:
                if (not numpy.linalg.norm(lp) < 0.001):
                    modules.learn(lp,ws)
                    out = modules.output(lp,3,3,3)
                    if (it % 10 == 0):
                        print out            
        
        if (it % 10 == 0):
            print "---"

class Shell(cmd.Cmd):
    intro = 'Welcome to the reserbot ('+version.lower()+') shell. \nType help or ? to list commands.\n'
    prompt = '--> '
    
    # ----- basic commands -----
    
    def do_quit(self, arg):
        'Quit.'
        print "Bye!"
        sys.exit(0)
    
    def do_exit(self, arg):
        'Quit.'
        self.do_quit(arg)
    def do_EOF(self, arg):
        'Quit.'
        print ""
        self.do_quit(arg)
        
    def do_version(self, arg):
        'Show version'
        print version
        
    def do_debug(self, arg):
        'Toggle debug'
        global debug
        debug = not debug
        print "Debug is "+str(debug)
    
    # ----- conversation commands -----
    
    def do_start(self, arg):
        'Start conversation'
        global lastp, conversation, conversation_started
        modules.reset()
        
        lastp = numpy.repeat(0,st.phrase_len) # null phrase, at the beggining of conversation
        lastp = numpy.array([lastp])
        
        conversation = []
        conversation_started = True
        print "Conversation started."
    
    def do_end(self, arg):
        'End conversation'
        global conversation_started, conversations
        conversation_started = False
        conversations.append(conversation)
        
        print "Conversation ended."
    
    def do_discard(self, arg):
        'Abort current conversation'
        global conversation_started, conversation
        conversation_started = False
        conversation = []
        
        print "Conversation aborted."
    
    
    def do_bootstrap(self, arg):
        'Start bootstrapping process.'
        print "Bootstrapping toki pona. This can take a while..."
        modules.bootstrap(corpus, debug)
        
    def do_rest(self, arg):
        'Train brain with recent conversations'
        
        if (not conversation_started):
            print "Resting ..."
            rest()
            print "Done."
        else:
            print "First end or discard current conversation."
    
    # ----- IO commands -----
    def do_save(self, arg):
        'Load weights to file.'
        print "Saving bootstrapped neurosequencers."
        modules.save()
    
    def do_load(self, arg):
        'Load weights from file.'
        print "Loading bootstrapped neurosequencers."
        modules.load()
  
    def do_show(self, arg):
        print "Collected conversations:"
        for c in conversations:
            for (a,b) in c:
                print a
                print b
                print "---"
            print "___"
        
    # ----- processing commands -----
    
    def do_test(self,arg):
        'Test syllable and letter composition'
        print "Processing \""+arg+"\""
        modules.test([arg], True)
    
    def do_say(self, arg):
        'Say something to the bot'
        if (not conversation_started):
            print "First, start a conversation."
        else:
            print "Processing \""+arg+"\""
            print "<== "+process(arg)
    
    # ----------
    
    def default(self, arg):
        print "Invalid command!"
    
    def precmd(self, line):
        if line <> "EOF":
            line = line.lower()
        return line
    
    def emptyline(self):
        return 0

# start the shell!
Shell().cmdloop()