import pandas as pd
import ast

# Load datasets
movies = pd.read_csv("/home/diya_kabbin/MovieReccSystem/data/TMDB_5000_MovieDataset/tmdb_5000_movies.csv")
credits = pd.read_csv("/home/diya_kabbin/MovieReccSystem/data/TMDB_5000_MovieDataset/tmdb_5000_credits.csv")

# Rename for merge
credits.rename(columns={"movie_id": "id"}, inplace=True)

# Ensure same type
movies["id"] = movies["id"].astype(str)
credits["id"] = credits["id"].astype(str)

# Merge
df = movies.merge(credits.drop(columns=["title"]), on="id")


# ---------- JSON CLEANING ----------
def clean_json_column(x):
    try:
        items = ast.literal_eval(x)
        return " ".join([i["name"] for i in items])
    except:
        return ""

# Extract top 3 cast
def extract_cast(x):
    try:
        items = ast.literal_eval(x)
        return " ".join([i["name"] for i in items[:3]])
    except:
        return ""

# Extract director
def extract_director(x):
    try:
        items = ast.literal_eval(x)
        for i in items:
            if i["job"] == "Director":
                return i["name"]
        return ""
    except:
        return ""

# Clean columns
df["genres"] = df["genres"].apply(clean_json_column)
df["keywords"] = df["keywords"].apply(clean_json_column)
df["cast"] = df["cast"].apply(extract_cast)
df["director"] = df["crew"].apply(extract_director)

df["overview"] = df["overview"].fillna("")
df["tagline"] = df["tagline"].fillna("")

# Create final text
df["text"] = (
    df["overview"] + " " +
    df["genres"] + " " +
    df["keywords"] + " " +
    df["cast"] + " " +
    df["director"] + " " +
    df["tagline"]
)

df = df.head(5000)


import re

def clean_text(text):
    text = str(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

df["text"] = df["text"].apply(clean_text)

df = df[["id", "title", "text"]]
df = df.drop_duplicates(subset="title")
df = df.reset_index(drop=True)

df.to_csv("/home/diya_kabbin/MovieReccSystem/data/TMDB_5000_MovieDataset/processed_movies.csv", index=False)