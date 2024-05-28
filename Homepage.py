import streamlit as st
import pandas as pd
import sqlite3
# from streamlit_card import card
from config import CONFIG as config

SQLITE_DB = config["SQLITE_DB"]
SQLITE_STREAMINGPLATFORM_TABLE = config["SQLITE_STREAMINGPLATFORM_TABLE"]
SQLITE_IMDB_TMDB_MOVIES_TABLE = config['SQLITE_IMDB_TMDB_MOVIES_TABLE']
SQLITE_IMDB_TMDB_TV_TABLE = config['SQLITE_IMDB_TMDB_TV_TABLE']



@st.cache_data(show_spinner=True, ttl=3600)
def load_data_to_df():
    conn = sqlite3.connect(SQLITE_DB)
    sql_query = f'SELECT * FROM {SQLITE_IMDB_TMDB_MOVIES_TABLE}'
    df = pd.read_sql_query(sql_query, conn)
    conn.close()
    return df

@st.cache_data(show_spinner=True, ttl=3600)
def load_streamingplatform_data_to_df():
    conn = sqlite3.connect(SQLITE_DB)
    sql_query = f'SELECT * FROM {SQLITE_STREAMINGPLATFORM_TABLE}'
    df = pd.read_sql_query(sql_query, conn)
    conn.close()
    return df


def add_where_and_clause(base_sql_query, filter_count):
    if filter_count <= 0:
        raise Exception("Filter Count cannot be less than or equal to Zero")
    elif filter_count == 1:
        new_query = f"{base_sql_query}" + " where "
    else:
        new_query = f"{base_sql_query}" + " and "
    return new_query


def add_sql_condition_name(base_sql_query, user_input_name, filter_count):
    new_query = add_where_and_clause(base_sql_query, filter_count)
    final_query = f"{new_query}" + f"TITLE LIKE '%{user_input_name}%'"
    return final_query


def add_sql_condition_streaming_platform(base_sql_query, streaming_options, filter_count):
    new_query = add_where_and_clause(base_sql_query, filter_count)
    if len(streaming_options) == 1:
        final_query = f"{new_query}" + f"STREAMING_PLATFORM LIKE '%{streaming_options[0]}%'"
    elif len(streaming_options) > 1:
        # streaming_options_tuple = tuple(streaming_options)
        # final_query = f"{new_query}" + f"platform IN {streaming_options_tuple}"

        joined_sql = ' OR'.join([" STREAMING_PLATFORM LIKE '%{0}%'".format(str_opt) for str_opt in streaming_options])
        final_query = f"{new_query}" + f"({joined_sql})"
    else:
        raise Exception("Invalid Streaming Options")
    return final_query


def add_sql_condition_rating(base_sql_query, rating_slider, filter_count):
    new_query = add_where_and_clause(base_sql_query, filter_count)
    final_query = f"{new_query}" + f"IMDB_RATING between {rating_slider[0]} and {rating_slider[1]}"
    return final_query


def add_sql_condition_votecount(base_sql_query, votecount_slider, filter_count):
    new_query = add_where_and_clause(base_sql_query, filter_count)
    final_query = f"{new_query}" + f"IMDB_VOTES between {votecount_slider[0]} and {votecount_slider[1]}"
    return final_query


def filter_data_by_name_to_df(user_input_name=None, streaming_options=None, rating_slider=None, votecount_slider=None):
    base_sql_query = f"SELECT * FROM {SQLITE_IMDB_TMDB_MOVIES_TABLE}"
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
    # st.markdown('## FINAL SQL Query Executed :')
    # st.write(base_sql_query)
    df = pd.read_sql_query(base_sql_query, conn)
    sort_column = "IMDB_RATING"
    df_sorted = df.sort_values(by=sort_column, ascending=False)
    conn.close()
    return df_sorted

# USE DEFAULT SETTINGS
def set_defaults_true():
    # st.write(st.session_state.use_defaults)
    # st.write(st.session_state.streaming_options)
    # st.write(st.session_state.rating_slider)
    # st.write(st.session_state.votecount_slider)
    st.session_state.streaming_options = ["Netflix", "Disney Plus", "Hulu", "Max", "Amazon Prime Video", "Crunchyroll"]
    # st.session_state.streaming_options = ["Crunchyroll"]
    st.session_state.rating_slider = (7.0, 10.0)
    st.session_state.votecount_slider = (100000, 5000000)


def set_defaults_false():
    # st.write(st.session_state.use_defaults)
    # st.write(st.session_state.streaming_options)
    # st.write(st.session_state.rating_slider)
    # st.write(st.session_state.votecount_slider)
    st.session_state.streaming_options = []
    st.session_state.rating_slider = (0.0, 10.0)
    st.session_state.votecount_slider = (0, 5000000)

def load_more(total_rows, current_row_count):
    if total_rows - current_row_count <= 10:
        st.session_state.incremental_limit += (total_rows - current_row_count)
    else:
        st.session_state.incremental_limit += 10


def save_config_to_session():
    st.session_state.current_config = {"platform": st.session_state.streaming_options,
                                       "rating": st.session_state.rating_slider,
                                       "votes": st.session_state.votecount_slider
                                       }
    st.success("Config Saved!")


