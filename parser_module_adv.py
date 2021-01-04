from nltk import PorterStemmer
from nltk import RegexpTokenizer
from spellchecker import SpellChecker

from configuration import ConfigClass
from parser_module import Parse

class Parse_ADV(Parse):
    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        try:
            tokenized_text = []
            #url handle
            splited_url = []
            if 'http' in text:
                index = text.index('http')#TODO:check if gives index of hhtps
                #cut the URL
                url_part = text[index:]
                text = text[:index]
                splited_url_1 = self.UrlHandle(url_part)#including stop words
                for var in splited_url_1:
                    if var.lower() not in self.stop_words and var.lower() not in self.additional_stop_words:
                        splited_url.append(var)
            text = text.replace(",", "")
            tokenizer = RegexpTokenizer(r'\w-|\$[\d\.]+|\S+') #tokenize the original tweet
            rweetTokenize = tokenizer.tokenize(text)
            i = 0
            flag = True
            while i < len(rweetTokenize):
                flag = False
                w = rweetTokenize[i]
                w = self.cut_end_begining(w)
                if w == '':
                    i += 1
                    continue
                if "f*" in w or 'a/' in w:
                    x=2
                if w[0].isupper(): #names and entity
                    name_entity = ''
                    name_entity += w
                    j = i + 1
                    while j < len(rweetTokenize):
                        next_word = rweetTokenize[j]
                        if next_word[0].isupper():
                            name_entity += ' '
                            name_entity += next_word
                            j += 1
                        else:
                            break
                    if len(name_entity) > len(w):#recognized
                        tokenized_text.append(name_entity)
                    name_entity = ''
                    j = 0
                    flag = False
                if w.lower() not in self.stop_words and w not in self.additional_stop_words:
                    if w[0] == '#' and not(flag): #hashtags
                        list = self.HashtagsHandle(w)
                        tokenized_text = tokenized_text + (self.HashtagsHandle(w))
                        flag = True
                    if w[0] == '@' and not(flag): #tags
                        tokenized_text.append(w)
                        flag = True
                    number = self.is_number(w)
                    if number and not(flag):#start with int
                        ans = self.NumbersHandle(w, i, rweetTokenize)
                        tokenized_text.append(ans[0])
                        i = ans[1]
                        flag = True
                    # if not w.isascii() and not(flag):
                    #     i += 1
                    #     continue

                    if not(flag):
                        #start of upper case handle
                        sttemer = PorterStemmer()
                        if w[0].isupper():
                            w = sttemer.stem(w)
                            w = w.upper()
                        else:
                            w = sttemer.stem(w)
                        # else:#end of upper case handle
                        #     w = w.lower()
                        w = w.replace(".", " ")#handle mikrey katze
                        w = w.replace("-", " ")
                        w = w.replace("/", " ")
                        # w = w.replace("\'", " ")
                        # w = w.replace("|", "")
                        # w = w.replace("*", "")
                        # w = w.replace("?", "")
                        # w = w.replace('"', "")
                        last_split = w.split(" ")
                        tokenized_text = tokenized_text + last_split
                        flag = True
                i += 1
            tokenized_text = tokenized_text + splited_url
            tokenized_text_fixed = []
            for var in tokenized_text:#clean end and begining
                if len(var) > 1:#cut all the term size les than one exept numbers
                    if var.lower() in self.corona_list:#handle virus corona terms
                        var = 'coronavirus'
                        continue
                    else:
                        var = self.cut_end_begining(var)
                    tokenized_text_fixed.append(var)
                elif self.is_number(var):
                    var = self.numbers_to_int(var)
                    tokenized_text_fixed.append(var)
            return tokenized_text_fixed
        except Exception:
            raise
            #print("fail in parser main function")

    def numbers_to_int(self,num):
        numbers = ['one','two','three','for','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen', \
             'seventeen','eighteen','nineteen','twenteen']
        if num in numbers:
            num = numbers.index(num)
        return str(num)
