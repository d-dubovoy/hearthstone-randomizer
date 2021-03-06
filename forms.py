"""Forms for Hearthstone deck randomizer."""

from wtforms import StringField, SelectField
from wtforms.validators import InputRequired, Length
from flask_wtf import FlaskForm

class RandomizerForm(FlaskForm):
    """Main form for submitting a randomizer request."""

    deck_name = StringField("Deck Name", validators=[InputRequired(), Length(min=4, max=50)])

    deck_class = SelectField("Select A Class", choices=[
        ('druid', 'Druid'), ('hunter', 'Hunter'), ('mage', 'Mage'),
        ('paladin', 'Paladin'), ('priest', 'Priest'), ('rogue', 'Rogue'),
        ('shaman', 'Shaman'), ('warlock', 'Warlock'), ('warrior', 'Warrior')],
        validators=[InputRequired()])