def load_config_from_session():
    if "current_config" in st.session_state:
        st.session_state.streaming_options = st.session_state.current_config["platform"]
        st.session_state.rating_slider = st.session_state.current_config["rating"]
        st.session_state.votecount_slider = st.session_state.current_config["votes"]
        st.success("Config Loaded!")
    else:
        st.error("No Saved Config Found!")


def clear_config():
    st.session_state.streaming_options = []
    st.session_state.rating_slider = (0.0, 10.0)
    st.session_state.votecount_slider = (0, 5000000)


def display_results(filtered_data, limit_data):
    for row in range(limit_data):
        st.write(f"row: {row}")
        imdb_id = filtered_data.iloc[row][0]
        imdb_rating = filtered_data.iloc[row][1]
        imdb_votes = filtered_data.iloc[row][2]
        tmdb_id = filtered_data.iloc[row][3]
        movie_name = filtered_data.iloc[row][5]
        poster_path = filtered_data.iloc[row][6]
        streaming_platform = filtered_data.iloc[row][7]

        with st.expander(f"{movie_name}", expanded=True):
            col1, col2 = st.columns([1, 4])
            with col1:
                image_url = f"https://image.tmdb.org/t/p/w154{poster_path}"  # width values --> w92, w154, w185, w342, w500, w780, original
                st.image(image_url, use_column_width=False)
            with col2:
                st.markdown(f"TITLE: :red[{movie_name}]")
                st.markdown(f"IMDB RATING: :red[{imdb_rating}]")
                st.markdown(f"IMDB VOTES: :red[{imdb_votes}]")
                st.markdown(f"STREAMING PLATFORM: :red[{streaming_platform}]")

    current_row_count = limit_data
    if current_row_count < total_rows:
        # button_load_more = st.button("Load More", on_click=load_more, args=(total_rows, current_row_count), key="button_load_more")
        # button_load_more = st.button("Load More", on_click=display_results, args=(filtered_data, limit_data + 10),
        #                              key="button_load_more")
        button_load_more = st.button("Load More",key="button_load_more")
        if button_load_more:
            display_results(filtered_data, limit_data + 10)


def load_movies_data():
    conn = sqlite3.connect(SQLITE_DB)
    sql_query = f'SELECT * FROM {SQLITE_IMDB_TMDB_MOVIES_TABLE}'
    df = pd.read_sql_query(sql_query, conn)
    conn.close()
    return df

def load_tv_data():
    conn = sqlite3.connect(SQLITE_DB)
    sql_query = f'SELECT * FROM {SQLITE_IMDB_TMDB_TV_TABLE}'
    df = pd.read_sql_query(sql_query, conn)
    conn.close()
    return df

@st.cache_data(show_spinner=False, ttl=3600)
def split_frame(input_df, rows):
    df = [input_df.iloc[i : i + rows - 1, :] for i in range(0, len(input_df), rows)]
    return df

def display_results_from_df(df):
    top_menu = st.columns(3)
    with top_menu[0]:
        sort_input = st.radio("Sort Data", options=["Yes", "No"], horizontal=1, index=0)
    if sort_input == "Yes":
        with top_menu[1]:
            sort_field = st.selectbox("Sort By", options=df.columns, index=1)
        with top_menu[2]:
            sort_direction = st.radio("Direction", options=["⬆️", "⬇️"], horizontal=True, index=1)
        df = df.sort_values(
            by=sort_field, ascending=sort_direction == "⬆️", ignore_index=True
        )

    pagination = st.container()
    bottom_menu = st.columns((4, 1, 1))
    with bottom_menu[2]:
        batch_size = st.selectbox("Page Size", options=[25, 50, 100])
    with bottom_menu[1]:
        total_pages = (
            int(len(df) / batch_size) if int(len(df) / batch_size) > 0 else 1
        )
        current_page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
    with bottom_menu[0]:
        st.markdown(f"Page **{current_page}** of **{total_pages}** ")

    pages = split_frame(df, batch_size)
    # pagination.dataframe(data=pages[current_page - 1], use_container_width=True)

    if not pages:
        st.error("No Results for current filters")
        st.stop()

    with pagination:
        data = pages[current_page - 1]
        for row in range(len(data)):
            st.write(f"Row Number: {row}")
            imdb_id = data.iloc[row][0]
            imdb_rating = data.iloc[row][1]
            imdb_votes = data.iloc[row][2]
            tmdb_id = data.iloc[row][3]
            title_type = data.iloc[row][4]
            movie_name = data.iloc[row][5]
            poster_path = data.iloc[row][6]
            streaming_platform = data.iloc[row][7]

            with st.expander(f"{movie_name}", expanded=True):
                col1, col2 = st.columns([1, 4])
                with col1:
                    image_url = f"https://image.tmdb.org/t/p/w154{poster_path}"  # width values --> w92, w154, w185, w342, w500, w780, original
                    st.image(image_url, use_column_width=False)
                with col2:
                    st.markdown(f"TITLE: :red[{movie_name}]")
                    st.markdown(f"TITLE TYPE: :red[{title_type}]")
                    st.markdown(f"IMDB RATING: :red[{imdb_rating}]")
                    st.markdown(f"IMDB VOTES: :red[{imdb_votes}]")
                    st.markdown(f"STREAMING PLATFORM: :red[{streaming_platform}]")

    # current_row_count = limit_data
    # if current_row_count < total_rows:
    #     # button_load_more = st.button("Load More", on_click=load_more, args=(total_rows, current_row_count), key="button_load_more")
    #     # button_load_more = st.button("Load More", on_click=display_results, args=(filtered_data, limit_data + 10),
    #     #                              key="button_load_more")
    #     button_load_more = st.button("Load More",key="button_load_more")
    #     if button_load_more:
    #         display_results(filtered_data, limit_data + 10)


