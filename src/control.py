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


import numpy, cmd, readline, sys, os, random



class Control:
    # Modules loaded
    modules = None
    
    # Conversation state
    conversation_started = False
    lastp                = None
    conversations        = []
    conversation         = []

    # Language
    language = None

    # Information
    interface = None
    debug     = False
    version   = None

    def __init__(self, language, interface, version):
        
        self.interface = interface
        self.language = language
        self.version = version
        
        sys.path.append(os.path.join("src","languages",language))
        self.modules = __import__("modules")
   
    # Conversation definitions
    
    def start_conversation(self):
        modules = self.modules
        
        modules.reset()
        
        self.lastp = modules.initial_phrase 
        self.lastp = numpy.array([self.lastp])
        
        self.conversation = []
        self.conversation_started = True
        print "Conversation started."
    
    def end_conversation(self):
        self.conversation_started = False
        self.conversations.append(self.conversation)
        
        print "Conversation ended."
    def discard_conversation(self):
        self.conversation_started = False
        self.conversation = []
        
        print "Conversation aborted."
    
    # Cognitive definitions
    
    def process(self,inp):
        
        if (not self.conversation_started):
            print "First, start a conversation."
            return
        
        print "Processing \""+inp+"\""
        
        modules = self.modules
        
        # This is just an stub
        (p, ws) =  modules.input(inp)
        out = modules.output(p,3,3,3) # How to adjust this parameters ?
        self.conversation.append((self.lastp,ws))
        self.lastp = p
        print "<== "+out
    
    def bootstrap(self):
        modules = self.modules
        print "Bootstrapping "+self.language+" This can take a while..."
        # Where is corpus ??
        modules.bootstrap(modules.corpus, self.debug)
        
    def rest(self):
        
        if (self.conversation_started):
            print "First end or discard current conversation."
            return
    
        modules = self.modules
        
        # This is just a stub
        its = 100
        print "Resting ..."
        for it in range(its):
            perm = numpy.random.permutation(range(len(self.conversations)))
            for i in perm:
                c = self.conversations[i]
                modules.reset()
                for (lp,ws) in c:
                    if (not numpy.linalg.norm(lp) < 0.001):
                        modules.learn(lp,ws)
                        out = modules.output(lp,3,3,3)
                        if (it % 10 == 0):
                            print out            
        
            if (it % 10 == 0):
                print "---"
    
        print "Done."
        
    def test_word_composition(self, word):
        
        modules = self.modules
        
        print "Processing \""+word+"\""
        modules.test([word], True)
    
    # IO definitions
    
    def save(self):
        modules = self.modules
        
        print "Saving bootstrapped neurosequencers."
        modules.save()
        
    def load(self):
        modules = self.modules
        
        print "Loading bootstrapped neurosequencers."
        modules.load()
  
    
    # Basic commands definitions
    
    def toggle_debug(self):
        self.debug = not self.debug
        print "Debug is "+str(self.debug)
    def show_version(self):
        print self.version
        

class Shell(cmd.Cmd):
    #intro = 'Welcome to the reserbot ("""'+version.lower()+'"""") shell. \nType help or ? to list commands.\n'
    intro  = ' '
    prompt = '--> '
    
    def __init__(self, language, interface, version):
    
        
        self.interface = interface
        
        if (self.interface == "console"):
            #import sys
            self.stdin = sys.stdin
            self.stdout = sys.stdout
            self.cmdqueue = []
            self.completekey = 'tab'
        
        #elif (self.interface == "jabber"):
        #    
        #    sys.path.append(os.path.join("src","jabberbot"))
        #    import jabberbot 
        #    username = ''
        #    password = ''
        #    bot = jabberbot.JabberBot(username,password,res="FCEIA")
        #    conn = bot.connect()
        #    
        #    while (True):
        #        conn.Process(1)
        #        
        else:
            print "Unknown interface."
            
        self.control = Control(language,interface, version)
    
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
        self.control.show_version()
        
    def do_debug(self, arg):
        'Toggle debug'
        self.control.toggle_debug()
        
    
    # ----- conversation commands -----
    
    def do_start(self, arg):
        'Start conversation'
        self.control.start_conversation()
    
    def do_end(self, arg):
        'End conversation'
        self.control.end_conversation()
    
    def do_discard(self, arg):
        'Abort current conversation'
        self.control.discard_conversation()
    
    
    def do_bootstrap(self, arg):
        'Start bootstrapping process.'
        self.control.bootstrap()
        
    def do_rest(self, arg):
        'Train brain with recent conversations'
        self.control.rest()
        
    # ----- IO commands -----
    def do_save(self, arg):
        'Load weights to file.'
        self.control.save()
    
    def do_load(self, arg):
        'Load weights from file.'
        self.control.load()
        
    """def do_show(self, arg):
        print "Collected conversations:"
        for c in conversations:
            for (a,b) in c:
                print a
                print b
                print "---"
            print "___"
    """    
    # ----- processing commands -----
    
    def do_test(self,arg):
        'Test syllable and letter composition'
        self.control.test_word_composition(arg)
    
    def do_say(self, arg):
        'Say something to the bot'
        self.control.process(arg)
    
    # ----------
    
    def default(self, arg):
        print "Invalid command!"
    
    def precmd(self, line):
        if line <> "EOF":
            line = line.lower()
        return line
    
    def emptyline(self):
        return 0

