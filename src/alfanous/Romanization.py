# coding: utf-8


##     Copyright (C) 2009-2012 Assem Chelli <assem.ch [at] gmail.com>

##     This program is free software: you can redistribute it and/or modify
##     it under the terms of the GNU Affero General Public License as published by
##     the Free Software Foundation, either version 3 of the License, or
##     (at your option) any later version.

##     This program is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU Affero General Public License for more details.

##     You should have received a copy of the GNU Affero General Public License
##     along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Buckwalter Romanization  letters mapping
BUCKWALTER2UNICODE = {"'": u"\u0621", # hamza-on-the-line
                "|": u"\u0622", # madda
                ">": u"\u0623", # hamza-on-'alif
                "&": u"\u0624", # hamza-on-waaw
                "<": u"\u0625", # hamza-under-'alif
                "}": u"\u0626", # hamza-on-yaa'
                "A": u"\u0627", # bare 'alif
                "b": u"\u0628", # baa'
                "p": u"\u0629", # taa' marbuuTa
                "t": u"\u062A", # taa'
                "v": u"\u062B", # thaa'
                "j": u"\u062C", # jiim
                "H": u"\u062D", # Haa'
                "x": u"\u062E", # khaa'
                "d": u"\u062F", # daal
                "*": u"\u0630", # dhaal
                "r": u"\u0631", # raa'
                "z": u"\u0632", # zaay
                "s": u"\u0633", # siin
                "$": u"\u0634", # shiin
                "S": u"\u0635", # Saad
                "D": u"\u0636", # Daad
                "T": u"\u0637", # Taa'
                "Z": u"\u0638", # Zaa' (DHaa')
                "E": u"\u0639", # cayn
                "g": u"\u063A", # ghayn
                "_": u"\u0640", # taTwiil
                "f": u"\u0641", # faa'
                "q": u"\u0642", # qaaf
                "k": u"\u0643", # kaaf
                "l": u"\u0644", # laam
                "m": u"\u0645", # miim
                "n": u"\u0646", # nuun
                "h": u"\u0647", # haa'
                "w": u"\u0648", # waaw
                "Y": u"\u0649", # 'alif maqSuura
                "y": u"\u064A", # yaa'
                "F": u"\u064B", # fatHatayn
                "N": u"\u064C", # Dammatayn
                "K": u"\u064D", # kasratayn
                "a": u"\u064E", # fatHa
                "u": u"\u064F", # Damma
                "i": u"\u0650", # kasra
                "~": u"\u0651", # shaddah
                "o": u"\u0652", # sukuun
                "`": u"\u0670", # dagger 'alif
                "{": u"\u0671", # waSla
                #extended here
                "^": u"\u0653", # Maddah
                "#": u"\u0654", # HamzaAbove

                ":"  : "\u06DC", # SmallHighSeen
                "@"  : "\u06DF", # SmallHighRoundedZero
                "\"" : "\u06E0", # SmallHighUprightRectangularZero
                "["  : "\u06E2", # SmallHighMeemIsolatedForm
                ";"  : "\u06E3", # SmallLowSeen
                ","  : "\u06E5", # SmallWaw
                "."  : "\u06E6", # SmallYa
                "!"  : "\u06E8", # SmallHighNoon
                "-"  : "\u06EA", # EmptyCentreLowStop
                "+"  : "\u06EB", # EmptyCentreHighStop
                "%"  : "\u06EC", # RoundedHighStopWithFilledCentre
                "]"  : "\u06ED"          #

                }

# ISO233-2 romanization letter mapping
ISO2UNICODE = { "ˌ": u"\u0621", # hamza-on-the-line
                #"|": u"\u0622", # madda
                "ˈ": u"\u0623", # hamza-on-'alif
                "ˈ": u"\u0624", # hamza-on-waaw
                #"<": u"\u0625", # hamza-under-'alif
                "ˈ": u"\u0626", # hamza-on-yaa'
                "ʾ": u"\u0627", # bare 'alif
                "b": u"\u0628", # baa'
                "ẗ": u"\u0629", # taa' marbuuTa
                "t": u"\u062A", # taa'
                "ṯ": u"\u062B", # thaa'
                "ǧ": u"\u062C", # jiim
                "ḥ": u"\u062D", # Haa'
                "ẖ": u"\u062E", # khaa'
                "d": u"\u062F", # daal
                "ḏ": u"\u0630", # dhaal
                "r": u"\u0631", # raa'
                "z": u"\u0632", # zaay
                "s": u"\u0633", # siin
                "š": u"\u0634", # shiin
                "ṣ": u"\u0635", # Saad
                "ḍ": u"\u0636", # Daad
                "ṭ": u"\u0637", # Taa'
                "ẓ": u"\u0638", # Zaa' (DHaa')
                "ʿ": u"\u0639", # cayn
                "ġ": u"\u063A", # ghayn
                #"_": u"\u0640", # taTwiil
                "f": u"\u0641", # faa'
                "q": u"\u0642", # qaaf
                "k": u"\u0643", # kaaf
                "l": u"\u0644", # laam
                "m": u"\u0645", # miim
                "n": u"\u0646", # nuun
                "h": u"\u0647", # haa'
                "w": u"\u0648", # waaw
                "ỳ": u"\u0649", # 'alif maqSuura
                "y": u"\u064A", # yaa'
                "á": u"\u064B", # fatHatayn
                "ú": u"\u064C", # Dammatayn
                "í": u"\u064D", # kasratayn
                "a": u"\u064E", # fatHa
                "u": u"\u064F", # Damma
                "i": u"\u0650", # kasra
                #"~": u"\u0651", # shaddah
                "°": u"\u0652", # sukuun
                #"`": u"\u0670", # dagger 'alif
                #"{": u"\u0671", # waSla
                ##extended here
                #"^": u"\u0653", # Maddah
                #"#": u"\u0654", # HamzaAbove

                #":"  : "\u06DC", # SmallHighSeen
                #"@"  : "\u06DF", # SmallHighRoundedZero
                #"\"" : "\u06E0", # SmallHighUprightRectangularZero
                #"["  : "\u06E2", # SmallHighMeemIsolatedForm
                #";"  : "\u06E3", # SmallLowSeen
                #","  : "\u06E5", # SmallWaw
                #"."  : "\u06E6", # SmallYa
                #"!"  : "\u06E8", # SmallHighNoon
                #"-"  : "\u06EA", # EmptyCentreLowStop
                #"+"  : "\u06EB", # EmptyCentreHighStop
                #"%"  : "\u06EC", # RoundedHighStopWithFilledCentre
                #"]"  : "\u06ED"          #

                }

# Available romanization systems
ROMANIZATION_SYSTEMS_MAPPINGS = {
					"buckwalter":BUCKWALTER2UNICODE,
					"iso": ISO2UNICODE,
					"arabtex": None,
					}



def guess_romanization_system():
	""" @todo """
	pass


def transliterate( mode, string, ignore = "" , reverse = False ):
	""" encode & decode different  romanization systems """

	if ROMANIZATION_SYSTEMS_MAPPINGS.has_key( mode ):
		MAPPING = ROMANIZATION_SYSTEMS_MAPPINGS[mode]
	else:
		MAPPING = {}

	if reverse:
		mapping = {}
		for k, v in MAPPING.items():
			#reverse the mapping buckwalter <-> unicode
			mapping[v] = k
	else:
		mapping = MAPPING

	result = ""
	for char in string :
		if mapping.has_key( char ) and char not in ignore:
			result += mapping[char]
		else :
			result += char
	return result

