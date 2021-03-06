from models import db
from app import app

# Create tables for app
db.drop_all()
db.create_all()