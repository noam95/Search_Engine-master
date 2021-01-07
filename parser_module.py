from nltk import regexp_tokenize, TweetTokenizer, RegexpTokenizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import regexp_tokenize

from configuration import ConfigClass
from document import Document
import re
from urllib.parse import urlparse
from nltk import PorterStemmer

class Parse:

    def __init__(self):
        self.stop_words = [] #TODO stopwords.words('english')
        self.additional_stop_words = ['RT', 'tweet', 'www', 'http', 'https','WWW']
        self.corona_list = ['corona', 'coronavirus', 'covid','covid19', 'covid 19', 'corona virus', 'virus corona', 'corona_virus', 'virus_corona']

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
                        if w[0].isupper():
                            w = w.upper()
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
                        continue #TODO:advance
                        var = 'coronavirus'
                    else:
                        var = self.cut_end_begining(var)
                    tokenized_text_fixed.append(var)
                elif self.is_number(var):
                    tokenized_text_fixed.append(var)

            return tokenized_text_fixed
        except Exception:
            raise
            #print("fail in parser main function")

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-presenting the tweet.
        :return: Document object with corresponding fields.
        """
        try:
            tweet_id = doc_as_list[0]
            tweet_date = doc_as_list[1]
            full_text = doc_as_list[2]
            url = doc_as_list[3]
            indices = doc_as_list[4]
            retweet_text = doc_as_list[5]
            retweet_url = doc_as_list[6]
            retweet_indices = doc_as_list[7]
            quote_text = doc_as_list[8]
            quote_url = doc_as_list[9]
            term_dict = {}
            if url != '{}':#there is an url
                split_url = url.split('"')
                if split_url[2] in full_text:
                    cleanindices = indices.replace('[', '')
                    cleanindices2 = cleanindices.replace(']', '')
                    cleanindices3 = cleanindices2.split(',')
                    full_text = full_text[:int(cleanindices3[0])] #cutting the short url from the text
                    full_text += ' '
                    full_text += split_url[3]
                else:
                    full_text += ' '
                    full_text += split_url[3]
            else:
                pass
            tokenized_text = self.parse_sentence(full_text)
            tokenized_text.append(self.parse_date(tweet_date)[0])

            doc_length = len(tokenized_text)  # after text operations.

            for term in tokenized_text:
                if term == '':
                    continue
                if not term.isascii():
                    continue
                if term not in term_dict.keys():
                    term_dict[term] = 1
                else:
                    term_dict[term] += 1

            document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                                quote_url, term_dict, doc_length)
            return document
        except Exception:
            pass
            #print("failed in parsing doc")

    def cut_end_begining(self, w):
        while len(w) != 0:  # cut the end
            if not (w[-1].isalpha()) and not (self.is_number(w[-1])) and (w[-1] not in ["#", "%", "@"]):  # , "$"
                if len(w) > 1:
                    w = w[:-1]
                else:
                    flag = True
                    break
            else:
                break
        while len(w) != 0:  # cut the beggining
            if not (w[0].isalpha()) and not (self.is_number(w[0])) and (w[0] not in ["#", "@"]):  # , "$"  "%"
                if len(w) > 1:
                    w = w[1:]
                elif len(w) == 1:
                    w = ''
                    break
                else:
                    flag = True
                    break
            else:
                break
        return w

    def parse_date(self,tweet_date):
        try:
            date_split = tweet_date.split(" ")
            token_list = []
            token = ""
            token += date_split[2]
            token += " "
            token += date_split[1]
            token += " "
            token += date_split[5]
            token_list.append(token)
            return token_list
        except Exception:
            pass
            #print("fail in parsing date")

    def NumbersHandle(self, w, i, TokenizedList):
        try:
            l = len(TokenizedList) - 1
            if i != l:
                t = TokenizedList[i + 1]
                if (t == "%" or t == "percent" or t== "percentage"):
                    return [w+"%",i+1]
                if t == "Billion" or t == "Billions" or t == "billion" or t == "billions":
                    return [w + "B", i + 1]
                if t == "Million" or t == "Millions" or t == "million" or t == "millions":
                    return [w+"M", i+1]
                if t == "Thousand" or t == "Thousands" or t == "thousand" or t == "thousands":
                    return [w+"K", i+1]
                if len(t) >0 and t.find('/') != -1:
                    return [w + " " + t, i+1]
            if len(w) >= 4:
                word = self.ThousandMillionHandle(w, i, TokenizedList)
                return [word, i]
            return [w, i]
        except Exception:
            pass
            #print("fail in Number Handler")

    def ThousandMillionHandle(self, w, i, TokenizedList):
        try:
            if float(w) > 999:
                number = self.cleanNumber(w)
                length = len(number)
                if length > 9:#Billions
                    number = number[:length-9] + "." + number[(length-9):(length-6)] + "B"
                    if number[-2] == "0":
                        return number[:-2]+"B"
                    return number
                if 9 >= length and length > 6:#Millions
                    number = number[:length-6] + "." + number[(length-6):(length-3)] + "M"
                    if number[-2] == "0":
                        number = number[:-2]+"M"
                        if number[-2] == "0":
                            number = number[:-2] + "M"
                            if number[-2] == "0":
                                number = number[:-3] + "M"
                    return number
                if length > 3 and length <= 6:#thousands
                    number = number[:length-3] + "." + number[length-3:] + "K"
                    if number[-2] == "0":
                        number= number[:-2]+"K"
                        if number[-2] == "0":
                            number = number[:-2] +"K"
                            if number[-2] == "0":
                                number = number[:-3] + "K"
                    return number
            else:
                return w[:7]
            return w
        except:
            pass
            #print("fail in handle ThousandMillionHandle")

    def cleanNumber(self, w):
        try:
            number = ""
            for i in w:
                if i == ",":
                    continue
                if i == ".":
                    break
                if self.is_number(i):
                    number += i
            return number
        except Exception:
            pass
            #print("fail in cleanNumber")

    def UrlHandle(self, word):
        return []
        try:
            to_return = []
            url_split = urlparse(word)
            temp_str = ''
            for l in url_split[0]:
                temp_str += l
            to_return.append(temp_str)
            temp_str = ''
            for l in url_split[1]:
                temp_str += l
            if 'www' in temp_str:
                to_return.append(temp_str[:3])
                to_return.append(temp_str[4:])
            else:
                to_return.append(temp_str)
            temp_str = ''
            for l in url_split[2]:
                if not (33 <= ord(l) <= 47 or 58 <= ord(l) <= 64 or 91 <= ord(l) <= 96
                        or 123 <= ord(l) <= 126): #not unneccry char
                    temp_str += l
                else:
                    if temp_str != '':
                        if temp_str not in self.stop_words:
                            to_return.append(temp_str)
                            temp_str = ''
                        else:
                            temp_str = ''
            for i in range(3, 6):
                for l in url_split[i]:
                    if not (33 <= ord(l) <= 47 or 58 <= ord(l) <= 64 or 91 <= ord(l) <= 96
                            or 123 <= ord(l) <= 126):  # not unneccry char
                        temp_str += l
                    else:
                        if temp_str != '':
                            if temp_str not in self.stop_words:
                                to_return.append(temp_str)
                                temp_str = ''
                            else:
                                temp_str = ''
            to_return.append(temp_str)
            return to_return
        except Exception:
            pass
            #print("fail in URL")

    def is_number(self, w):
        try:
            float(w)
            return True
        except ValueError:
            return False

    def HashtagsHandle(self, word):
        try:
            toReturn = []
            capital_str = ''
            #full_str = ''
            if len(word) <= 1:
                toReturn.append(word)
                return toReturn
            temp_str = word[1]
            full_str = word[1].lower()
            i = 2
            flag = True
            while i < len(word):
                l = word[i]
                #full_str += l
                flag = True
                if 33 <= ord(l) <= 47 or 58 <= ord(l) <= 64 \
                        or 91 <= ord(l) <= 96 or 123 <= ord(l) <= 126:  # special chars
                    toReturn.append(temp_str.lower())
                    temp_str = ''
                elif 65 <= ord(l) <= 90:  # capital letter
                    if len(temp_str) > 1:
                        toReturn.append(temp_str.lower())
                        # full_str += l.lower()
                        temp_str = ''

                    full_str += l.lower()
                    capital_str += temp_str
                    capital_str += l
                    temp_str += l
                    j = i + 1
                    while j < len(word):
                        w2 = word[j]
                        if w2.isupper():
                            capital_str += w2
                            full_str += w2.lower()
                            temp_str+=w2 #test COVID19
                            j += 1
                        else:
                            i = j
                            capital_str = ''
                            temp_str+=w2 #test COVID19
                            full_str += w2
                            break
                    if len(capital_str) > 1:
                        toReturn.append(capital_str)
                        capital_str = ''
                        i = j
                    # if len(capital_str) == len(word)-i:
                    #     toReturn.append(capital_str)
                    #     capital_str = ''
                    #     i=j
                else:  # regular letter
                    if len(capital_str) > 1:
                        toReturn.append(capital_str)
                    capital_str = ''
                    temp_str += l
                    full_str += l
                i += 1
            if len(temp_str) > 1:
                toReturn.append(temp_str.lower())
            # if full_str != temp_str:
            #     toReturn.append(full_str)
            toReturn.append('#'+full_str)

            return toReturn
        except Exception:
            pass
            #print("fail in HashTag #")
