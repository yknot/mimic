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
    return ((col - min(col)) / (max(col) - min(col)))

# create decoder function


def decode(x, limits):
    for k, v in limits.items():
        if x < k:
            return v


# read in data with column names
df = pd.read_csv('data/final_df.csv')
df = df.dropna()
df = df.drop(['ADMITTIME', 'DISCHTIME'], axis=1)

# test
new_col, lim = categorical(df.ICU)
assert ((new_col.apply(lambda x: decode(x, lim)) == df.ICU).all())

limits = {}
for c in df.columns:
    if df[c].dtype.char == 'O' or df[c].dtype.char == 'l':
        new_col, lim = categorical(df[c])
        df[c] = new_col
        limits[c] = lim
    elif df[c].dtype.char == 'd':
        df[c] = numeric(df[c])

# save data and decoders
df.to_csv('data/final_df_sdv.csv', index=False)
pickle.dump(limits, open('data/decoders', 'wb'))
