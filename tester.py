import requests
import json
from prettytable import PrettyTable
import sys
from loguru import logger

API_KEY="8d3f57a9458d9b1ea62ce6b28f6df4e7"
BEARER="Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4ZDNmNTdhOTQ1OGQ5YjFlYTYyY2U2YjI4ZjZkZjRlNyIsInN1YiI6IjY0ZTA2Y2JmYWFlYzcxMDNmYTQ4NzBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.qfJ2QoGnAkMkblZJBhJGv8K3WC9izald8K7TQ0Eak70"
HEADER = {
    "accept": "application/json",
    "Authorization":BEARER
    }
AUTH_URL = "https://api.themoviedb.org/3/authentication?api_key=8d3f57a9458d9b1ea62ce6b28f6df4e7"
videos="https://api.themoviedb.org/3/movie/11/videos"




auth_response = requests.get(AUTH_URL, headers=HEADER)
videos_response = requests.get(videos, headers=HEADER)
test_response = requests.get("https://api.themoviedb.org/3/search/movie?query=star%20wars", headers=HEADER)

videos_response_parsed = json.loads(test_response.text)

def _auth_check():
    response = requests.get(AUTH_URL)
    if not response.ok:
        logger.error(response.status_code)
        sys.exit(0)

def api_call(url) -> json.load:
    response = requests.get(url, headers=HEADER)

    return json.loads(response.text)


if __name__ == "__main__":
    while True:
        _auth_check()
        #movie_input = input("What movie would you like to watch?\n")
        movie_input = ""
        movie_input_parsed = movie_input.replace(" ", '%20')
        movie_matches = api_call(url=f"https://api.themoviedb.org/3/search/movie?query={movie_input_parsed}")
        if not movie_matches["results"]:
            logger.error(f"no movies found")
            continue
        for index, match in enumerate(movie_matches["results"]):
            if  movie_input.lower() in match["original_title"].lower():
                print(f"exact match for:{match['original_title']}")
            

