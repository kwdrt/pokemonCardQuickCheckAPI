from flask import Flask, render_template, request
from werkzeug.exceptions import HTTPException

from api_handlers import *
from threading import Thread

app = Flask(__name__)

def get_shown_card(i, cards_list, eur_value, data_source, add):
    eur_price = 0
    pln_price = 0
    try:
        if add:
            cards_list.append([data_source["data"][i]["images"]["small"],
                                            data_source["data"][i]["cardmarket"]["prices"]["avg7"],
                                            round(data_source["data"][i]["cardmarket"]["prices"]["avg7"] *
                                            eur_value["rates"][0]["mid"],2),
                                            data_source["data"][i]["cardmarket"]["url"]])

        eur_price = data_source["data"][i]["cardmarket"]["prices"]["avg7"]
        pln_price = data_source["data"][i]["cardmarket"]["prices"]["avg7"] * eur_value["rates"][0]["mid"]
    except KeyError:
        pass
    return eur_price, pln_price


@app.route("/", methods=['GET'])
def hello_point():
    return render_template("index.html")


@app.route("/result", methods=['POST'])
def run_service():
    errors = []
    errors.clear()
    results = {}

    if None in [request.form.get("pokemon_one"), request.form.get("pokemon_two"), request.form.get("shown_cards")]:
        errors.append("Unable to parse the received form data, please check your request")
        return render_template("results.html", errors=errors)
    else:
        pokemon_one = request.form.get("pokemon_one")
        pokemon_two = request.form.get("pokemon_two")
        shown_cards = int(request.form.get("shown_cards"))

    pokemon_one_thread = Thread(target=get_pokemon_data, args=(pokemon_one, errors, results))
    pokemon_two_thread = Thread(target=get_pokemon_data, args=(pokemon_two, errors, results))
    nbp_thread = Thread(target=get_current_eur(errors, results))
    pokemon_one_cards_thread = Thread(target=get_pokemon_cards(pokemon_one, errors, results))
    pokemon_two_cards_thread = Thread(target=get_pokemon_cards(pokemon_two, errors, results))

    pokemon_one_thread.start()
    pokemon_two_thread.start()
    nbp_thread.start()
    pokemon_one_cards_thread.start()
    pokemon_two_cards_thread.start()

    pokemon_one_thread.join()
    pokemon_two_thread.join()
    nbp_thread.join()
    pokemon_one_cards_thread.join()
    pokemon_two_cards_thread.join()

    pokemon_one_data = results.get(pokemon_one)
    pokemon_two_data = results.get(pokemon_two)
    eur_value = results.get("eur")
    pokemon_one_cards = results.get(pokemon_one + "_cards")
    pokemon_two_cards = results.get(pokemon_two + "_cards")

    if len(errors) == 0:
        pokemon_one_picture = pokemon_one_data["sprites"]["other"]["home"]["front_default"]
        pokemon_two_picture = pokemon_two_data["sprites"]["other"]["home"]["front_default"]
        total_pokemon_one_cards = pokemon_one_cards["totalCount"]
        total_pokemon_two_cards = pokemon_two_cards["totalCount"]
    else:
        return render_template("results.html", errors=errors)

    pokemon_one_cards_shown = []
    pokemon_two_cards_shown = []
    total_eur_price_pokemon_one = 0
    total_eur_price_pokemon_two = 0
    total_shown_eur_price_pokemon_one = 0
    total_shown_eur_price_pokemon_two = 0
    total_pln_price_pokemon_one = 0
    total_pln_price_pokemon_two = 0
    total_shown_pln_price_pokemon_one = 0
    total_shown_pln_price_pokemon_two = 0

    for i in range(max(total_pokemon_one_cards, total_pokemon_two_cards)):
        if i < min(total_pokemon_one_cards, 250) and i < shown_cards:
            eur_card, pln_card = get_shown_card(i, pokemon_one_cards_shown, eur_value, pokemon_one_cards, True)
            total_shown_eur_price_pokemon_one += eur_card
            total_shown_pln_price_pokemon_one += pln_card

        if i < min(total_pokemon_two_cards, 250) and i < shown_cards:
            eur_card, pln_card = get_shown_card(i, pokemon_two_cards_shown, eur_value, pokemon_two_cards, True)
            total_shown_eur_price_pokemon_two += eur_card
            total_shown_pln_price_pokemon_two += pln_card

        if i < min(total_pokemon_one_cards, 250):
            eur_card, pln_card = get_shown_card(i, pokemon_one_cards_shown, eur_value, pokemon_one_cards, False)
            total_eur_price_pokemon_one += eur_card
            total_pln_price_pokemon_one += pln_card

        if i < min(total_pokemon_two_cards, 250):
            eur_card, pln_card = get_shown_card(i, pokemon_two_cards_shown, eur_value, pokemon_two_cards, False)
            total_eur_price_pokemon_two += eur_card
            total_pln_price_pokemon_two += pln_card

    chart_one = get_chart(pokemon_one, pokemon_two, total_pokemon_one_cards, total_pokemon_two_cards, "total+number+of+cards", errors)
    chart_two = get_chart(pokemon_one, pokemon_two, total_eur_price_pokemon_one, total_eur_price_pokemon_two, "total+price+of+all+cards", errors)

    total_shown_pln_price_pokemon_one = round(total_shown_pln_price_pokemon_one, 2)
    total_shown_pln_price_pokemon_two = round(total_shown_pln_price_pokemon_two, 2)
    total_shown_eur_price_pokemon_one = round(total_shown_eur_price_pokemon_one, 2)
    total_shown_eur_price_pokemon_two = round(total_shown_eur_price_pokemon_one, 2)
    total_eur_price_pokemon_one = round(total_eur_price_pokemon_one, 2)
    total_eur_price_pokemon_two = round(total_eur_price_pokemon_two, 2)
    total_pln_price_pokemon_one = round(total_pln_price_pokemon_one, 2)
    total_pln_price_pokemon_two = round(total_pln_price_pokemon_two, 2)

    return render_template(
                            "results.html",
                            pokemon_one=pokemon_one,
                            pokemon_two=pokemon_two,
                            pokemon_one_picture=pokemon_one_picture,
                            pokemon_two_picture=pokemon_two_picture,
                            shown_cards=shown_cards,
                            pokemon_one_cards_shown=pokemon_one_cards_shown,
                            pokemon_two_cards_shown=pokemon_two_cards_shown,
                            total_shown_eur_price_pokemon_one=total_shown_eur_price_pokemon_one,
                            total_shown_eur_price_pokemon_two=total_shown_eur_price_pokemon_two,
                            total_eur_price_pokemon_one=total_eur_price_pokemon_one,
                            total_eur_price_pokemon_two=total_eur_price_pokemon_two,
                            total_pln_price_pokemon_one=total_pln_price_pokemon_one,
                            total_pln_price_pokemon_two=total_pln_price_pokemon_two,
                            total_shown_pln_price_pokemon_one=total_shown_pln_price_pokemon_one,
                            total_shown_pln_price_pokemon_two=total_shown_pln_price_pokemon_two,
                            chart_one=chart_one,
                            chart_two=chart_two
                           )


@app.errorhandler(404)
def page_not_found(error):
    returned_error = ["The chosen resource was not found, please check the URL used in the request."]
    return render_template("results.html", errors=returned_error)


@app.errorhandler(405)
def wrong_request(error):
    returned_error = ["Chosen endpoint does not support this operation."]
    return render_template("results.html", errors=returned_error)


@app.errorhandler(500)
def internal_error_handler(error):
    returned_error = ["We have run into an internal server error, please try again or check data."]
    return render_template("results.html", errors=returned_error)


@app.errorhandler(HTTPException)
def generic_error_handler(error):
    returned_error = [error]
    return render_template("results.html", errors=returned_error)



if __name__== '__main__':
    app.run(
        host='0.0.0.0',
        port=7776
    )