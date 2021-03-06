import os

import pandas as pd

from parser_module_stamming import Parse_stem
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher_word2vec import Searcher
from timeit import default_timer as timer
from datetime import timedelta
from gensim.models import KeyedVectors

import utils

#word2vec

# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        if config == None:
            config = ConfigClass()
        self._config = config
        if config.toStem:
            self._parser = Parse_stem()
        else:
            self._parser = Parse()
        self._indexer = Indexer(config)
        self._model = None

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
        config = self._config
        indexer = self._indexer
        number_of_documents = 0

        if(config.getoneFile()):
            df = pd.read_parquet(fn, engine="pyarrow")
            documents_list = df.values.tolist()
            # Iterate over every document in the file
            for idx, document in enumerate(documents_list):
                # parse the document
                parsed_document = self._parser.parse_doc(document)
                number_of_documents += 1
                # index the document data
                self._indexer.add_new_doc(parsed_document)
            self._indexer.calculationSummerize()
        else:
            r = ReadFile(corpus_path=config.get__corpusPath())
            for root, dirs, files in os.walk(config.get__corpusPath(), topdown=True):
                for name in files:
                    ext = name.split('.')[-1]
                    if ext == 'parquet':
                        documents_list = r.read_folder(root, file_name=name)
                        # Iterate over every document in the file
                        for idx, document in enumerate(documents_list):
                            # parse the document
                            parsed_document = self._parser.parse_doc(document)
                            number_of_documents += 1
                            # index the document data
                            indexer.add_new_doc(parsed_document)
                        # indexer.update_posting_files()
                        # indexer.reset_cach()

        self._indexer.save_index('inverted_idx')
        print('Finished parsing and indexing.')

    # def get_full_text(self, d_id):
    #     return  self._indexer.documents_data[d_id][4]
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):#TODO implement
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        self._model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
        # self._model = KeyedVectors.load_word2vec_format(self._config.google_news_vectors_negative300_path, binary=True)


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
        if self._indexer.inverted_idx == None:
            print("can't run query without inverted index been loaded")
            return
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        return searcher.search(query)

    def main(self, queries = None, num_docs_to_retrieve= None):
        config = self._config
        # config.set_corpusPath(corpus_path)
        # config.set_savedFileMainFolder(output_path)
        # config.set_toStem(stemming)
        self.load_precomputed_model()
        vectorModel = self._model
        start = timer()
        print("----started parsing and indexer----")
        self.build_index_from_parquet('data/benchmark_data_train.snappy.parquet')
        end = timer()
        print("Process ends..")
        # print(timedelta(seconds=end - start))

        if num_docs_to_retrieve == None:
            num_docs_to_retrieve = 2000
        inverted_index = self.load_index('inverted_idx')
        if queries == None: #for end users use
            user_query = input("Please enter a query")
            user_num = int(input("How many tweets you want to get (maximum)?"))
            res = self.search(user_query)
            print("here are the links to the tweets related to use query")
            for x in range(user_num):
                try:
                    tweeter_start_link = 'https://twitter.com/IsraelHayomHeb/status/'
                    tweet_id = (res[1][x])
                    print(tweeter_start_link+tweet_id)

                except:
                    pass #less than number of doc to retrive found
        else:#for engenier use
            import csv
            with open('queries_output.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["query", "tweet"])
                if not isinstance(queries, list):
                    try:
                        f = open(queries, "r+", encoding='utf-8')
                        # queries = f.read()
                        queries = f.readlines()
                        f.close()
                    except Exception:
                        raise
                        print("fail in reading queries file")
                        # see numbers for the document file
                    i = 0
                    for querie in queries:
                        print("querie number" + str(i))
                        print(querie)
                        i += 1
                        res = self.search(querie)
                        for s in range(num_docs_to_retrieve):
                            try:
                                writer.writerow([i,res[1][s]])
                            except:
                                pass  # less than number of doc to retrive found
                        # for doc in res[1]:
                        #     #print('Tweet id: {}, Score: {}'.format(doc_tuple[1], doc_tuple[0]))
                        #     writer.writerow([i, doc])


