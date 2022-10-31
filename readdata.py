import os.path
import pyam
import pandas as pd

if not os.path.exists("credentials.py"):
    with open("credentials.py", 'w') as f:
        f.write('USERNAME = "here.your.username"\n')
        f.write('PASSWORD = "here.your.password"\n')
    raise Exception("Provide your credentials in credentials.py")

from credentials import *

FILENAME_DB = "iiasa_db_data.csv"

pyam.iiasa.set_config(USERNAME, PASSWORD)

def get_from_iiasadb(update=True):
    if update and os.path.exists(FILENAME_DB):
        return pyam.read_iiasa
    else:
        return lambda **x: pyam.lazy_read_iiasa(file=FILENAME_DB, **x)

def read_iiasa(region='World', update=True, no_hist_data=False):
    df_database = get_from_iiasadb(update)(
        name='navigate_internal',
        scenario='NAV_Dem*',
        region=region
    )
    if not no_hist_data:
        hist_df = pyam.IamDataFrame(r'NAV_Dem-NPi-ref_historicresults.csv')
        df = pyam.IamDataFrame(pd.concat([df_database.as_pandas(meta_cols=False), hist_df.as_pandas(meta_cols=False)]))
    return df