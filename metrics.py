import csv
from _csv import reader

import pandas
import pandas as pd
from functools import reduce


# precision(df, True, 1) == 0.5
# precision(df, False, None) == 0.5
def precision(df, single=False, query_number=None):
    """
        This function will calculate the precision of a given query or of the entire DataFrame
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :param single: Boolean: True/False that tell if the function will run on a single query or the entire df
        :param query_number: Integer/None that tell on what query_number to evaluate precision or None for the entire DataFrame
        :return: Double - The precision
    """
    if single:
        df2 = df[df['query'] == query_number]
        return df2['y_true'].mean()
    else:
        return df.groupby('query')['y_true'].mean().mean()

def recall_single(df, num_of_relevant, query_number):
    """
        This function will calculate the recall of a specific query or of the entire DataFrame
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :param num_of_relevant: Integer: number of relevant tweets
        :param query_number: Integer/None that tell on what query_number to evaluate precision or None for the entire DataFrame
        :return: Double - The recall
    """
    df2 = df[df['query'] == query_number]
    return df2['y_true'].sum() / num_of_relevant

# recall(df, {1:2}, True) == 0.5
# recall(df, {1:2, 2:3, 3:1}, False) == 0.388
def recall(df, num_of_relevant):
    """
        This function will calculate the recall of a specific query or of the entire DataFrame
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :param num_of_relevant: Dictionary: number of relevant tweets for each query number. keys are the query number and values are the number of relevant.
        :return: Double - The recall
    """
    rec = 0
    for query_number in num_of_relevant.keys():
        relevant = num_of_relevant.get(query_number)
        rec += recall_single(df, relevant, query_number)
    return rec / len(num_of_relevant)

# precision_at_n(df, 1, 2) == 0.5
# precision_at_n(df, 3, 1) == 0
def precision_at_n(df, query_number=1, n=5):
    """
        This function will calculate the precision of the first n files in a given query.
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :param query_number: Integer that tell on what query_number to evaluate precision
        :param n: Total document to splice from the df
        :return: Double: The precision of those n documents
    """
    return precision(df[df['query'] == query_number][:n], True, query_number)

# map(df) == 2/3
def map(df):
    """
        This function will calculate the mean precision of all the df.
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :return: Double: the average precision of the df
    """
    acc = 0
    split_df = [pd.DataFrame(y).reset_index() for x, y in df.groupby('query', as_index=True)]
    indices = [sdf.index[sdf['y_true'] == 1].tolist() for sdf in split_df]
    for i, indexes in enumerate(indices):
        pres = [precision_at_n(split_df[i], i + 1, index + 1) for index in indexes]
        acc += reduce(lambda a, b: a + b, pres) / len(indexes) if len(pres) > 0 else 0
    return acc / len(split_df)

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

#calculate_engine_officiant('C:/Users/User/PycharmProjects/Search_Engine_AN/queries_output.csv','C:/Users/User/PycharmProjects/Search_Engine_AN/data/benchmark_lbls_train.csv')
