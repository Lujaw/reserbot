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

import cmd, readline, sys

def process(inp):
    (p, ws) =  input(inp)
    out = output(p,3,3,3)
    return out


class Shell(cmd.Cmd):
    intro = 'Welcome to the reserbot shell.   Type help or ? to list commands.\n'
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
    
    def do_start(self, arg):
        'Start conversation'
        print "Conversation started."
    
    def do_end(self, arg):
        'End conversation'
        print "Conversation ended."
    
    def do_bootstrap(self, arg):
        'Start bootstrapping process.'
        print "Bootstrapping toki pona. This can take a while..."
        bootstrap(corpus, True)
        
    def do_save(self, arg):
        'Load weights to file.'
        print "Saving bootstrapped neurosequencers."
        save()
    
    def do_load(self, arg):
        'Load weights from file.'
        print "Loading bootstrapped neurosequencers."
        load()
        
    def do_say(self, arg):
        'Say something to the bot'
        print "Processing \""+arg+"\""
        print "<== "+process(arg)
        
    def default(self, arg):
        print "Invalid command!"
    
    def precmd(self, line):
        if line <> "EOF":
            line = line.lower()
        return line
    
    def emptyline(self):
        return 0
    

Shell().cmdloop()

"""
#lastp = numpy.repeat(0,phrase_len) # null phrase, at the beggining of conversation 
while (True):
    print "--> ",
    inp = raw_input()
    print "<== "+response
    #learn(lastp,ws)
    
    #lastp = p
"""