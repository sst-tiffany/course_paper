import datetime as dt
import os

import numpy as np
import pandas as pd

from research_tools.tirvim.utils.get_ftp_file import get_ftp_file


def read_catalog(path_to_src_file):
    with open(path_to_src_file, 'r') as f:
        txt = f.read()
    data = []
    columns = []
    for row in txt.split('\n'):
        if row:
            if not row.startswith('#'):
                data.append(row.split())
            else:
                columns.append(row.split()[1:])
    columns = columns[np.array([sum([row.isdigit() for row in cols]) for cols in columns]).argmin()]

    df = pd.DataFrame(data, columns=columns)
    for col in ['nse', 'gr', 'rec1', 'rec2', 'id1', 'id2', 'n_avr', 'a_max', 'a', 'm', 'f', 'g']:
        df[col] = df[col].astype(int)

    for col in ['asun_sca', 'asmi_sca', 'pro_sca', 'asun_sol', 'asmi_sol', 'pro_sol', 'Ls']:
        df[col] = df[col].astype(float)

    df = df.sort_values(by=['nse'])

    df['utc_start'] = df['utc_start'].apply(lambda x: dt.datetime.strptime(x, '%Y-%b-%d-%H:%M:%S.%f'))
    df['utc_start'] = df['utc_start'].apply(lambda x: x.replace(microsecond=0))

    df['orb_num_hex'] = df['nse'].apply(lambda x: format(x, 'x'))
    return df


def filter_orbits(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['a_max'] > 2_500]
    df = df[df['n_avr'] < 27_200]

    # Zeros in the data in the beginning of March 2018.
    df = df[df['utc_start'] >= dt.datetime(2018, 3, 19, 0, 0, 0)]
    # Double pendulum motion control processor problems
    df = df[(df['utc_start'] < dt.datetime(2018, 4, 28, 0, 0, 0)) |
            (df['utc_start'] > dt.datetime(2018, 5, 23, 0, 0, 0))]
    # Stirling cooler overheating.
    df = df[(df['utc_start'] < dt.datetime(2018, 7, 15, 0, 0, 0)) |
            (df['utc_start'] > dt.datetime(2018, 9, 1, 0, 0, 0))]

    return df


def get_orbit_catalog():
    path_to_cat_orb = 'Pub/ACS_TIRVIM'
    cat_orb_file = 'mode_OCC_SOL_1542.txt'
    local_path = '/Users/t.kuzenko/course_paper/db'
    local_path_to_cat = os.path.join(local_path, 'catalog.csv')

    full_local_path = get_ftp_file(path_to_cat_orb, cat_orb_file, local_path)
    cat_orb = read_catalog(full_local_path)
    cat_orb = filter_orbits(cat_orb)
    cat_orb[['file', 'nse', 'orb_num_hex', 'rec1', 'rec2', 'Ls', 'utc_start']].to_csv(local_path_to_cat, index=False)
