import utils
import math

class Ranker:


    def rank_relevant_doc(relevant_doc, qurey, config):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        if config.toStem:
            documents_data = utils.load_obj("documents_stem")#keys- document id. values- [max freq term, number of difrent words, number of words]
            inverted_index = utils.load_obj("inverted_idx_stem")#keys-terms. values- [line number in post file,number of documents appears in,total appearance in corpus]
        else:
            documents_data = utils.load_obj("documents")#keys- document id. values- [max freq term, number of difrent words, number of words]
            inverted_index = utils.load_obj("inverted_idx")
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
        return cosine_list

    def retrieve_top_k(sorted_relevant_doc, k=1):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]
