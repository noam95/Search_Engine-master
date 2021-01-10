# DO NOT MODIFY CLASS NAME
import math
import pickle

import utils


class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.inverted_idx = {}#keys-terms. values- [(post file name, post file line),number of documents appears in,total appearance in corpus]
        self.postingDict = {} #keys-posting files names. values- lists of lines(lists) each line represent term
        self.header_posting_files = {} #keys-posting files name. values-line number of the next term
        self.documents_data = {} #keys- document id. values- [max freq term, number of difrent words, number of words, weight]
        self.config = config
        self.name_and_entity = {} #keys- name_and_entitys, values- data to addterm function
        self.name_of_files = {} #keys- term first letter 't', values- number

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        d_id = document.tweet_id
        #adding term to catch
        for term in document_dictionary.keys():
            number_times = document_dictionary[term]
            self.add_term(term,number_times,d_id)

        #adding information about the file
        dict_length = len(document_dictionary.keys())
        if dict_length > 0:
            sorted(document_dictionary.items(), key=lambda x: x[1])
            max_freq_term = list(document_dictionary.keys())[0]
            total_words = len(document.full_text.split(" "))
        else:
            max_freq_term = " "
            total_words =  len(document.full_text.split(" "))
        self.documents_data[d_id] = [max_freq_term,dict_length,total_words,0]

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        fn = fn.split(".")[0]
        try:
            stored_index = utils.load_obj(fn)
            self.inverted_index = stored_index[0]
            self.postingDict = stored_index[1]
            self.documents_data = stored_index[2]
        except:
            print("inverted index file not found. indexer.load_index")

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn, indexer=None):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        if indexer != None:
            utils.save_obj(indexer,fn)
        else:
            utils.save_obj((self.inverted_idx,self.postingDict,self.documents_data), fn)

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """

        return term in self.postingDict

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []

    def add_term(self, term, number_of_appears, document_id):
        '''add to main dict'''
        if term.isupper() and term.lower() in self.inverted_idx.keys():#if the term is upper and the dict contain's a lower version
            term = term.lower()
        if not term in self.inverted_idx.keys() and term.upper() in self.inverted_idx.keys():  # if there was no lower but was a upper term
            self.inverted_idx[term] = self.inverted_idx[term.upper()]  # change the term key
            self.inverted_idx.pop(term.upper())  # remove the upper key
        #adding term
        if term in self.inverted_idx.keys(): #if there was already a term
            post_file_line = self.inverted_idx[term][0][1]
            post_file_name = self.inverted_idx[term][0][0]
            data = (str(number_of_appears), document_id)
            self.add_term_to_cath_dict(post_file_name,post_file_line, data)
            self.inverted_idx[term][1] += 1
            self.inverted_idx[term][2] += number_of_appears

        else: #if this is the first appear of the term
            post_file_name = self.NewFileName(term)
            if " " in term: #this is name and entity
                if term in self.name_and_entity.keys():#not the first appear
                    #adding in first time menually
                    post_file_name = self.name_and_entity[term][0]
                    document_id = (self.name_and_entity[term][1])[1]
                    number_of_appears = (self.name_and_entity[term][1])[0]
                    if post_file_name in self.header_posting_files.keys():  # if there is already a post file
                        post_file_line = self.header_posting_files[post_file_name]  # post file line for the term
                        self.header_posting_files[post_file_name] += 1
                    else:  # if we need to creat a post file
                        self.header_posting_files[post_file_name] = 1
                        post_file_line = 0
                    self.inverted_idx[term] = [(post_file_name,post_file_line), 1,number_of_appears]
                    data = (str(number_of_appears), document_id)
                    self.add_term_to_cath_dict(post_file_name, post_file_line, data)
                    # adding second time by calling add term function
                    self.add_term(term,number_of_appears,document_id)
                    return
                else:#first time this term came
                    self.name_and_entity[term] = (post_file_name,(number_of_appears, document_id)) #data to be added if more than one tweet
                    return #not add the term in first time
            if post_file_name in self.header_posting_files.keys(): #if there is already a post file
                post_file_line = self.header_posting_files[post_file_name] #post file line for the term
                self.header_posting_files[post_file_name] +=1
            else:#if we need to creat a post file
                self.header_posting_files[post_file_name] = 1
                post_file_line = 0

            self.inverted_idx[term] = [(post_file_name,post_file_line),1,number_of_appears]
            data = (str(number_of_appears), document_id)
            self.add_term_to_cath_dict(post_file_name, post_file_line, data)

    def update_posting_files(self):#dict contains posting files list of terms data - keys: 'posting file name', data: new data to be added to posting file
        posting_files_dict = self.postingDict
        try:
            folder = self.config.get_outputPath()
        except:
            pass
            #print("fail in getting output forlder path")
        for terms_doc in posting_files_dict.keys(): #scaning all the posting files
            file_name = folder + terms_doc.lower() + ".p"
            new_data = posting_files_dict[terms_doc]  # new data to be added
            try:
                file = open(str(file_name), "rb")  # open a file if exist
                origin_lines = pickle.load(file) #old data to be mareged
                file.close()
                marged_post_file = []
                #scanning all the terms in the post file 'terms_doc_list'
                origin_file_len = len(origin_lines)
                index = 0
                while index < origin_file_len:
                    try:
                        marged_post_file.append(origin_lines[index] + new_data[index])
                        index +=1
                    except:
                        #print("fail in marging file" + file_name)
                        index +=1
                marged_post_file = marged_post_file + new_data[index:] #marging the additional terms added to the post file
                file = open(str(file_name), "wb")  # open a file
                pickle.dump(marged_post_file, file)
                file.close()
            except:
                try:
                    file = open(file_name, "wb")
                    pickle.dump(new_data, file)#new data
                    file.close()
                except:
                    pass
                    #print('fail in marge post file -' + terms_doc)

    def add_term_to_cath_dict(self, name_of_file, lineNumber, data):#data = [str(number_of_appears), document_id]
            try:
                if name_of_file in self.postingDict.keys(): #if there is already a posting file with this name
                    stored_data = self.postingDict[name_of_file]
                    if len(stored_data) <= lineNumber:#if there is no data for the term
                        stored_data.append([data])#open new line for the term
                    else:#if tere is already data for the spasific term
                        stored_data[lineNumber].append(data)#adding the data to the term line data
                else:#if there is no posting file yet
                    stored_data = [[data]]#put the data to be the first line data
                self.postingDict[name_of_file] = stored_data #update the cach data
            except:
                pass
                #"fail to add a term to the cath dict" + name_of_file

    def reset_cach(self):
        for post_file_lines in self.postingDict.keys():#for each
            for line_term in range(len(self.postingDict[post_file_lines])):
                self.postingDict[post_file_lines][line_term] = []

    def margelist(self, list1, list2):
        size_1 = len(list1)
        size_2 = len(list2)
        res = []
        i, j = 0, 0
        if size_1 ==1 or size_2==1:
            ls = list1+(list2)
            return ls
        while i < size_1 and j < size_2:
            if size_1 < size_2:
                if list1[i][0] <= list2[j][0]:
                    res.append(list1[i])
                    i += 1
                else:
                    res.append(list2[j])
                    j += 1
            else:
                if list1[i][0] < list2[j][0]:
                    res.append(list1[i])
                    i += 1
                else:
                    res.append(list2[j])
                    j += 1
        res = res + list1[i:] + list2[j:]
        return res

    def NewFileName(self, term):
        first_letter = term[0].lower()
        if first_letter not in self.name_of_files.keys():
            self.name_of_files[first_letter] = 1
        number_to_add = self.name_of_files[first_letter]
        if number_to_add == 29:
            number_to_add = 0
        self.name_of_files[first_letter] = number_to_add+1
        return first_letter + str(number_to_add)

    def calculationSummerize(self):
        corpus_len = len(self.documents_data.keys())
        self.config.set_cut_by(corpus_len)
        for term in self.inverted_idx.keys():
            post_file_name = self.inverted_idx[term][0][0]
            post_file_line = self.inverted_idx[term][0][1]
            df = self.inverted_idx[term][1] #number of ducuments appears in
            idf = math.log((corpus_len/df),10)
            for terminDoc in self.postingDict[post_file_name][post_file_line]:
                tf = (int(terminDoc[0])) / self.documents_data[terminDoc[1]][2] #number of appear /number of word in doc
                self.documents_data[terminDoc[1]][3] += tf*idf



