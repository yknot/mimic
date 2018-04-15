import sys
import pickle
import pandas as pd
from scipy.stats import truncnorm


def categorical(col):
    """convert a categorical column to continuous"""
    # get categories
    categories = (col.value_counts() / len(col)).sort_values(ascending=False)
    # get distributions to pull from
    distributions = {}
    limits = {}
    a = 0
    for cat, val in categories.iteritems():
        b = a + val
        mu, sigma = (a + b) / 2, (b - a) / 6
        distributions[cat] = truncnorm((a - mu) / sigma,
                                       (b - mu) / sigma,
                                       mu, sigma)
        limits[b] = cat
        a = b

    # sample from the distributions and return that value
    return col.apply(lambda x: distributions[x].rvs()), limits


def numeric(col):
    """normalize a numeric column"""
    return ((col - min(col)) / (max(col) - min(col))), min(col), max(col)


# create decoder function
def decode(x, limits):
    for k, v in limits.items():
        if x < k:
            return v


# read in data with column names
df = pd.read_csv(sys.argv[1])
df = df.dropna()

# loop through every column
limits = {}
min_max = {}
for c in df.columns:
    if df[c].dtype.char == 'O' or df[c].dtype.char == 'l':
        df[c], lim = categorical(df[c])
        limits[c] = lim
    elif df[c].dtype.char == 'd':
        df[c], min_res, max_res = numeric(df[c])
        min_max[c] = (min_res, max_res)

# save data and decoders
df.to_csv(sys.argv[:-4] + 'sdv.csv', index=False)
pickle.dump(limits, open('data/decoders_limits', 'wb'))
pickle.dump(min_max, open('data/decoders_min_max', 'wb'))
