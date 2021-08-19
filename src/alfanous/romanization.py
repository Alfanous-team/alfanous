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
BUCKWALTER2UNICODE = {
                u"'": u"\u0621", # hamza-on-the-line
                u"|": u"\u0622", # madda
                u">": u"\u0623", # hamza-on-'alif
                u"&": u"\u0624", # hamza-on-waaw
                u"<": u"\u0625", # hamza-under-'alif
                u"}": u"\u0626", # hamza-on-yaa'
                u"A": u"\u0627", # bare 'alif
                u"b": u"\u0628", # baa'
                u"p": u"\u0629", # taa' marbuuTa
                u"t": u"\u062A", # taa'
                u"v": u"\u062B", # thaa'
                u"j": u"\u062C", # jiim
                u"H": u"\u062D", # Haa'
                u"x": u"\u062E", # khaa'
                u"d": u"\u062F", # daal
                u"*": u"\u0630", # dhaal
                u"r": u"\u0631", # raa'
                u"z": u"\u0632", # zaay
                u"s": u"\u0633", # siin
                u"$": u"\u0634", # shiin
                u"S": u"\u0635", # Saad
                u"D": u"\u0636", # Daad
                u"T": u"\u0637", # Taa'
                u"Z": u"\u0638", # Zaa' (DHaa')
                u"E": u"\u0639", # cayn
                u"g": u"\u063A", # ghayn
                u"_": u"\u0640", # taTwiil
                u"f": u"\u0641", # faa'
                u"q": u"\u0642", # qaaf
                u"k": u"\u0643", # kaaf
                u"l": u"\u0644", # laam
                u"m": u"\u0645", # miim
                u"n": u"\u0646", # nuun
                u"h": u"\u0647", # haa'
                u"w": u"\u0648", # waaw
                u"Y": u"\u0649", # 'alif maqSuura
                u"y": u"\u064A", # yaa'
                u"F": u"\u064B", # fatHatayn
                u"N": u"\u064C", # Dammatayn
                u"K": u"\u064D", # kasratayn
                u"a": u"\u064E", # fatHa
                u"u": u"\u064F", # Damma
                u"i": u"\u0650", # kasra
                u"~": u"\u0651", # shaddah
                u"o": u"\u0652", # sukuun
                u"`": u"\u0670", # dagger 'alif
                u"{": u"\u0671", # waSla
                #extended here
                u"^": u"\u0653", # Maddah
                u"#": u"\u0654", # HamzaAbove

                u":"  : u"\u06DC", # SmallHighSeen
                u"@"  : u"\u06DF", # SmallHighRoundedZero
                u"\"" : u"\u06E0", # SmallHighUprightRectangularZero
                u"["  : u"\u06E2", # SmallHighMeemIsolatedForm
                u";"  : u"\u06E3", # SmallLowSeen
                u","  : u"\u06E5", # SmallWaw
                u"."  : u"\u06E6", # SmallYa
                u"!"  : u"\u06E8", # SmallHighNoon
                u"-"  : u"\u06EA", # EmptyCentreLowStop
                u"+"  : u"\u06EB", # EmptyCentreHighStop
                u"%"  : u"\u06EC", # RoundedHighStopWithFilledCentre
                u"]"  : u"\u06ED"          #

                }

# ISO233-2 romanization letter mapping
ISO2UNICODE = { u"ˌ": u"\u0621", # hamza-on-the-line
                #u"|": u"\u0622", # madda
                u"ˈ": u"\u0623", # hamza-on-'alif
                u"ˈ": u"\u0624", # hamza-on-waaw
                #u"<": u"\u0625", # hamza-under-'alif
                u"ˈ": u"\u0626", # hamza-on-yaa'
                u"ʾ": u"\u0627", # bare 'alif
                u"b": u"\u0628", # baa'
                u"ẗ": u"\u0629", # taa' marbuuTa
                u"t": u"\u062A", # taa'
                u"ṯ": u"\u062B", # thaa'
                u"ǧ": u"\u062C", # jiim
                u"ḥ": u"\u062D", # Haa'
                u"ẖ": u"\u062E", # khaa'
                u"d": u"\u062F", # daal
                u"ḏ": u"\u0630", # dhaal
                u"r": u"\u0631", # raa'
                u"z": u"\u0632", # zaay
                u"s": u"\u0633", # siin
                u"š": u"\u0634", # shiin
                u"ṣ": u"\u0635", # Saad
                u"ḍ": u"\u0636", # Daad
                u"ṭ": u"\u0637", # Taa'
                u"ẓ": u"\u0638", # Zaa' (DHaa')
                u"ʿ": u"\u0639", # cayn
                u"ġ": u"\u063A", # ghayn
                #u"_": u"\u0640", # taTwiil
                u"f": u"\u0641", # faa'
                u"q": u"\u0642", # qaaf
                u"k": u"\u0643", # kaaf
                u"l": u"\u0644", # laam
                u"m": u"\u0645", # miim
                u"n": u"\u0646", # nuun
                u"h": u"\u0647", # haa'
                u"w": u"\u0648", # waaw
                u"ỳ": u"\u0649", # 'alif maqSuura
                u"y": u"\u064A", # yaa'
                u"á": u"\u064B", # fatHatayn
                u"ú": u"\u064C", # Dammatayn
                u"í": u"\u064D", # kasratayn
                u"a": u"\u064E", # fatHa
                u"u": u"\u064F", # Damma
                u"i": u"\u0650", # kasra
                #u"~": u"\u0651", # shaddah
                u"°": u"\u0652", # sukuun
                #u"`": u"\u0670", # dagger 'alif
                #u"{": u"\u0671", # waSla
                ##extended here
                #u"^": u"\u0653", # Maddah
                #u"#": u"\u0654", # HamzaAbove

                #u":"  : "\u06DC", # SmallHighSeen
                #u"@"  : "\u06DF", # SmallHighRoundedZero
                #u"\"" : "\u06E0", # SmallHighUprightRectangularZero
                #u"["  : "\u06E2", # SmallHighMeemIsolatedForm
                #u";"  : "\u06E3", # SmallLowSeen
                #u","  : "\u06E5", # SmallWaw
                #u"."  : "\u06E6", # SmallYa
                #u"!"  : "\u06E8", # SmallHighNoon
                #u"-"  : "\u06EA", # EmptyCentreLowStop
                #u"+"  : "\u06EB", # EmptyCentreHighStop
                #u"%"  : "\u06EC", # RoundedHighStopWithFilledCentre
                #u"]"  : "\u06ED"          #

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


def transliterate( mode, string, ignore = u"" , reverse = False ):
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
			result += mapping[ char ] #test
		else :
			result += char
	return result

