CONFIG = {"SQLITE_DB": "imdb_tmdb_movie_database.db",
          "SQLITE_TOPRATED_TABLE": "movies_toprated",
          "SQLITE_STREAMINGPLATFORM_TABLE": "streaming_platforms",
          "SQLITE_IMDB_TMDB_MOVIES_TABLE": "imdb_tmdb_movies"}


headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNDU3MDA2NjBkNjg0MjdkMjMwM2FmMGI0ZmM2ODA0MiIsInN1YiI6IjY0ZmE5ZTdiZTBjYTdmMDBjYmU4NDZiMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.4_ewJkaXFru7807biidXcTQbcHpRufxIz5MpE5dQvtw"
}

imdb_urls = {"imdb_ratings": "https://datasets.imdbws.com/title.ratings.tsv.gz"}