########################################################################
#JPwordsearch Version 0.9, Momodath 28/09/2020
########################################################################

import re
from colorama import init, Fore, Back, Style

from sudachipy import tokenizer, dictionary

tokenizer_obj = dictionary.Dictionary().create()

from xml.etree import ElementTree as ET

kanji_xml_path = '/Users/earth/Documents/Programming/My own Japanese programs/Lets make cards/kanjidic2.xml'
jpdict_xml_path = '/Users/earth/Documents/Programming/My own Japanese programs/Lets make cards/JMdict_e.xml'

kanjitree = ET.parse(kanji_xml_path)
JPtree = ET.parse(jpdict_xml_path).findall('entry')

########################################################################
							#Endings

#Verbs
_い_る = ('_い_る', 'る', 'ない', 'ます', 'ません', 'よう', 'ましょう', 'るでしょう', 'ないでしょう', 'ろ', 'るな', 'て', 'ないで', 'た', 'なかった', 'ました', 'ませんでした', 'たろう', 'ただろう', 'なかっただろう', 'たでしょう', 'なかったでしょう', 'れば', 'なければ', 'たら', 'なかったら', 'ましたら', 'ませんでしたら', 'られる', 'られない', 'られます', 'られません', 'させる', 'させない', 'させます', 'させません', 'ないで')
う = ('_う', 'う', 'わない', 'います', 'いません', 'おう', 'わないだろう', 'いましょう', 'うでしょう', 'わないでしょう', 'え', 'うな', 'ってください', 'わないでください', 'った', 'わなかった', 'いました', 'いませんでした', 'っただろう', 'わなかっただろう', 'ったでしょう', 'わなかったでしょう', 'って', 'えば', 'わなければ', 'ったら', 'わなかったら', 'いましたら', 'いませんでしたら', 'える', 'えない', 'えます', 'えません', 'わせる', 'わせない', 'わせます', 'わせません', 'われる', 'われない', 'われます', 'われません', 'わないで')
_え_る = ('_え_る_', 'る', 'えない', 'えます', 'えません', 'えよう', 'える', 'えましょう', 'えるでしょう', 'えないでしょう', 'えろ', 'えるな', 'えて', 'えないで', 'えた', 'えなかった', 'えました', 'えませんでした', 'えたろう', 'えただろう', 'えなかっただろう', 'えたでしょう', 'えなかったでしょう', 'えれば', 'えなければ', 'えたら', 'えなかったら', 'えましたら', 'えませんでしたら', 'えられる', 'えられない', 'えられます', 'えられません', 'えさせる', 'えさせない', 'えさせます', 'えさせません', 'えないで')
く = ('_く', 'く', 'かない', 'きます', 'きません', 'こう', 'かないだろう', 'きましょう', 'くでしょう', 'かないでしょう', 'け', 'くな', 'いてください', 'かないでください', 'いた', 'かなかった', 'きました', 'きませんでした', 'いただろう', 'かなかっただろう', 'いたでしょう', 'かなかったでしょう', 'いて', 'けば', 'かなければ', 'いたら', 'かなかったら', 'きましたら', 'きませんでしたら', 'ける', 'けない', 'けます', 'けません', 'かせる', 'かせない', 'かせます', 'かせません', 'かれる', 'かれない', 'かれます', 'かれません', 'かないで')
ぐ = ('_ぐ', 'ぐ', 'がない', 'ぎます', 'ぎません', 'ご', 'がないだろう', 'ぎましょう', 'ぐでしょう', 'がないでしょう', 'げ', 'ぐな', 'いでください', 'がないでください', 'いだ', 'がなかった', 'ぎました', 'ぎませんでした', 'いだだろう', 'がなかっただろう', 'いだでしょう', 'がなかったでしょう', 'いで', 'げば', 'がなければ', 'いだら', 'がなかったら', 'ぎましたら', 'ぎませんでしたら', 'げる', 'げない', 'げます', 'げません', 'がせる', 'がせない', 'がせます', 'がせません', 'がれる', 'がれない', 'がれます', 'がれません', 'がないで')
くる = ('_くる', 'る', 'ます', 'るでしょう', 'い', 'てください', 'た', 'ました', 'たでしょう', 'れば', 'ますれば', 'たら', 'ましたら', 'られる', 'られます', 'させる', 'させます')
す = ('_す', 'す', 'さない', 'します', 'しません', 'そう', 'さないだろう', 'しましょう', 'すでしょう', 'さないでしょう', 'せ', 'すな', 'してください', 'さないでください', 'した', 'さなかった', 'しました', 'しませんでした', 'しただろう', 'さなかっただろう', 'したでしょう', 'さなかったでしょう', 'して', 'せば', 'さなければ', 'したら', 'さなかったら', 'しましたら', 'しませんでしたら', 'せる', 'せない', 'せます', 'せません', 'させる', 'させます', 'させません', 'される', 'されない', 'されます', 'されません', 'さないで')
する = ('_する', 'する', 'します', 'した', 'しました', 'するだろう', 'するでしょう', 'しただろう', 'しましたろう', 'しています', 'していました', 'すれば', 'しますれば', 'したら', 'しましたら', 'できる', 'できます', 'させる', 'しろ', 'して','してください', 'しないで')
つ = ('_つ', 'つ', 'たない', 'ちます', 'ちません', 'とう', 'たないだろう', 'ちましょう', 'つでしょう', 'たないでしょう', 'て', 'つな', 'ってください', 'たないでください', 'った', 'たなかった', 'ちました', 'ちませんでした', 'っただろう', 'たなかっただろう', 'ったでしょう', 'たなかったでしょう', 'って', 'てば', 'たなければ', 'ったら', 'たなかったら', 'ちましたら', 'ちませんでしたら', 'てる', 'てない', 'てます', 'てません', 'たせる', 'たせない', 'たせます', 'たせません', 'たれる', 'たれない', 'たれます', 'たれません', 'たないで')
ぬ = ('_ぬ', 'ぬ', 'なない', 'にます', 'にません', 'のう', 'なないだろう', 'にましょう', 'ぬでしょう', 'なないでしょう', 'ね', 'ぬな', 'んでください', 'なないでください', 'んだ', 'ななかった', 'にました', 'にませんでした', 'んだだろう', 'ななかっただろう', 'んだでしょう', 'ななかったでしょう', 'んで', 'ねば', 'ななければ', 'んだら', 'ななかったら', 'にましたら', 'にませんでしたら', 'ねる', 'ねない', 'ねます', 'ねません', 'なせる', 'なせない', 'なせます', 'なせません', 'なれる', 'なれない', 'なれます', 'なれません', 'なないで')
む = ('_む', 'む', 'まない', 'みます', 'みません', 'もう', 'む', 'まないだろう', 'みまょう', 'むでょう', 'まないでょう', 'め', 'むな', 'んでください', 'まないでください', 'んだ', 'まなかった', 'みまた', 'みませんでた', 'んだだろう', 'まなかっただろう', 'んだでょう', 'まなかったでょう', 'んで', 'めば', 'まなければ', 'んだら', 'まなかったら', 'みまたら', 'みませんでたら', 'める', 'めない', 'めます', 'めません', 'ませる', 'ませない', 'ませます', 'ませません', 'まれる', 'まれない', 'まれます', 'まれません', 'まないで')
る = ('_る', 'る', 'らない', 'ります', 'りません', 'ろう', 'らないだろう', 'りましょう', 'るでしょう', 'らないでしょう', 'れ', 'るな', 'ってください', 'らないでください', 'った', 'らなかった', 'りました', 'りませんでした', 'っただろう', 'らなかっただろう', 'ったでしょう', 'らなかったでしょう', 'って', 'れば', 'らなければ', 'ったら', 'らなかったら', 'りましたら', 'りませんでしたら', 'れる', 'れない', 'れます', 'れません', 'らせる', 'らせない', 'らせます', 'らせません', 'られる', 'られない', 'られます', 'られません', 'らないで')

