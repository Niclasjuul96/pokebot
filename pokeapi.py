import requests

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/{}"
POKEAPI_SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/{}"

def get_pokemon_data(pokemon_id):
    response = requests.get(POKEAPI_URL.format(pokemon_id))
    if response.status_code != 200:
        return None
    data = response.json()
    name = data["name"].capitalize()
    sprites = data["sprites"]["other"]
    sprite_url = sprites["showdown"]["front_default"] or sprites["official-artwork"]["front_default"]
    return name, sprite_url

def get_capture_rate(pokemon_id):
    response = requests.get(POKEAPI_SPECIES_URL.format(pokemon_id))
    if response.status_code != 200:
        return None
    return response.json()["capture_rate"]

# Pokemon gif - https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/25.gif
# Bedre pokemon gif tror jeg "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/25.gif