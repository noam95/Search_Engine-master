import utils
import math
from datetime import timedelta

from timeit import default_timer as timer
from numpy.dual import norm
import numpy

class Ranker:
    def __init__(self):
        pass

    @staticmethod
    def rank_relevant_docs(relevant_doc, qurey, indexer, model_vector = None, k=None):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        config = indexer.config
        inverted_index = indexer.inverted_idx#keys-terms. values- [line number in post file,number of documents appears in,total appearance in corpus]
        documents_data = indexer.documents_data#keys- document id. values- [max freq term, number of difrent words, number of words]
        idf_dict = {}
        docs_dict = {}
        tf_idf_q = 0
        #calculating tf-idf for query
        for term in qurey:
            df_term = inverted_index[term][1]
            total_docs = len(documents_data.keys())
            idf_term = math.log((total_docs / df_term), 2)
            idf_dict[term] = idf_term
            #tf term in query
            tf_term_q = qurey.count(term)
            tf_idf_q += tf_term_q * idf_term
        for doc_id in relevant_doc.keys():
            for term in relevant_doc[doc_id][
                1]:  # key= doc_id, value= (num_of_terms_in_qury, [(term,num_of_term_appears)])
                term_name = term[0]
                tf_term = int(term[1]) / documents_data[doc_id][2]
                idf_term = float(idf_dict[term_name])
                tf_idf = tf_term * idf_term
                docs_dict[doc_id] += tf_idf
        cosine_list = []
        for doc in docs_dict:
            inner_prodect = doc * tf_idf_q
            doc_len = documents_data[doc] #lenght of doc
            q_len = len(qurey)
            mul = doc_len * q_len
            cosine = float(inner_prodect/mul)
            tup = (cosine, doc)#similarity, doc_id
            cosine_list.append(tup)
        if k is not None:
            cosine_list = cosine_list[:k]
        return [d[1] for d in cosine_list]#TODO debug here
