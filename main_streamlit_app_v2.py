import streamlit as st
import sqlite3
import pandas as pd
from main_streamlit_app_config_v2 import CONFIG as config

SQLITE_DB = config["SQLITE_DB"]
SQLITE_TOPRATED_TABLE =config["SQLITE_TOPRATED_TABLE"]
SQLITE_STREAMINGPLATFORM_TABLE = config["SQLITE_STREAMINGPLATFORM_TABLE"]


# SQLITE_DB = "mydatabase.db"
# SQLITE_TABLE ="mytable"

def load_data_to_df():
    conn = sqlite3.connect(SQLITE_DB)
    sql_query = f'SELECT * FROM {SQLITE_TOPRATED_TABLE}'
    df = pd.read_sql_query(sql_query, conn)
    conn.close()
    return df

def load_streamingplatform_data_to_df():
    conn = sqlite3.connect(SQLITE_DB)
    sql_query = f'SELECT * FROM {SQLITE_STREAMINGPLATFORM_TABLE}'
    df = pd.read_sql_query(sql_query, conn)
    conn.close()
    return df

def add_where_and_clause(base_sql_query, filter_count):
    if filter_count <= 0:
        raise Exception ("Filter Count cannot be less than or equal to Zero")
    elif filter_count == 1:
        new_query = f"{base_sql_query}" + " where "
    else:
        new_query = f"{base_sql_query}" + " and "
    return new_query


def add_sql_condition_name(base_sql_query, user_input_name, filter_count):
    new_query = add_where_and_clause(base_sql_query, filter_count)
    final_query = f"{new_query}" + f"name LIKE '%{user_input_name}%'"
    return final_query


def add_sql_condition_streaming_platform(base_sql_query, streaming_options, filter_count):
    new_query = add_where_and_clause(base_sql_query, filter_count)
    if len(streaming_options) == 1:
        final_query = f"{new_query}" + f"platform LIKE '%{streaming_options[0]}%'"
    elif len(streaming_options) > 1:
        # streaming_options_tuple = tuple(streaming_options)
        # final_query = f"{new_query}" + f"platform IN {streaming_options_tuple}"

        joined_sql = ' OR'.join([" platform LIKE '%{0}%'".format(str_opt) for str_opt in streaming_options])
        final_query = f"{new_query}" + f"({joined_sql})"
    else:
        raise Exception ("Invalid Streaming Options")
    return final_query


def add_sql_condition_rating(base_sql_query, rating_slider, filter_count):
    new_query = add_where_and_clause(base_sql_query, filter_count)
    final_query = f"{new_query}" + f"rating between {rating_slider[0]} and {rating_slider[1]}"
    return final_query

def add_sql_condition_votecount(base_sql_query, votecount_slider, filter_count):
    new_query = add_where_and_clause(base_sql_query, filter_count)
    final_query = f"{new_query}" + f"vote_count between {votecount_slider[0]} and {votecount_slider[1]}"
    return final_query

def filter_data_by_name_to_df(user_input_name = None, streaming_options = None,rating_slider = None, votecount_slider = None):
    base_sql_query = f"SELECT * FROM {SQLITE_TOPRATED_TABLE}"
    filter_count = 0
    if user_input_name:
        filter_count += 1
        base_sql_query = add_sql_condition_name(base_sql_query, user_input_name, filter_count)
    if streaming_options:
        filter_count += 1
        base_sql_query = add_sql_condition_streaming_platform(base_sql_query, streaming_options, filter_count)
    if rating_slider:
        filter_count += 1
        base_sql_query = add_sql_condition_rating(base_sql_query, rating_slider, filter_count)
    if votecount_slider:
        filter_count += 1
        base_sql_query = add_sql_condition_votecount(base_sql_query, votecount_slider, filter_count)

    conn = sqlite3.connect(SQLITE_DB)
    # sql_query = f"SELECT * FROM mytable WHERE name LIKE '%{user_input_name}%' and platform in {streaming_options_tuple}"
    st.markdown('## FINAL SQL Query Executed :')
    st.write(base_sql_query)
    df = pd.read_sql_query(base_sql_query, conn)
    conn.close()
    return df


# if '__name__' == '__main__':
st.title('SQLite Data Filter by Name')
user_input_name = st.text_input('Enter a Name:', '')

# Get list of all Streaming Platforms from DB to Generate MultiSelect Filter List
# full_df = load_data_to_df()
# all_streaming_options_set = set()
# all_streaming_options = full_df['platform'].to_list()
# for item in all_streaming_options:
#     items = item.split(',')
#     for i in items:
#         if i:
#             all_streaming_options_set.add(i)


streaming_platforms_df = load_streamingplatform_data_to_df()
all_streaming_options_set = set(streaming_platforms_df["platform"].to_list())

# STREAMING PLATFORM Filter
streaming_options = st.multiselect(
    'Streaming Platforms',
    all_streaming_options_set)
st.write('You selected:', streaming_options)

# TMDB_RATINGS Filter
rating_slider = st.slider('Select Min Max Rating value', min_value=0.0, max_value=10.0, value=(0.0,10.0), step=0.10 )
st.write('Values:', rating_slider)

# TMDB_VOTECOUNT Filter
votecount_slider = st.slider('Select Min Max Rating value', min_value=0, max_value=100000, value=(0,100000))
st.write('Values:', votecount_slider)

# APPLY ALL FILTERS FROM USER
filtered_data = filter_data_by_name_to_df(user_input_name, streaming_options, rating_slider, votecount_slider)
if len(filtered_data) > 0:
    # st.table(filtered_data)
    st.dataframe(filtered_data, hide_index=True)
else:
    st.info('No Matching Data Found')