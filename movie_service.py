from dotenv import load_dotenv
load_dotenv()

import requests
import os


TMDB_API_KEY = os.getenv("TMDB_API_KEY")


LANGUAGE_CODES = {
    "telugu": "te",
    "hindi": "hi",
    "tamil": "ta",
    "malayalam": "ml",
    "kannada": "kn"
}


def get_movies(query="telugu", year=None):
    if not TMDB_API_KEY:
        return "TMDB API key is missing. Add TMDB_API_KEY in your .env file and restart the app."

    language_code = LANGUAGE_CODES.get(query.lower(), "te")

    url = "https://api.themoviedb.org/3/discover/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "sort_by": "popularity.desc",
        "with_original_language": language_code,
        "language": "en-US",
        "page": 1
    }

    if year:
        params["primary_release_year"] = year

    response = requests.get(url, params=params)
    data = response.json()

    if "results" not in data:
        return f"TMDB error: {data}"

    results = data["results"]

    if len(results) == 0 and year:
        params.pop("primary_release_year", None)
        response = requests.get(url, params=params)
        data = response.json()
        results = data.get("results", [])

        if len(results) == 0:
            return f"No {query} movies found in TMDB."

        note = f"No {query} movies found for {year}. Showing popular {query} movies instead.\n\n"
    else:
        note = ""

    movies = []

    for movie in results[:6]:
        title = movie.get("title", "Unknown")
        release = movie.get("release_date", "Unknown")
        rating = movie.get("vote_average", "N/A")
        overview = movie.get("overview", "No story available.")

        movies.append(
            f"""🎬 {title}

⭐ Rating: {rating}
📅 Release: {release}
🎭 Language: {query.title()}

📝 Story:
{overview[:180]}...
"""
        )

    return note + "\n".join(movies)