import pandas as pd
import json


def get_stays():
    """get patients older than 16, with first stay > 48 hours"""
    admissions = pd.read_csv('data/ADMISSIONS.csv')
    patients = pd.read_csv('data/PATIENTS.csv')
    merged = pd.merge(admissions, patients, on='SUBJECT_ID')

    # calculate age in years
    merged['AGE'] = ((pd.to_datetime(merged.ADMITTIME) -
                      pd.to_datetime(merged.DOB)) / 365.25).dt.days

    # filter out under 16, but keep negative wrapped values that mean >89
    merged_adult = merged[(merged.AGE >= 16) | (merged.AGE < 0)]

    # filter to first stay for each patient
    merged_a_first = merged_adult[merged_adult.ADMITTIME.groupby(
        merged_adult.SUBJECT_ID).apply(lambda x: x == x.min())]

    # filter to stays > 48 hour
    merged_a_f_long = merged_a_first[(pd.to_datetime(
        merged_a_first.DISCHTIME) -
        pd.to_datetime(merged_a_first.ADMITTIME)).dt.days > 2]

    return merged_a_f_long


def get_variable_codes():
    """get the codes for the variables we are looking at"""
    items = pd.read_csv('data/D_ITEMS.csv')
    measurements = json.load(open('measurements.json'))
    measurements_list = [i for i_s in measurements for i in i_s]
    items_subset = items[items.LABEL.isin(measurements_list)]

    return items_subset


if __name__ == '__main__':
    patients = get_stays()
    variables = get_variable_codes()
