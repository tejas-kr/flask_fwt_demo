import requests

url = "https://imdb8.p.rapidapi.com/auto-complete"

dummy_querystring = {"q":"Ramayana The legend of prince ram"}

headers = {
    "X-RapidAPI-Key": "b7c5624415mshae36f6d1f569aeap15b985jsnded89a764e55",
    "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
}

def get_movie_summary(querystring=dummy_querystring):

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.text