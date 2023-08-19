import requests
import json
API_KEY="8d3f57a9458d9b1ea62ce6b28f6df4e7"
BEARER="Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4ZDNmNTdhOTQ1OGQ5YjFlYTYyY2U2YjI4ZjZkZjRlNyIsInN1YiI6IjY0ZTA2Y2JmYWFlYzcxMDNmYTQ4NzBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.qfJ2QoGnAkMkblZJBhJGv8K3WC9izald8K7TQ0Eak70"
movie_id=""

videos="https://api.themoviedb.org/3/movie/11/videos"
watch_providers=f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
url = "https://api.themoviedb.org/3/authentication?api_key=8d3f57a9458d9b1ea62ce6b28f6df4e7"

headers = {
    "accept": "application/json",
    "Authorization":BEARER
    }

auth_response = requests.get(url, headers=headers)
videos_response = requests.get(videos, headers=headers)
test_response = requests.get("https://api.themoviedb.org/3/search/movie?query=star%20wars", headers=headers)

print(videos_response.text)
videos_response_parsed = json.loads(test_response.text)
print(videos_response_parsed["results"][0]["id"])
for test in videos_response_parsed["results"][0]["id"]:
    print(test)