import csv
import traceback
from _csv import reader
from csv import DictReader

import pandas
import pandas as pd

# df = pd.DataFrame(
#     {'query': [1, 1, 2, 2, 3], 'tweet': [12345, 12346, 12347, 12348, 12349],'label': [1, 0, 1, 1, 0]})
#
# # df = pd.DataFrame(
# #       {'query': [1, 1, 2, 2, 3, 4, 4, 4, 5, 6, 6], 'Tweet_id': [12345, 12346, 12347, 12348, 12349, 12350, 12351, 12352, 12352, 12353, 12346],
# #        'label': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1]})
# test_number = 0
# results = []


# precision(df, True, 1) == 0.5
# precision(df, False, None) == 0.5
def precision(df, single=False, query_number=None):
    """
        This function will calculate the precision of a given query or of the entire DataFrame
        :param df: DataFrame: Contains query numbers, tweet ids, and label
        :param single: Boolean: True/False that tell if the function will run on a single query or the entire df
        :param query_number: Integer/None that tell on what query_number to evaluate precision or None for the entire DataFrame
        :return: Double - The precision
       """


    num_of_querys = df.count()
    data_counter = {}  # keys- query_num, values- [retrive,relevant]
    for index, row in df.iterrows():
        qury_num = row['query']
        if qury_num in data_counter.keys():
            retrive_counter = data_counter[qury_num][1] + int(row['label'])
            data_counter[qury_num] = [data_counter[qury_num][0] + 1, retrive_counter]
        else:
            retrive_counter = row['label']
            data_counter[qury_num] = [1, retrive_counter]
    # calculate non single precision
    if not single:
        num_of_querys = 0
        sum_precision = 0
        for query in data_counter.keys():
            num_of_relevant_doc = data_counter[query][1]
            num_of_doc = data_counter[query][0]
            if num_of_doc == 0:
                continue
            precision = num_of_relevant_doc / num_of_doc
            sum_precision = sum_precision + precision
            num_of_querys += 1
        if num_of_querys == 0:
            return 0
        return sum_precision / num_of_querys
    else:  # if single
        num_of_relevant_doc = data_counter[query_number][1]
        num_of_doc = data_counter[query_number][0]
        if num_of_doc == 0:
            return 0
        precision = num_of_relevant_doc / num_of_doc
        return precision


# recall(df, {1:2}, True) == 0.5
# recall(df, {1:2, 2:3, 3:1}, False) == 0.388

def recall(df, num_of_relevant):
    """
        This function will calculate the recall of a specific query or of the entire DataFrame
        :param df: DataFrame: Contains query numbers, tweet ids, and label
        :param num_of_relevant: Dictionary: number of relevant tweets for each query number. keys are the query number and values are the number of relevant.
        :return: Double - The recall
    """

    #num of relevant docs that retrived \ num of tatol num of relevant.
    num_of_relevant_retrived = {}  #dictionary which the keys are query numbers and values are the relevant docs that retrived.
    recall = 0
    for index, row in df.iterrows():
        if row['query'] in num_of_relevant and row['label'] == 1:
            if row['query'] in num_of_relevant_retrived:
                num_of_relevant_retrived[row['query']] += 1
            else:
                num_of_relevant_retrived[row['query']] = 1
    for query in num_of_relevant_retrived.keys():
        if num_of_relevant[query] == 0:
            continue
        recall += (num_of_relevant_retrived[query]/num_of_relevant[query])
    if num_of_relevant == 0:
        return None
    return float(recall/len(num_of_relevant))

