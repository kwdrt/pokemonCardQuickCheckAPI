import requests
import json
import os

pokeapi_url = "https://pokeapi.co/api/v2/pokemon/" #add lowercase pokemon name after that
pokemontcg_url = "https://api.pokemontcg.io/v2/cards?q=name:" #add pokemon name after that
nbp_url = "http://api.nbp.pl/api/exchangerates/rates/a/eur" #don't add anything
chart_base_url = "https://image-charts.com/chart?cht=p3&chs=700x400"

#example of chart: https://image-charts.com/chart?cht=p3&chs=700x400&chd=t:60,40&chl=pokemon1|pokemon2

def get_base_url(source):
    return os.path.dirname(source) + '/'


def create_error_message(source, number):
    if number == 404 and get_base_url(source) == pokeapi_url:
        return "At least one of Pokemon was not found! Please check whether you have written in both names correctly."
    if number // 100 == 4:
        return "Error at source " + source + ", probably due to client error " + str(number) + ", please check the data in input."
    if number // 100 == 5:
        return "Error at source " + source + ", server error " + str(number) + ", we were unable to reach one of the servers we acquire data from, please try again later."
    return None


def validate_data(data, source, errors):
    if data.status_code // 100 == 2:
        return True
    else:
        errors.append(create_error_message(source, data.status_code))
        return False

def data_response(data, source, errors):
    if validate_data(data, source, errors):
        return json.loads(data.content)
    else:
        return None

def get_pokemon_data(pokemon_name, errors, results):
    data = requests.get(pokeapi_url + str.lower(pokemon_name))
    results[pokemon_name] = data_response(data, pokeapi_url, errors)

def get_pokemon_cards(pokemon_name, errors, results):
    data = requests.get(pokemontcg_url + str.lower(pokemon_name))
    results[pokemon_name + "_cards"] = data_response(data, pokemontcg_url, errors)

def get_current_eur(errors, results):
    data = requests.get(nbp_url)
    results["eur"] = data_response(data, nbp_url, errors)

def get_chart(pokemon_name_one, pokemon_name_two, total_cards_one, total_cards_two, title, errors):
    chart_url = chart_base_url + "&chd=a:{0},{1}&chl={2}|{3}&chtt={4}".format(total_cards_one, total_cards_two, pokemon_name_one, pokemon_name_two, title)
    return chart_url
