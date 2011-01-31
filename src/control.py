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
from conv import *

class Control:
    # Modules loaded
    modules = None
    
    # Conversation state
    conversation = None
    conversations = []


    # Language
    language = None

    # Information
    interface = None
    debug     = False
    version   = None

    def __init__(self, language, version, stdout):
        
        self.language = language
        self.version = version
        
        self.stdout = stdout
        
        try: 
            sys.path.append(os.path.join("src","languages",language))
            self.modules = __import__("modules")
        except ImportError:
            print ""
            print "language:",language,"is not available"
            sys.exit(-1)
            
        self.conversation = Conversation()
   
    # Conversation definitions
    
    def start_conversation(self):
        modules = self.modules
        
        modules.reset()
        
        self.conversation = Conversation()
        self.conversation.start()
        
        initial_phrase = numpy.array([modules.initial_phrase])
        self.conversation.add_processed_phrase(initial_phrase)

        self.stdout.write("Conversation started.\n")
    
    def end_conversation(self):
        self.conversation.end()
        self.conversations.append(self.conversation)     
        self.stdout.write("Conversation ended.\n")
        
    def discard_conversation(self):
        self.conversation.end()
        self.stdout.write("Conversation aborted.\n")
        
    def clean_conversations(self):
        self.conversation.end()
        self.conversations = []
        self.stdout.write("Conversations cleaned.\n")
        
    #def give_feedback(self,args):
    #    
    #    modules = self.modules
    #    
    #    #Primitive feedback system   
    #    if args == "+":
    #        out = modules.output(self.lastp,5,5,5)
    #        
    #        if (not self.debug):
    #            out = filter(lambda c: c <> "-", out)
    #        
    #        self.stdout.write("feedback is "+args+"\n")
    #        self.stdout.write("prediction: "+out+"\n")
    #
    
    # Cognitive definitions
    
    def process(self,inp):
        
        if (not self.conversation.started):
            self.stdout.write("First, start a conversation.\n")
            return
        
        self.stdout.write("Processing \""+inp+"\"\n")
        
        modules = self.modules
            
        # This is just an stub
        (p, ws) =  modules.input(inp)
        out = modules.output(p,5,5,5) # How to adjust this parameters ?
        
        self.conversation.add_processed_words(ws)    
        self.conversation.add_processed_phrase(p)
        
        
        if (not self.debug):
            out = filter(lambda c: c <> "-", out)
        
        self.stdout.write("<== "+out+"\n")
        
    def bootstrap(self):
        
        if (self.conversation.started):
            self.stdout.write("First end or discard current conversation.\n")
            return

        modules = self.modules
        self.stdout.write("Bootstrapping "+self.language+" This can take a while...\n")
        modules.bootstrap(modules.corpus, 0.1, 0.001, 30, True, self.debug)
        
    def rest(self):
        
        if (self.conversation.started):
            self.stdout.write("First end or discard current conversation.\n")
            return
        
        
        if (self.conversations == []):
            self.stdout.write("No conversations available for resting.\n")
            return
        
    
        modules = self.modules
        
        #modules.bootstrap(modules.corpus, 0.001, 0.001, 2, False, self.debug)
        
        # This is NOT definitive (just a stub)
        
        its = 100*len(self.conversations)
        
        self.stdout.write("Resting ...\n")
        self.stdout.write("(wait please)\n")
        
        clist = map( lambda c: c.processed_phrases(), self.conversations)
        modules.freshmem(clist)
        
        for it in range(its):
            perm = numpy.random.permutation(range(len(self.conversations)))
            for i in perm:
                c = self.conversations[i].processed_words_phrases()
                modules.reset()
                for (p,ws) in c[1:]:

                    modules.learn(p,ws)
                    out = modules.output(p,3,3,3)
                    #if (it % 10 == 0):
                    #    print filter(lambda c: c <> "-", out)            
            
        self.stdout.write("Done.\n")
        
    #def sleep(self):
    #    
    #    modules = self.modules
    #    self.stdout.write("Consolidating knowledge ...\n")
    #    modules.consolidate()
    #    self.stdout.write("Done!\n")
   
    def test_word_composition(self, word):
        
        modules = self.modules
        
        word = filter(lambda c: c<> "\"", word)
        
        self.stdout.write("Processing \""+word+"\"\n")
        (s,f) = modules.test([word], self.debug)
        self.stdout.write(s)
    
    # IO definitions
    
    def save(self):
        modules = self.modules
        
        self.stdout.write("Saving bootstrapped neurosequencers.\n")
        self.stdout.write(modules.save())
        
    def load(self):
        
        if (self.conversation.started):
            self.stdout.write("First end or discard current conversation.\n")
            return
        
        modules = self.modules
        
        self.stdout.write("Loading bootstrapped neurosequencers.\n")
        self.stdout.write(modules.load())
        self.clean_conversations()
  
    
    # Basic commands definitions
    
    def toggle_debug(self):
        self.debug = not self.debug
        self.stdout.write("Debug is "+str(self.debug)+"\n")
    def show_version(self):
        self.stdout.write(self.version)
        

class Shell(cmd.Cmd):
    intro  = None
    prompt = '--> '
    
    def __init__(self, intro, language, version, stdin = None, stdout = None):
    
        self.stdin = stdin
        self.stdout = stdout
        self.cmdqueue = []
        self.completekey = 'tab'
        
        self.control = Control(language, version, stdout)
        self.stdout.write(str(intro)+"\n")
        self.stdout.write(version+"\n")
        self.stdout.write("Type help or ? to list commands.\n")
    
    # ----- basic commands -----
    
    def do_quit(self, arg):
        'Quit.'
        self.stdout.write("bye!\n")
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
    
    def do_clean(self, arg):
        'Abort current conversation and delete conversation log'
        self.control.clean_conversations()
    
    #def do_feedback(self, arg):
    #    'Give feedback during the conversation'
    #    self.control.give_feedback(arg)
    
    def do_bootstrap(self, arg):
        'Start bootstrapping process.'
        self.control.bootstrap()
        
    def do_rest(self, arg):
        'Train brain with recent conversations'
        self.control.rest()
        
    def do_sleep(self, arg):
        ''
        self.control.sleep()
        
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
        self.stdout.write("Invalid command!\n")
    
    def precmd(self, line):
        
        # comments support
        if line <> "" and line.lstrip()[0] == "#":
            return ""
            
        if line <> "EOF":
            line = line.lower()
        return line
    
    def emptyline(self):
        self.stdout.write("\n")
        return ""


def mkShell(intro, args, version):
    
    if (args.interface == "console"):
        import sys
        Shell(intro, args.language, version, sys.stdin, sys.stdout).cmdloop()
        
    elif (args.interface == "jabber"):
        
        import sys    
        if args.username == None:
            print "You have to specify a username to use jabber interface"
            sys.exit(-1)
        if args.password == None:
            print "You have to specify a password to use jabber interface"
            sys.exit(-1)
        if args.jid == None:
            print "You have to specify a jid to use jabber interface"
            sys.exit(-1)
        
        sys.path.append(os.path.join("src","jabber"))
        import jabberbot
        
        bot = jabberbot.JabberBot(args.username,args.password)
        conn = bot.connect()
        
        if not conn:
            sys.exit(-1)
        
        # bot is online!
        jstdout = type('writable', (object,), {'write' : (lambda self,txt: bot.send(args.jid,txt))})()
        
        shell = Shell(intro, args.language, version, None, jstdout)
        bot.setmycallback(shell.onecmd,args.jid)

        while (True):
            conn.Process(1)
            
    else:
        print "Unknown interface."
        

