# you can change whatever you want in this module, just make sure it doesn't 
# break the searcher module
import math
from datetime import timedelta

from timeit import default_timer as timer
from numpy.dual import norm
import numpy

import utils


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
        # key= doc_id, value= (num_of_terms appears_in_doc from qury, [(terms,num_of_term_appears)])
        # print("start ranking")
        start_rank = timer()
        dict_doc = {}  # key - doc_id . value - sigma (tf*idf*vector_term)

        inverted_index = indexer.inverted_idx#keys-terms. values- [line number in post file,number of documents appears in,total appearance in corpus]
        documents_data = indexer.documents_data#keys- document id. values- [max freq term, number of difrent words, number of words]
        temp_list = []
        idf_dict = {}  # key= term, value= idf
        vector_query = numpy.zeros(300)
        dict_vector_model = {}  # key = term . value- vector represantion from model
        for term in qurey:
            if term in model_vector.vocab:
                term_vector = model_vector.wv.get_vector(term)
            else:  # not exist in the model
                term_vector = numpy.zeros(300)
            dict_vector_model[term] = term_vector  # keeping the vector of the term
            tf_q = qurey[term]
            # idf_query
            df_term = inverted_index[term][1]
            total_docs = len(documents_data.keys())
            idf_term = math.log((total_docs / df_term), 2)
            idf_dict[term] = idf_term
            tf_idf_q = tf_q * idf_term
            result = tf_idf_q * term_vector
            vector_query += result

        # calculate the vector of current query

        start_calculating_vectors = timer()
        for doc_id in relevant_doc.keys():
            for term in relevant_doc[doc_id][
                1]:  # key= doc_id, value= (num_of_terms_in_qury, [(term,num_of_term_appears)])
                term_name = term[0]
                tf_term = int(term[1]) / documents_data[doc_id][2]
                idf_term = float(idf_dict[term_name])
                tf_idf = tf_term * idf_term
                tf_idf_vector = tf_idf * dict_vector_model[term_name]
                if doc_id in dict_doc.keys():
                    dict_doc[doc_id] += tf_idf_vector
                else:
                    new_vec = numpy.zeros(300)
                    dict_doc[doc_id] = new_vec
                    dict_doc[doc_id] += tf_idf_vector
        end_calculating_vectors = timer()
        print(str(timedelta(seconds=end_calculating_vectors - start_calculating_vectors)) + "calculatingvectors time")
        rank_cosine = []
        temp_vec = []
        cosine_sim = numpy.zeros(300)
        start_calculate_cosim = timer()
        for doc in dict_doc.items():
            doc_as_vec = doc[1]
            if numpy.all(doc_as_vec) == 0 or numpy.all(vector_query) == 0:  # if the doc vector is zeros.
                rank_tuple = (0, doc[0], relevant_doc[doc[0]][0])
                rank_cosine.append(rank_tuple)
            else:
                dot = numpy.dot(vector_query, doc_as_vec)
                normlize = norm(vector_query) * norm(doc_as_vec)
                cosine_sim = dot / normlize
                rank_tuple = (cosine_sim, doc[0],
                              relevant_doc[doc[0]][0])  # cosine_similarity result, doc_id, number of common word withw
                rank_cosine.append(rank_tuple)
        end_calculate_cosim = timer()
        print(str(timedelta(seconds=end_calculate_cosim - start_calculate_cosim)) + "calculate_cosim time")
        # if rank_cosine == []:
        #     return rank_cosine
        rank_list_sorted = sorted(rank_cosine, reverse=True)
        end_rank = timer()
        # print("finished rank at {}".format(timedelta(seconds=end_rank-start_rank)))

        if k is not None:
            rank_list_sorted = rank_list_sorted[:k]
        return [d[1] for d in rank_list_sorted]#TODO debug here

