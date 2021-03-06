from flask import Flask, render_template, redirect, flash, request, url_for, session
import requests
import random
from models import Deck, DeckCards, Card, connect_db, db, get_or_create_card
from forms import RandomizerForm
import os

app = Flask(__name__)


app.config['SECRET_KEY'] = #


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hearthstone_randomizer'



app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

url = "https://omgvamp-hearthstone-v1.p.rapidapi.com/cards"

headers = {
    #
}

querystring = {"locale":"enUS","collectible":"1"}


##############################################################################
# Routes

@app.route("/")
def root():
    """Root directory, redirect to randomizer."""
    
    return redirect(url_for("randomizer"))

@app.route("/randomizer", methods=["GET", "POST"])
def randomizer():
    """Randomizer app route"""

    form = RandomizerForm()

    deck_display = []

    if 'user_decks' not in session:
        session['user_decks'] = []

    if 'user_decks' in session:
        for item in session['user_decks']:
            add_item = Deck.query.get(item)
            deck_display.append(add_item)

    if form.validate_on_submit():
        deck_name = form.deck_name.data
        deck_class = form.deck_class.data

        deck = Deck.add_deck(deck_name, deck_class)
        # returns deck item from Models.py, already committed to database

        deck_id = deck.id        

        # sending get request and saving the response as response object 
        r = requests.get(url=url, params=querystring, headers=headers)

        data = r.json()

        # returns the completed deck
        final_deck = create_random_deck(data=data, deck_id=deck_id, deck_class=deck_class)

        flash("Random Deck Created!", "success")

        return render_template("result.html", final_deck=final_deck, deck_name=deck_name)
    else:
        return render_template("randomizer.html", form=form, deck_display=deck_display)


@app.route("/decks/<int:deck_id>", methods=["GET"])
def deck_view(deck_id):
    """Display a particular deck that a user has created previously."""
    
    # prevent jumping to a deck that a user did not create via the deck id
    if 'user_decks' in session:
        if deck_id not in session['user_decks']:
            flash("Access Denied.", "danger")
            return redirect(url_for("randomizer"))
    else: 
        return redirect(url_for("randomizer"))

    card_query = DeckCards.query.filter_by(deck_id=deck_id).all()

    cards_list = []

    for item in card_query:
        add_item = Card.query.get(item.card_id)
        cards_list.append(add_item.image)

    name = Deck.query.filter_by(id=deck_id).first()

    return render_template("deck_details.html", cards_list=cards_list, name=name)

@app.route("/decks/<int:deck_id>/delete", methods=["GET"])
def session_remove_deck(deck_id):
    """Remove a deck from the user's session but not the database."""

    session_decks = session['user_decks']

    if 'user_decks' in session:
        session_decks = session['user_decks']
        for item in session_decks:

            if item == deck_id:
                session_decks.remove(item)
                session['user_decks'] = session_decks

                return redirect(url_for("randomizer"))
            else:
                pass
            
    else: 
        return redirect(url_for("randomizer"))

##############################################################################
# Random deck logic 
   
def create_random_deck(data, deck_id, deck_class):
    """Picks random cards from list of all cards using user-selected parameters."""

    valid_card_list = []

    for set_name, set_cards in data.items():
        for item in set_cards:
            # filter out the hero cards from each card set and add the card to a new valid card list
            if item["type"] != "Hero" and any([item["playerClass"] == deck_class.capitalize(), item["playerClass"] == "Neutral"]):
                valid_card_list.append(item)

    # select 30 random cards from the deck
    random_deck = random.sample(valid_card_list, k=30)

    # use random_deck object to store card IDs and img urls in the database to retrieve later
    for card in random_deck:
        get_or_create_card(hearthstone_id=card["cardId"], image=card["img"])
    db.session.commit()

    # create the relational link in the DeckCards table
    for card_ in random_deck:
        deck_cards = DeckCards(deck_id=deck_id, card_id=card_["cardId"])
        db.session.add(deck_cards)
    db.session.commit()

    #add the deck_id to the user's session
    if 'user_decks' not in session:
        session['user_decks'] = []
    user_decks = session['user_decks']
    user_decks.append(deck_id)
    session['user_decks'] = user_decks

    return random_deck