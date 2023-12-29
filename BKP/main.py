import pandas as pd
import sqlite3
import ast
from config import CONFIG as config

SQLITE_DB = config["SQLITE_DB"]
SQLITE_STREAMINGPLATFORM_TABLE = config["SQLITE_STREAMINGPLATFORM_TABLE"]
SQLITE_IMDB_TMDB_MOVIES_TABLE = config['SQLITE_IMDB_TMDB_MOVIES_TABLE']


# Refresh data in SQLITE DB
def load_csv_to_sqlite(filename):
    df = pd.read_csv(filename)
    conn = sqlite3.connect(SQLITE_DB)
    headers_mapping = {"tconst": "IMDB_ID",
                       "averageRating": "IMDB_RATING",
                       "numVotes": "IMDB_VOTES",
                       "TMDB_ID": "TMDB_ID",
                       "TITLE": "TITLE",
                       "POSTER_PATH": "POSTER_PATH",
                       "STREAMING_PLATFORM": "STREAMING_PLATFORM"}
    df.rename(columns=headers_mapping,
              inplace=True)

    df.to_sql(SQLITE_IMDB_TMDB_MOVIES_TABLE, conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

    print(f"Data load to SQLITE DATABASE - DONE!! ")


def refresh_streamingplatforms_table(filename):
    df = pd.read_csv(filename, na_filter=False)
    all_streaming_options_set = set()
    all_streaming_options = df['STREAMING_PLATFORM'].to_list()
    for items_strings in all_streaming_options:
        if items_strings:
            item_list = ast.literal_eval(items_strings)
            for i in item_list:
                all_streaming_options_set.add(i)

    print(all_streaming_options_set)
    conn = sqlite3.connect(SQLITE_DB)

    df_platform = pd.DataFrame(list(all_streaming_options_set), columns=["PLATFORM"])
    df_platform.to_sql(SQLITE_STREAMINGPLATFORM_TABLE, conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

csv_filename = "dataset_glue_export.csv"
load_csv_to_sqlite(csv_filename)
refresh_streamingplatforms_table(csv_filename)