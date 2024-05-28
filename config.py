CONFIG = {"SQLITE_DB": "imdb_tmdb_movie_database.db",
          "SQLITE_TOPRATED_TABLE": "movies_toprated",
          "SQLITE_STREAMINGPLATFORM_TABLE": "streaming_platforms",
          "SQLITE_IMDB_TMDB_MOVIES_TABLE": "imdb_tmdb_movies",
          "SQLITE_IMDB_TMDB_TV_TABLE": "imdb_tmdb_tv"}


headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNDU3MDA2NjBkNjg0MjdkMjMwM2FmMGI0ZmM2ODA0MiIsInN1YiI6IjY0ZmE5ZTdiZTBjYTdmMDBjYmU4NDZiMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.4_ewJkaXFru7807biidXcTQbcHpRufxIz5MpE5dQvtw"
}

headers_mapping = {"tconst": "IMDB_ID",
                   "averageRating": "IMDB_RATING",
                   "numVotes": "IMDB_VOTES",
                   "TMDB_ID": "TMDB_ID",
                   "TITLE_TYPE": "TITLE_TYPE",
                   "TITLE": "TITLE",
                   "POSTER_PATH": "POSTER_PATH",
                   "PLATFORM": "STREAMING_PLATFORM"}

imdb_urls = {"imdb_ratings": "https://datasets.imdbws.com/title.ratings.tsv.gz"}