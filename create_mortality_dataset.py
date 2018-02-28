import json
import csv
from contextlib import ExitStack
import argparse
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

    return merged_a_f_long


def get_variable_codes():
    """get the codes for the variables we are looking at"""
    items = pd.read_csv('data/D_ITEMS.csv')
    measurements = json.load(open('measurements.json'))
    measurements_list = [i for i_s in measurements.values() for i in i_s]
    items_subset = items[items.ITEMID.isin(measurements_list)]

    return items_subset


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
                writer.writerow(row)
                i += 1
                continue
            i += 1
            if i % ten == 0:
                print(f'{i * 10//ten}% Done')
            # check item_id
            if int(row[4]) not in item_id:
                continue
            # check hadm_id
            if int(row[2]) not in hadm_id:
                continue

            writer.writerow(row)


def trim_subset(admissions, patients):
    """open the subset created and trim it"""
    with ExitStack() as stack:
        f = stack.enter_context(open('data/subset_CHARTEVENTS.csv'))
        o = stack.enter_context(open('data/subset_trim_CHARTEVENTS.csv', 'w'))
        reader = csv.reader(f)
        writer = csv.writer(o, delimiter=",")

        headers = next(reader, None)  # skip the headers
        writer.writerow(headers)

        for row in reader:
            admit_time = admissions.ADMITTIME[admissions.HADM_ID == int(
                row[2])]
            diff = pd.to_datetime(row[5]) - \
                pd.to_datetime(admit_time).values[0]
            if diff.days <= 2:
                writer.writerow(row)


def parse_args(parser):
    """parse command line arguments"""
    parser.add_argument('--subset', action='store_true',
                        help="Create subset of CHARTEVENTS")
    parser.add_argument('--trim', action='store_true',
                        help="Trim subset of CHARTEVENTS")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args(argparse.ArgumentParser())

    if args.subset:
        hadm_id = get_stays().HADM_ID.values
        item_id = get_variable_codes().ITEMID.values

        subset_chartevents(item_id, hadm_id)
    if args.trim:
        admissions = get_stays()
        items = get_variable_codes()

        trim_subset(admissions, items)

    if not (args.subset or args.trim):
        print('No option selected')
