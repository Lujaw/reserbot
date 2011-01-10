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

import argparse
import control as ctr

version = "Alpha 0 - Codename: Ralph Wiggum (\"I\'m special!\")"
ascii_intro = """
 _   _______ _____ _   __
| | | | ___ \_   _| | / /
| | | | |_/ / | | | |/ / 
| | | | ___ \ | | |    \ 
| |_| | |_/ /_| |_| |\  \\
 \___/\____/ \___/\_| \_/

I am Ubik. Before the universe was I am. I made the suns. I made the worlds.
I created the lives and the places they inhabit;
I move them here, I put them there. They go as I say, they do as I tell them.
I am the word and my name is never spoken, the name which no one knows.
I am called Ubik but that is not my name. I am. I shall always be.
"""

parser = argparse.ArgumentParser(description='Reserbot')
parser.add_argument('language', help='A language to use.')
parser.add_argument('--interface', dest='interface', action='store',
                   default="console",
                   help='An interface to use (default is console).')


args = parser.parse_args()

print ascii_intro
print version

ctr.Shell(args.language, args.interface, version).cmdloop()