#Adjectives
い = ('_い',"い", "くない", "かった", "くなかった")
な = ('_な',"な")

#Fulldata is a list of all the values, to allow for easier searching. database is the lists split into their corresponding verbs
database = [_い_る, う, _え_る, く, ぐ, くる, す, する, つ, ぬ, む, る, い, な]
fulldata = (_い_る + う + _え_る + く + ぐ + くる + す + する + つ + ぬ + む + る + い + な)

########################################################################

katakana_chart = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ"
hiragana_chart = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ" 
hir2kat = str.maketrans(hiragana_chart, katakana_chart)
kat2hir  =str.maketrans(katakana_chart, hiragana_chart)

########################################################################

def kanji_check(strg, search=re.compile(r'[\u3400-\u4DB5\u4E00-\u9FCB\uF900-\uFA6A]').search):
	return bool(search(strg))

def colourise_sentence(sentencestr):
	return Fore.GREEN + sentencestr.replace("{",Fore.RESET + Style.NORMAL + Back.RED).replace("}",Fore.GREEN + Style.NORMAL + Back.RESET) +Fore.RESET

def furigana_cleaner(kanji, reading):

	formatted_string = "{Kanji}<{Reading}>".format(Kanji=kanji,Reading=reading)

	Readingregex = re.compile(r'''
	([\u3040-\u309F]*?)			#Line before reading    -GROUP 1-
	(?:\<)			  			#Opening square bracket -not captured-
	([^A-z0-9]+?)	  			#Kanji Reading          -GROUP 2-
	(?:\>)            			#Closing square bracket -not captured-
	''', re.VERBOSE)

	ReadingFinder = Readingregex.findall(formatted_string) #returns our readings as a list of two part tuples [ (okurigana, furigana), (ok, fg) ... ]

	###    OLD    ###
	OriginalFurigana = [  "".join( (item[0], "<" + item[1] + ">") ) for item in ReadingFinder] #grabs the original string, as captured by ReadingFinder, and joins it into one string, adding brackets

	###    NEW    ###
	#NewFurigana =  [  "[" + re.sub(item[0],"",i[1]) + "]" + item[0] for item in ReadingFinder] #For each tuple in ReadingFinder, deletes the text in [0](The Okurigana) FROM [1](The furigana) and swaps their positions ([1], [0]), adds sq brackets, and joins the whole thing as one string
	NewFurigana = ["<"+(re.sub(rf'{i[0]}$',"",i[1], count=1))+">"+i[0] for i in ReadingFinder]

	FuriganaDict = {}

	for x in range(len(NewFurigana)):
		FuriganaDict[OriginalFurigana[x]] = NewFurigana[x]
	
	for original, new in FuriganaDict.items():
		formatted_string = re.sub(original, new, formatted_string, count=1).replace("<","[").replace(">","]") #Note we have to do this with the brackets because the square brackets fuck with the regex

	return formatted_string

