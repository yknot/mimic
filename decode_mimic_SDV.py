import pickle
import pandas as pd
import numpy as np

TEST = True


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
test_data = pd.read_csv('data/final_df_sdv.csv')


if TEST:
    df = pd.read_csv('data/final_df.csv')
    df = df.dropna()
    df = df.reset_index()
    df = df.drop(['ADMITTIME', 'DISCHTIME', 'index'], axis=1)

    for c in test_data.columns:
        if c in limits:
            test_data[c] = undo_categorical(test_data[c], limits[c])
        else:
            test_data[c] = undo_numeric(test_data[c], *min_max[c])

    # assert data frames are equal (does all close)
    pd.util.testing.assert_frame_equal(test_data, df)

else:
    # real decode
    gen_data = pd.DataFrame(np.load('data/gen_df_sdv.npy'),
                            columns=test_data.columns)

    for c in gen_data.columns:
        if c in limits:
            gen_data[c] = undo_categorical(gen_data[c], limits[c])
        else:
            gen_data[c] = undo_numeric(gen_data[c], *min_max[c])

    # save result
    gen_data.to_csv('data/gen_df.csv', index=False)
