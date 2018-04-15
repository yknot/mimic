import sys
import pickle
import pandas as pd
import numpy as np


def undo_categorical(col, lim):
    """convert a categorical column to continuous"""

    def decode(x, limits):
        for k, v in limits.items():
            if x < k:
                return v

    return col.apply(lambda x: decode(x, lim))


def undo_numeric(col, min_col, max_col):
    """normalize a numeric column"""
    return ((max_col - min_col) * col) + min_col


limits = pickle.load(open('data/decoders_limits', 'rb'))
min_max = pickle.load(open('data/decoders_min_max', 'rb'))
test_data = pd.read_csv(sys.argv[2])


# real decode
gen_data = pd.DataFrame(np.load(sys.argv[1]),
                        columns=test_data.columns)

for c in gen_data.columns:
    if c in limits:
        gen_data[c] = undo_categorical(gen_data[c], limits[c])
    else:
        gen_data[c] = undo_numeric(gen_data[c], *min_max[c])

# save result
gen_data.to_csv(sys.argv[1][:-4] + '.csv', index=False)