# precision_at_n(df, 1, 2) == 0.5
# precision_at_n(df, 3, 1) == 0
def precision_at_n(df, query_number=1, n=5):
    """
            This function will calculate the precision of the first n files in a given query.
            :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
            :param query_number: Integer/None that tell on what query_number to evaluate precision or None for the entire DataFrame
            :param n: Total document to splice from the df
            :return: Double: The precision of those n documents
        """

    num_of_querys = df.count()
    data_counter = {}  # keys- query_num, values- [retrive,relevant]
    for index, row in df.iterrows():
        qury_num = row['query']
        if qury_num == query_number:
            if qury_num in data_counter.keys():
                doc_counter = data_counter[qury_num][0]
                if doc_counter < n:
                    retrive_counter = data_counter[qury_num][1] + row['label']
                    data_counter[qury_num] = [doc_counter + 1, retrive_counter]
            else:
                retrive_counter = row['label']
                data_counter[qury_num] = [1, retrive_counter]
    if n != 0:
        num_of_relevant_doc = data_counter[query_number][1]
        num_of_doc = data_counter[query_number][0]
        if num_of_doc == 0:
            return 0
        precision = num_of_relevant_doc / num_of_doc
        return precision
    return 0


# map(df) == 2/3
def map(df):
    """
        This function will calculate the mean precision of all the df.
        :param df: DataFrame: Contains query numbers, tweet ids, and label
        :return: Double: the average precision of the df
    """
    quries_set = pd.unique(df['query'])
    map_value = 0
    for q in quries_set:
        relevant = 0
        # doc_num = 0
        precision_value = 0
        k_row = 0
        for index, row in df.iterrows():
            if row['query'] == q:
                k_row += 1
                if row['label'] == 1:
                    relevant += 1
                    precision_value += precision_at_n(df, q, k_row)
            else:
                continue
        if relevant != 0:
            if relevant == 0:
                continue
            map_value += float(precision_value / relevant)
    if len(quries_set) == 0:
        return 0
    return map_value / len(quries_set)

def createDF(retunedDoc, benchMark):#return df with lable from benchmark and number of relevant dict

    colnames_benchmark = ['query', 'tweet', 'y_true']
    colnames_engineOutpot = ['query','tweet','Rank']
    benchMark_data = pandas.read_csv(benchMark, names=colnames_benchmark)
    engine_output_date = pandas.read_csv(retunedDoc, names=colnames_engineOutpot)

    with open(benchMark, 'r') as read_obj:
        r = csv.reader(read_obj)
        lables_dict = {(row[0],row[1]): row[2] for row in r} #Key=(query_num, tweet_id), val= lable
    with open(retunedDoc, 'r') as read_engine_data:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_engine_data)
        # Pass reader object to list() to get a list of lists
        engine_data = list(csv_reader)
    data_frame = []
    nuber_of_rellevan_dict = {} #key = queryNum , value = Number of relevan
    for line in engine_data:
        try:
            data_frame.append([line[0], line[1], lables_dict[line[0],line[1]]])
        except:
            data_frame.append([line[0], line[1], 0.0] )
    query_list = []
    tweet_list = []
    label_list = []
    for line in data_frame:
        if line[0] == 'query':
            continue
        query_list.append(int(line[0]))
        tweet_list.append(int(line[1]))
        label_list.append(int(float(line[2])))
        if (line[2] == '1.0'):
            try:
                nuber_of_rellevan_dict[line[0]] = nuber_of_rellevan_dict[line[0]] +1
            except:
                nuber_of_rellevan_dict[line[0]] = 1

    df = pd.DataFrame(
        {'query':query_list, 'tweet': tweet_list, 'label': label_list})

    return df, nuber_of_rellevan_dict

def calculate_engine_officiant(engine_output, benchmark):
    df, relevant_dict = createDF(engine_output,benchmark)
    pression_val = precision(df, query_number=1)
    recall_val = recall(df,relevant_dict)
    map_val = map(df)
    with open('engine_rate.csv', 'w') as read_obj:
        r = csv.writer(read_obj)
        r.writerow(['pressision', 'recall', 'map'])
        r.writerow([pression_val,recall_val,'map_val'])
        r.writerow(['queriy','tweet', 'lable'])
        r.writerows(df.values.tolist())
    return pression_val, recall_val, map_val

#calculate_engine_officiant('queries_output.csv','C:/Users/User/PycharmProjects/Search_Engine_AN/data/benchmark_lbls_train.csv')
