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

    # create decoder function
    def decode(x):
        for k, v in limits.items():
            if x < k:
                return v

    # sample from the distributions and return that value
    return col.apply(lambda x: distributions[x].rvs()), decode


def numeric(col):
    """normalize a numeric column"""
    return ((col - min(col)) / (max(col) - min(col)))


# read in data with column names
df = pd.read_csv('data/final_df.csv')
df = df.dropna()

# test
new_col, decode = categorical(df.ICU)
assert ((new_col.apply(decode) == df.ICU).all())

decoders = {}
for c in df.columns:
    if df[c].dtype.char == 'O' or df[c].dtype.char == 'l':
        new_col, decode = categorical(df[c])
        df[c] = new_col
        decoders[c] = decode
    elif df[c].dtype.char == 'd':
        df[c] = numeric(df[c])


df.to_csv('data/final_df_sdv.csv', index=False)
