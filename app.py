import streamlit as st
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('imdb_tmdb_movie_database.db')


# Function to check if table exists
def table_exists(table_name):
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    result = pd.read_sql_query(query, conn, params=(table_name,))
    return not result.empty


# Function to fetch data from the database
def fetch_data(query, params=()):
    return pd.read_sql_query(query, conn, params=params)


def get_genres():
    query = """
    SELECT DISTINCT GENRES FROM genres 
    """
    genres = fetch_data(query)
    return genres['GENRES'].tolist()

def get_countries():
    query = """
    SELECT DISTINCT COUNTRIES FROM countries 
    """
    countries = fetch_data(query)
    return countries['COUNTRIES'].tolist()

# Check if required tables exist
tables = ['imdb_tmdb_movies', 'imdb_tmdb_tv', 'streaming_platforms']
missing_tables = [table for table in tables if not table_exists(table)]

if missing_tables:
    st.error(f"Missing tables in database: {', '.join(missing_tables)}")
else:
    # Function to fetch streaming platforms
    def get_streaming_platforms():
        query = "SELECT DISTINCT PLATFORM FROM streaming_platforms"
        platforms = fetch_data(query)
        return platforms['PLATFORM'].tolist()


    # Streamlit App Layout
    st.set_page_config(layout="wide")

    # Title
    st.title('WatchByStream App - Powered by The Movie Database (TMDB) API')

    # Section 1: Search Movie/TV
    st.header('Search Movie/TV')
    search_query = st.text_input("Enter a Movie/TV Show Name:")


    def display_pagination_buttons(page, total_pages, key_prefix, button_key):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if page > 1:
                st.button("Previous Page", key=f"{button_key}_{key_prefix}_prev",
                          on_click=lambda: st.session_state.update({key_prefix: page - 1}))
        with col2:
            st.text(f"Page {page} of {total_pages}")
        with col3:
            if page < total_pages:
                st.button("Next Page", key=f"{button_key}_{key_prefix}_next",
                          on_click=lambda: st.session_state.update({key_prefix: page + 1}))


    # Fetch search results
    if search_query:
        search_results = fetch_data(
            """
            SELECT * FROM (
                SELECT IMDB_ID, IMDB_RATING, IMDB_VOTES, TITLE_TYPE, TITLE, POSTER_PATH, STREAMING_PLATFORM
                FROM imdb_tmdb_movies
                UNION ALL
                SELECT IMDB_ID, IMDB_RATING, IMDB_VOTES, TITLE_TYPE, TITLE, POSTER_PATH, STREAMING_PLATFORM
                FROM imdb_tmdb_tv
            )
            WHERE TITLE LIKE ?
            """, ('%' + search_query + '%',)
        )

        # Pagination for search results
        if 'search_results_page' not in st.session_state:
            st.session_state.search_results_page = 1

        search_results_page = st.session_state.search_results_page
        search_results_per_page = 10
        total_search_pages = (len(search_results) - 1) // search_results_per_page + 1

        display_pagination_buttons(search_results_page, total_search_pages, 'search_results_page',
                                   button_key="search_top")

        start_idx = (search_results_page - 1) * search_results_per_page
        end_idx = start_idx + search_results_per_page

        for idx, row in search_results.iloc[start_idx:end_idx].iterrows():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(f"https://image.tmdb.org/t/p/w154{row['POSTER_PATH']}", width=100)
            with col2:
                st.write(f"**{row['TITLE']}**")
                st.write(f"Title Type: {row['TITLE_TYPE']}")
                st.write(f"IMDB Rating: {row['IMDB_RATING']}, Votes: {row['IMDB_VOTES']}")
                st.write(f"Streaming Platforms: {row['STREAMING_PLATFORM']}")
            st.write("---")

        display_pagination_buttons(search_results_page, total_search_pages, 'search_results_page',
                                   button_key="search_bottom")

    # Section 2: Filter Movies/TV
    st.header('Filter Movies/TV')
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        selected_title_type = st.multiselect("Streaming Platforms", ["MOVIE","TV"], default=["MOVIE","TV"])

    with col2:
        min_rating, max_rating = st.slider("Select Min Max Rating value", 0.0, 10.0, (7.0, 10.0), 0.1)

    with col3:
        min_votes, max_votes = st.slider("Select Min Max Votes value", 0, 3000000, (100000, 3000000), 50000)

    with col4:
        platforms = get_streaming_platforms()
        selected_platforms = st.multiselect("Streaming Platforms", platforms, default=["Netflix", "Amazon Prime Video", "Max", "Hulu", "Disney Plus", "Crunchyroll"])

    with col5:
        sort_by = st.selectbox("Sort By", ["IMDB_RATING", "IMDB_VOTES"])
        sort_direction = st.radio("Direction", ["Ascending", "Descending"], index=1)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        genres = get_genres()
        selected_genre = st.multiselect("Genre", genres)

    with col2:
        countries = get_countries()
        selected_country = st.multiselect("Country", countries)

    with col3:
        min_year, max_year = st.slider("Select Min Max Year value", 1980, 2024, (1980, 2024), 1)

    # Filter query
    filter_query = """
    SELECT * FROM (
        SELECT IMDB_ID, IMDB_RATING, IMDB_VOTES, TITLE_TYPE, TITLE, POSTER_PATH, STREAMING_PLATFORM, GENRES, ORIGIN_COUNTRY, RELEASE_DATE
        FROM imdb_tmdb_movies
        UNION ALL
        SELECT IMDB_ID, IMDB_RATING, IMDB_VOTES, TITLE_TYPE, TITLE, POSTER_PATH, STREAMING_PLATFORM, GENRES, ORIGIN_COUNTRY, RELEASE_DATE
        FROM imdb_tmdb_tv
    )
    WHERE IMDB_RATING BETWEEN ? AND ?
    AND IMDB_VOTES BETWEEN ? AND ?
    AND RELEASE_DATE BETWEEN ? AND ?
    """

    # Apply streaming platform filter
    params = [min_rating, max_rating, min_votes, max_votes, min_year, max_year]
    if selected_platforms:
        platforms_filter = " AND (" + " OR ".join(["STREAMING_PLATFORM LIKE ?" for _ in selected_platforms]) + ")"
        filter_query += platforms_filter
        params.extend(['%' + platform + '%' for platform in selected_platforms])
    if selected_title_type:
        title_type_filter = " AND (" + " OR ".join(["TITLE_TYPE LIKE ?" for _ in selected_title_type]) + ")"
        filter_query += title_type_filter
        params.extend(['%' + type + '%' for type in selected_title_type])
    if selected_genre:
        genre_filter = " AND (" + " OR ".join(["GENRES LIKE ?" for _ in selected_genre]) + ")"
        filter_query += genre_filter
        params.extend(['%' + genre + '%' for genre in selected_genre])
    if selected_country:
        country_filter = " AND (" + " OR ".join(["ORIGIN_COUNTRY LIKE ?" for _ in selected_country]) + ")"
        filter_query += country_filter
        params.extend(['%' + country + '%' for country in selected_country])

    # Apply sorting
    filter_query += f" ORDER BY {sort_by} {'ASC' if sort_direction == 'Ascending' else 'DESC'}"

    # Fetch filtered results
    filtered_results = fetch_data(filter_query, params)
    # st.write(filtered_results.columns)

    # Pagination for filtered results
    if 'filtered_results_page' not in st.session_state:
        st.session_state.filtered_results_page = 1

    filtered_results_page = st.session_state.filtered_results_page
    filtered_results_per_page = 10
    total_filtered_pages = (len(filtered_results) - 1) // filtered_results_per_page + 1

    display_pagination_buttons(filtered_results_page, total_filtered_pages, 'filtered_results_page',
                               button_key="list_top")

    start_idx = (filtered_results_page - 1) * filtered_results_per_page
    end_idx = start_idx + filtered_results_per_page

    for idx, row in filtered_results.iloc[start_idx:end_idx].iterrows():
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(f"https://image.tmdb.org/t/p/w154{row['POSTER_PATH']}", width=100)
        with col2:
            st.write(f"**{row['TITLE']}**")
            st.write(f"Title Type: {row['TITLE_TYPE']}")
            st.write(f"IMDB Rating: {row['IMDB_RATING']}, Votes: {row['IMDB_VOTES']}")
            st.write(f"Streaming Platforms: {row['STREAMING_PLATFORM']}")
            st.write(f"Genre: {row['GENRES']}")
            st.write(f"Origin Country: {row['ORIGIN_COUNTRY']}")
            st.write(f"Release Date: {row['RELEASE_DATE']}")
        st.write("---")

    display_pagination_buttons(filtered_results_page, total_filtered_pages, 'filtered_results_page',
                               button_key="list_bottom")
