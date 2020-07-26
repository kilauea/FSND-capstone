from app import db
from sqlalchemy.sql import func

# Define a base model for other database tables to inherit
class Base(db.Model):
    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime, default=func.current_timestamp(), server_default=func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=func.current_timestamp(), server_default=func.current_timestamp(), onupdate=func.current_timestamp())
