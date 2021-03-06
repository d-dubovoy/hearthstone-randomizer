import os
from unittest import TestCase

from models import Deck, Card, DeckCards, connect_db, db
from flask import session

os.environ['DATABASE_URL'] = "postgresql:///hearthstone-randomizer-test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class RandomizerTestCases(TestCase):
    """Test the randomizer app"""

    def test_randomizer_view(self):
        with app.test_client() as client:
            resp = client.get("/randomizer")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4>Your previously created decks:</h4>', html)
    
    def test_randomizer_function(self):
        with app.test_client() as client:
            # Set session to empty list
            with client.session_transaction() as set_session:
                set_session['user_decks'] = []

            resp = client.post('/randomizer', 
                data={"deck_name": "Test Name", 
                "deck_class": "mage"})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="text-center container">Test Name</h1>', html)
            # Test writing to session
            self.assertEqual(len(session['user_decks']), 1)

    def test_redirect(self):
        with app.test_client() as client:
            resp = client.get("/")

            self.assertEqual(resp.status_code, 302)

    def test_deck_details(self):
        with app.test_client() as client:
            with client.session_transaction() as set_session:
                set_session['user_decks'] = []
                set_session['user_decks'].append(1)

            resp = client.get("/decks/1")

            self.assertEqual(resp.status_code, 200)      
