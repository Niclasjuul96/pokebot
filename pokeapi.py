import requests

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/{}"

def get_pokemon_name(pokemon_id):
    response = requests.get(POKEAPI_URL.format(pokemon_id))
    if response.status_code!=200:
        return None
    return response.json()["name"].capitalize()


# Pokemon gif - https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/25.gif
# Bedre pokemon gif tror jeg "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/25.gif