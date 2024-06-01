import json


def get_top_songs():
  return json.dumps([
    {'rank': 1, 'artist': ['Sabrina Carpenter'], 'title': 'Espresso'},
    {'rank': 2, 'artist': ['Tommy Richman'], 'title': 'MILLION DOLLAR BABY'},
    {'rank': 3, 'artist': ['Billie Eilish'], 'title': 'LUNCH'},
    {'rank': 4, 'artist': ['Kendrick Lamar'], 'title': 'Not Like Us'},
    {'rank': 5, 'artist': ['Billie Eilish'], 'title': 'Birds of a Feather'},
    {'rank': 6, 'artist': ['FlyyMenor', 'Cris Mj'], 'title': 'Gata Only'},
    {'rank': 7, 'artist': ['Post Malone', 'Morgan Wallen'], 'title': 'I Had Some Help (Feat. Morgan Wallen)'},
    {'rank': 8, 'artist': ['Hozier'], 'title': 'Too Sweet'},
    {'rank': 9, 'artist': ['Benson Boone'], 'title': 'Beautiful Things'},
    {'rank': 10, 'artist': ['Billie Eilish'], 'title': 'CHIHIRO'},
  ])


def get_current_weather(location):
  location_lower = location.lower()
  if 'tokyo' in location_lower:
    return json.dumps({'location': 'Tokyo', 'temperature': '10F'})
  elif 'san francisco' in location_lower:
    return json.dumps({'location': 'San Francisco', 'temperature': '82F'})
  elif 'paris' in location_lower:
    return json.dumps({'location': 'Paris', 'temperature': '22F'})
  else:
    return json.dumps({'location': location, 'temperature': None})
