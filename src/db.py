from sqlalchemy import create_engine
import pandas as pd

# Replace 'YOUR_PASSWORD' with your postgres password
DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost/movierec"

engine = create_engine(DATABASE_URL)

def get_ratings():
    query = "SELECT * FROM ratings"
    return pd.read_sql(query, engine)

def get_movies():
    query = "SELECT * FROM movies"
    return pd.read_sql(query, engine)
