"""Models for the Hearthstone Deck Randomizer"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    """Connect your app to the database."""
    
    db.app = app
    db.init_app(app)

class Deck(db.Model):
    """Deck"""

    __tablename__ = "decks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deck_name = db.Column(db.String(50), nullable=False)
    deck_class = db.Column(db.String(12), nullable=False)

    cards = db.relationship('Card', secondary='deck_cards', backref='decks')

    @classmethod
    def add_deck(cls, deck_name, deck_class):
        """Create a deck instance and add the deck to the db session"""

        deck = cls(deck_name=deck_name, deck_class=deck_class)

        db.session.add(deck)
        db.session.commit()
        return deck
        

class Card(db.Model):
    """Card"""

    __tablename__ = "cards"

    id = db.Column(db.Integer, autoincrement=True)
    hearthstone_id = db.Column(db.String(20), primary_key=True, nullable=False)
    image = db.Column(db.String(1000), nullable=False)


class DeckCards(db.Model):
    """Mapping of a deck to a card"""

    __tablename__ = "deck_cards"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.id"), nullable=False)
    card_id = db.Column(db.String(20), db.ForeignKey("cards.hearthstone_id"), nullable=False)


def get_or_create_card(hearthstone_id, image):
        """Create a card and add the card to the session but do not commit."""

        card = Card.query.filter_by(hearthstone_id=hearthstone_id).first()
        if card:
            return card
        else:
            card = Card(hearthstone_id=hearthstone_id, image=image)
            db.session.add(card)
            return card