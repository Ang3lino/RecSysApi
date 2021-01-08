import heapq
import pandas as pd 
import numpy as np

from collections import defaultdict
from operator import itemgetter

from surprise import accuracy, dump, KNNBasic
from surprise import Dataset, Reader
from surprise.model_selection.split import train_test_split


def get_top_item_based(model, raw_uid, trainset, simsMatrix, k=10):
    testUserInnerID = trainset.to_inner_uid(raw_uid)

    # Get the top K items we rated
    testUserRatings = trainset.ur[testUserInnerID]  # list< pair< int, float>>: iids, ratings pairs
    kNeighbors = heapq.nlargest(k, testUserRatings, key=lambda t: t[1])

    # Get similar items to stuff we liked (weighted by rating)
    candidates = defaultdict(float)
    for itemID, rating in kNeighbors:
        similarityRow = simsMatrix[itemID]
        for innerID, score in enumerate(similarityRow):
            candidates[innerID] += score * (rating / 5.0)

    # stuff the user has already seen
    watched = set(itemID for itemID, rating in trainset.ur[testUserInnerID])

    # Get top-rated items from similar users:
    raw_iids = []
    pos = 0
    for itemID, ratingSum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
        if not itemID in watched:
            raw_iids.append(trainset.to_raw_iid(itemID))
            pos += 1
            if pos >= k:
                break
    return raw_iids

def get_top_n(predictions, n=10):
    """Return the top-N recommendation for each user from a set of predictions.

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.

    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    """

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

def train_test_from_df(df, cols, rating_scale=(1, 5), train_size=None, test_size=None):
    if train_size is None and test_size is None:
        raise ValueError('train size or test size required')
    # reader = Reader(rating_scale=(1, 5), line_format='item user rating')
    reader = Reader(rating_scale=(1, 5), )
    data = Dataset.load_from_df(df[cols], reader)
    if test_size:
        if test_size == 0:
            return data.build_full_trainset()
        return train_test_split(data, test_size=test_size)
    return train_test_split(data, train_size=train_size)

def serialize_algo(algo, fname):
    dump.dump(fname, algo=algo)

def load_algo(fname):
    _, loaded_algo = dump.load(fname)
    return load_algo

def get_rec_sys_resources():
    # get an instance of the algo
    sim_options = {'name': 'pearson', 'user_based': False}
    algo = KNNBasic(sim_options=sim_options)

    # load csv to build trainset, required to recommend
    cols = ['reviewerID', 'asin', 'overall']
    df_reviews = pd.read_csv('./model/software_reviews.csv')
    trainset, testset = train_test_from_df(df_reviews, cols, test_size=0.2)

    # train the model
    algo.fit(trainset)
    return algo, algo.compute_similarities(), trainset, testset