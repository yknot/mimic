import sqlite3
import pandas as pd
import argparse
import os
import sys

FILE_LIST = [
    'D_ITEMS.csv',
    'NOTEEVENTS.csv',
    'PROCEDURES_ICD.csv',
    'DRGCODES.csv',
    'PRESCRIPTIONS.csv',
    'CPTEVENTS.csv',
    'D_ICD_DIAGNOSES.csv',
    'CAREGIVERS.csv',
    'SERVICES.csv',
    'INPUTEVENTS_CV.csv',
    'INPUTEVENTS_MV.csv',
    'DATETIMEEVENTS.csv',
    'D_ICD_PROCEDURES.csv',
    'CHARTEVENTS.csv',
    'PROCEDUREEVENTS_MV.csv',
    'ICUSTAYS.csv',
    'LABEVENTS.csv',
    'OUTPUTEVENTS.csv',
    'DIAGNOSES_ICD.csv',
    'ADMISSIONS.csv',
    'PATIENTS.csv',
    'D_LABITEMS.csv',
    'D_CPT.csv',
    'CALLOUT.csv',
    'TRANSFERS.csv',
    'MICROBIOLOGYEVENTS.csv'
]


def check_file(f):
    # ensure file is new or can be replaced
    if os.path.exists(f):
        raw = input("Replace file {}?".format(f))
        if raw in ['Y', 'y']:
            os.remove(f)
        else:
            print('Change filename or relocate existing file.')
            sys.exit()


def files_to_database(data, filename='MIMIC.db'):
    check_file(filename)

    conn = sqlite3.connect(filename)
    for f in FILE_LIST:
        df = pd.read_csv(os.path.join(data, f))
        df.to_sql(f[:-4], conn)

    conn.close()


def parse_args(parser):
    parser.add_argument('data_dir', type=str, metavar='<data_dir>',
                        help='Directory with the csv files')

    return parser.parse_args()


if __name__ == '__main__':
    # parse arguments, get data folder and files
    args = parse_args(argparse.ArgumentParser())
    data_dir = os.path.join(os.getcwd(), args.data_dir)
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

    # dummy check for right folder
    if len(set(FILE_LIST).intersection(files)) != 26:
        print('Not the right data folder.')
        sys.exit()

    files_to_database(data_dir)