def generate_furigana(sentence):

	mode = tokenizer.Tokenizer.SplitMode.C
	parsed_sen = tokenizer_obj.tokenize(sentence, mode)

	word_list = [m.surface() for m in parsed_sen]
	word_readings = [m.reading_form() for m in parsed_sen]

	full_reading = ""

	for word in word_list:
		furigana_reading = []
		word_lookup = word_readings[word_list.index(word)]
		try:
			for char in word:
				if kanji_check(char):
					entry = kanjitree.find(f"character/[literal='{char}']")
					on = entry.findall("reading_meaning/rmgroup/reading[@r_type='ja_on']")
					kun = entry.findall("reading_meaning/rmgroup/reading[@r_type='ja_kun']")
					readings = [reading.text.split(".")[0] for reading in on+kun]
					readings = [i for i in readings if i.translate(kat2hir) in word_lookup.translate(kat2hir)]
					reading = max(readings, key=len)
					furigana_reading.append(reading)

				else:
					furigana_reading.append(None)

			word_reading = ""
			for i in range(len(word)):
				if furigana_reading[i]:
					word_reading += f' {word[i]}[{furigana_reading[i]}]'
				else:
					word_reading += word[i]
			full_reading += word_reading

		except:
			full_reading += f' {word}[{word_lookup}]'

	return(full_reading)

#Takes a Japanese verb in any form and returns the dictionary form, or returns None if nothing was found

##NOT USED ANYMORE##
def verbformat(wordinput, original_input = None, original_sentence = None):
	#Finds the longest item that matches the end of the wordinput, returns it to 's', if it finds a longer match it replaces it, this is necessary because we only want to search the longest match
	#(i.e. ました and した will both hit, but ました is obviously the correct ending because it is longer, if there are more than one it returns multiple)

	if type(wordinput) is list: #Converts the input to a str if it was a list
		wordinput = str(wordinput[0])

	dictforms = []

	p=0 #Updates per the len of our matched word, allowing us to override our match list if the len is longer
	match = ""

	for i in range(len(wordinput)):
		if wordinput[i:] in fulldata:
			for verblist in database:
				#Now we check each of our of discrete verb lists (the 'database') in turn, and see if 'match' is present in any of them
				if wordinput[i:] in verblist:
					#If we find a match, we know the verb could be one of those, and so we replace the matched ending with the correspondign dictionary form (position i[1])
					dictverb = wordinput.replace(wordinput[i:], verblist[1]) #We define this dictionary form as our 'dictverb' and return it
					dictforms.append(dictverb)
					if verblist == する:
						suru_noun = wordinput.replace(wordinput[i:],"")
						dictforms.append(suru_noun) #Just for suru nouns, we also add the noun as an option (note we do this after the suru verb, so that has priority)
			break
	return dictforms, original_input, original_sentence #this will be a list of the possible dict forms of the verb


class lookup_key:
	def __init__(self, searchword):
		self.senses = []
		
		for entry in JPtree:
			word_forms = entry.findall('k_ele/keb')
			senses = entry.findall('sense')

			try:
				for word in word_forms:
					if word.text == searchword:
						for sense in senses:
							gloss_list = sense.findall('gloss')
							self.senses.append([gloss.text for gloss in gloss_list])

						self.reading = entry.find('r_ele/reb').text
			except:
				pass



