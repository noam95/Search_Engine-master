from datetime import timedelta

from timeit import default_timer as timer

from ranker_tf_idf import Ranker
import utils


# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model
    # parameter allows you to pass in a precomputed model that is already in
    # memory for the searcher to use such as LSI, LDA, Word2vec models.
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._renker = Ranker()
        #self._ranker = indexer.config.getRanker #TODO
        self._model = model

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
        p = self._parser
        start_qury = timer()
        query_as_list = p.parse_sentence(query)  # returnes a list of words
        advance_query = {}  # key- term. value - tf of the term in qurey
        start_searcher = timer()
        relevant_docs = self._relevant_docs_from_posting(query_as_list)

        end_searcher = timer()
        print(str(timedelta(seconds=end_searcher - start_searcher)) + "searcher time")
        for term in query_as_list:
            if term in relevant_docs.keys():
                advance_query[term] = query_as_list.count(term) / len(query_as_list)
            elif term.lower() in relevant_docs.keys():
                advance_query[term.lower()] = query_as_list.count(term) / len(query_as_list)
        relevant_doc_dict = self.get_relevant_doc_dict(relevant_docs)  # key= doc_id, value= (num_of_terms appears_in_doc from qury, [(terms,num_of_term_appears)])
        relevant_doc_dict = sorted(relevant_doc_dict.items(), key=lambda item: item[1][0], reverse=True)
        relevant_doc_dict = dict(relevant_doc_dict[0:2000]) if len(relevant_doc_dict) > 2000 else dict(relevant_doc_dict)
        # relevant_doc_dict = sorted(relevant_doc_dict.keys(), key=lambda x:x[0],reverse=True)
        start_renking = timer()
        if self._model != None:
            ranked_docs = self._renker.rank_relevant_docs(relevant_doc_dict, advance_query,self._indexer,  self._model)
        else:
            ranked_docs = self._renker.rank_relevant_docs(relevant_doc_dict, advance_query,self._indexer)
        end_qury = timer()
        print(str(timedelta(seconds=end_qury - start_renking)) + "ranking time")
        print(str(timedelta(seconds=end_qury - start_qury)) + "qury time")

        return len(relevant_docs) , ranked_docs
        # query_as_list = self._parser.parse_sentence(query)
        #
        # relevant_docs = self._relevant_docs_from_posting(query_as_list)
        # n_relevant = len(relevant_docs)
        # ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        # return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implementation of this function
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        relevant_docs = {}
        for term in query_as_list:
            posting_list = self._indexer.get_term_posting_list(term)
            for doc_id, tf in posting_list:
                df = relevant_docs.get(doc_id, 0)
                relevant_docs[doc_id] = df + 1
        return relevant_docs

    def get_relevant_doc_dict(self, relevant_docs):
        docs_dict = {}# key= doc_id, value= (num_of_terms appears_in_doc from qury, [(terms,num_of_term_appears)])
        #relevant_docs = dict- key=term, value= [(num_of_term_appears, dic_id),(num_of_term_appears, dic_id)]
        for term in relevant_docs.keys():
            for doc_ditails in relevant_docs[term]:
                doc_id = doc_ditails[1]
                if doc_id in docs_dict.keys():
                    flag = False
                    #clean double docs in corpus
                    for term_in_doc in docs_dict[doc_id][1]:
                        if term_in_doc[0] == term:
                            flag = True
                    #not same term in same doc
                    if not flag:
                        sum_terms = docs_dict[doc_id][0] + 1
                        #details = docs_dict[doc_id]
                        docs_dict[doc_id] = (sum_terms, docs_dict[doc_id][1] + [(term, doc_ditails[0])])
                        #details1= docs_dict[doc_id]
                else:
                    docs_dict[doc_id] = (1, [(term, doc_ditails[0])])
        return docs_dict
