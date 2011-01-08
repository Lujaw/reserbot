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

extra_words = ["."]

corpus = map( lambda ls: filter((lambda l: l<>'\n'),ls), open('tokipona_corpus.txt','r').readlines())+extra_words
    
syllable = [
	    "a-",	"e-",	"i-",	"o-",	"u",
            "ka-",	"ke-",	"ki-",	"ko-",	"ku-",
            "sa-",	"se-",	"si-",	"so-",	"su-", 
	    "ta-",	"te-",		"to-",	"tu-",
	    "na-",	"ne-",	"ni-",	"no-",	"nu-",
	    "pa-",	"pe-",	"pi-",	"po-",	"pu-",
	    "ma-",	"me-",	"mi-",	"mo-",	"mu-",
	    "ja-",	"je-",		"jo-",
	    "jan-",	"wan-",	"lin-",	"sin-",	"kon-",
	    "ten-",	"mon-",	"tan-",	"ken-",
	    "la-",	"le-",	"li-",	"lo-",	"lu-",
	    "wa-",	"we-",	"wi-",
	    "len-",	"wen-", "sin-",	"pin-",	"lon-",
	    "pan-",	"kin-",	"pen-",	"nan-",	"mun-",
	    "an-",	"in-",	"en-",	"un-",	"es-",
	    " ",	"."
           ]
	   
syllable =  sorted(syllable, key = len, reverse = True)
abc = "abcdefghijklmnopqrstuvwxyz-. "

def silabizar(w,ss):
    wo = w
    r = []
    while (w<>""):
        f = False
        for s in ss:
            if (s in  w[0:len(s)]):
                f = True
                r.append(s)
                w = w[len(s):]
                break
        if (not f):
            print "Silabizacion fallida en "+w+" ("+wo+") !"
            assert(False)
    return r 