#Searches a list of Japanese words, and returns a list of definitions (lists can be a single item)
def jpwordsearch(searchlist, original_input = None, original_sentence = None):

	if type(searchlist) is str: #converts the input to a list if it was a str
		searchlist = [str(searchlist)]
	if not original_input: #If no seperate value is given for "original_input", use the value for "lookuplist" (this helps preserve it for passing to our other functions)
		original_input = searchlist[0]

	keyword = lookup_key(searchlist[0])

	if keyword.senses:
		return keyword, original_input, original_sentence
	else:
		return None, original_input, original_input

#defines the order to try the above, 1st straight wordsearch, then if no results a verb conjegation search
def jplookup(lookuplist, original_input=None, original_sentence = None):
	if lookuplist == None:
		return None

	if type(lookuplist) is not list: #Converts it to a list if it wasn't already
		lookuplist = [str(lookuplist)]

	if u'\u3099' or u'\u309A' in lookuplist[0]: #converts some nasty Unicode into the right thing
		pa_dict = {'は':'ぱ','ひ':'ぴ','ふ':'ぷ','へ':'ぺ','ほ':'ぽ','ハ':'パ','ヒ':'ピ','フ':'プ','ヘ':'ペ','ホ':'ポ'}
		ba_dict = {'か':'が','き':'ぎ','く':'ぐ','け':'げ','こ':'ご','さ':'ざ','し':'じ','す':'ず','せ':'ぜ','そ':'ぞ',
		   'た':'だ','ち':'ぢ','つ':'づ','て':'で','と':'ど','は':'ば','ひ':'び','ふ':'ぶ','へ':'べ','ほ':'ぼ',
		   'カ':'ガ','キ':'ギ','ク':'グ','ケ':'ゲ','コ':'ゴ','サ':'ザ','シ':'ジ','ス':'ズ','セ':'ゼ','ソ':'ゾ',
		   'タ':'ダ','チ':'ヂ','ツ':'ヅ','テ':'デ','ト':'ド','ハ':'バ','ヒ':'ビ','フ':'ブ','ヘ':'ベ','ホ':'ボ'}

		ba_dict_enc = {(i+u'\u3099'): j for i,j in ba_dict.items()}
		pa_dict_enc = {i+u'\u309A': j for i,j in pa_dict.items()}

		if u'\u3099' in lookuplist[0]:
	
			def convert_BA(i):
			    j = i.group(0)
			    if j in ba_dict_enc:
			        return ba_dict_enc.get(j)
			   

			lookuplist[0] = re.sub(r'''(.\u3099)''', convert_BA, lookuplist[0])

		if u'\u309A' in lookuplist[0]:
	
			def convert_PA(i):
			    j = i.group(0)
			    if j in pa_dict_enc:
			        return pa_dict_enc.get(j)
			   

			lookuplist[0] = re.sub(r'''(.\u3099)''', convert_PA, lookuplist[0])

	if not original_input: #If no seperate value is given for "original_input", use the value for "lookuplist" (this helps preserve it for passing to our other functions)
		original_input = lookuplist[0]

	if not original_sentence:
		original_sentence = lookuplist[0]

	if lookuplist[0] != '': #If the lookuplist val is not an empty string
		straight_result = jpwordsearch(lookuplist, original_input, original_sentence) #1st try doing a straight word search

		if straight_result[0]: #If that gave a result,
			return straight_result

		else: #If a straight search didn't return anything,

			mode = tokenizer.Tokenizer.SplitMode.C
			parsed_sen = tokenizer_obj.tokenize(original_input, mode)

			word_list = [m.dictionary_form() for m in parsed_sen if '助' not in m.part_of_speech()[0] and m.dictionary_form() not in ['ない','する','いる']]
			print(f'Word list: {word_list}')

			if word_list[0] != original_input:
				word_list_lookups = [jpwordsearch(i, original_input, original_sentence)[0] for i in word_list if i]
				word_list_lookups = [i for i in word_list_lookups if i]
				return word_list_lookups

			else: #If that doesn't return anything new
				if lookuplist[0].endswith("と") or lookuplist[0].endswith("な"): #Check if it ends with "と" or "な"
					Gitaigo_unmake = jpwordsearch(lookuplist[0][0:-1], original_input, original_sentence ) #if it does, strip the last character and try again

					if Gitaigo_unmake[0].senses:
						return Gitaigo_unmake

				
				else: #If it doesn't end with a と, try adding one and see if you get a result
					Gitaigo_make = jpwordsearch([lookuplist[0]+"と"], original_input, original_sentence)
					if Gitaigo_make[0].senses:
						return Gitaigo_make

	return None, original_input, original_sentence

if __name__ == '__main__':
	test1 = jplookup('嚆矢')
	print(test1[0].senses)
	#test2 = jplookup('狙える')