def apply_filters(user_input_name=None, title_type_input=None, streaming_options=None, rating_slider=None, votecount_slider=None):
    df_filtered = pd.DataFrame()

    if "MOVIE" in title_type_input:
        movies = load_movies_data()
        df_filtered = pd.concat([df_filtered, movies])
    if "TV" in title_type_input:
        tv = load_tv_data()
        df_filtered = pd.concat([df_filtered, tv])

    if user_input_name:
        df_filtered = df_filtered[df_filtered["TITLE"] == user_input_name]

    if streaming_options:
        mask = df_filtered['STREAMING_PLATFORM'].apply(lambda x: any(platform in x for platform in streaming_options) if x is not None else False)
        df_filtered = df_filtered[mask]

    if rating_slider:
        df_filtered = df_filtered[df_filtered["IMDB_RATING"].between(rating_slider[0], rating_slider[1])]

    if votecount_slider:
        df_filtered = df_filtered[df_filtered["IMDB_VOTES"].between(votecount_slider[0], votecount_slider[1])]

    return df_filtered






if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.title('WatchByStream App - Powered by The Movie Database (TMDB) API')

    streaming_platforms_df = load_streamingplatform_data_to_df()
    all_streaming_options_set = set(streaming_platforms_df["PLATFORM"].to_list())

    # st.write(st.session_state)



    # use_defaults = st.toggle('Use Default Configuration', value=False, key="use_defaults")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        button_use_default_config = st.button('Use Default Configuration', type="primary", key="use_default_config")
    with col2:
        button_save_config = st.button('Save Configuration', type="primary", key="save_config")
    with col3:
        button_load_config = st.button('Load Configuration', type="primary", key="load_config")
    with col4:
        button_clear_config = st.button('Clear Configuration', type="primary", key="clear_config")


    if button_use_default_config:
        set_defaults_true()
    # else:
    #     set_defaults_false()

    if button_save_config:
        save_config_to_session()

    if button_load_config:
        load_config_from_session()

    if button_clear_config:
        clear_config()




    # TITLE FILTER
    user_input_name = st.text_input('Enter a Movie Name:', '')


    # TITLE TYPE FILTER
    title_type_input = st.multiselect("Select Title Types",["MOVIE","TV"], default=["MOVIE","TV"], key="title_type_input")

    # STREAMING PLATFORM Filter
    streaming_options = st.multiselect(
        'Streaming Platforms',
        all_streaming_options_set, key="streaming_options")
    # st.write('You selected:', streaming_options)

    # TMDB_RATINGS Filter
    rating_slider = st.slider('Select Min Max Rating value', min_value=0.0, max_value=10.0, value=(0.0, 10.0), step=0.10,
                              key="rating_slider")
    # st.write('Values:', rating_slider)

    # TMDB_VOTECOUNT Filter
    votecount_slider = st.slider('Select Min Max Votes value', min_value=0, max_value=5000000, value=(0, 5000000),
                                 key="votecount_slider")
    # st.write('Values:', votecount_slider)

    # # APPLY ALL FILTERS FROM USER
    # filtered_data = filter_data_by_name_to_df(user_input_name, streaming_options, rating_slider, votecount_slider)
    # if len(filtered_data) > 0:
    #     total_rows = len(filtered_data)
    #     st.write(f"Total Results: :red[{total_rows}]")
    #     # if "incremental_limit" not in st.session_state:
    #     if total_rows > 10:
    #         st.session_state.incremental_limit = 10
    #     else:
    #         st.session_state.incremental_limit = total_rows
    #
    #     limit_data = st.session_state.incremental_limit
    #     st.write(f"Limit data : {limit_data}")
    #
    #     if total_rows > 10:
    #         limit_data = 10
    #     else:
    #         limit_data = total_rows
    #     display_results(filtered_data, limit_data)
    #
    #     # current_row_count = st.session_state.incremental_limit
    #     # st.write(f"Current row count: {current_row_count}")
    #
    # else:
    #     st.info('No Matching Data Found')

    df_filtered = apply_filters(user_input_name, title_type_input, streaming_options, rating_slider, votecount_slider)
    sorted_df = df_filtered.sort_values(by='IMDB_RATING', ascending=False)
    st.dataframe(df_filtered.head())
    display_results_from_df(df_filtered)