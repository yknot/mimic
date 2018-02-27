import json
import csv
from contextlib import ExitStack
import pandas as pd


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

    return merged_a_f_long.HADM_ID.values


def get_variable_codes():
    """get the codes for the variables we are looking at"""
    items = pd.read_csv('data/D_ITEMS.csv')
    measurements = json.load(open('measurements.json'))
    measurements_list = [i for i_s in measurements.values() for i in i_s]
    items_subset = items[items.ITEMID.isin(measurements_list)]

    return items_subset.ITEMID.values


def subset_chartevents(item_id, hadm_id):
    """go throught 30gb+ chart events file"""
    with ExitStack() as stack:
        f = stack.enter_context(open('data/CHARTEVENTS.csv'))
        o = stack.enter_context(open('data/subset_CHARTEVENTS.csv', 'w'))
        reader = csv.reader(f)
        writer = csv.writer(o, delimiter=",")
        i = 0
        ten = 330712484 // 10
        for row in reader:
            if i == 0:
                continue
            i += 1
            if i % ten == 0:
                print(f'{i//ten}% Done')
            # check item_id
            if int(row[4]) not in item_id:
                continue
            # check hadm_id
            if int(row[2]) not in hadm_id:
                continue

            writer.writerow(row)


if __name__ == '__main__':
    hadm_id = get_stays()
    item_id = get_variable_codes()

    subset_chartevents(item_id, hadm_id)
