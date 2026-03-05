import pandas as pd
import os
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
import joblib

# ==============================
# 1️⃣ PATH CONFIGURATION
# ==============================

BASE_PATH = "/home/diya_kabbin/MovieReccSystem/data/ml-latest-small"

movies_path = os.path.join(BASE_PATH, "movies.csv")
ratings_path = os.path.join(BASE_PATH, "ratings.csv")

# ==============================
# 2️⃣ LOAD DATA
# ==============================

movies = pd.read_csv(movies_path)
ratings = pd.read_csv(ratings_path)

print("Movies Loaded:", movies.shape)
print("Ratings Loaded:", ratings.shape)

# ==============================
# 3️⃣ CLEAN MOVIES DATA
# ==============================

# Extract release year
movies["release_year"] = movies["title"].str.extract(r"\((\d{4})\)")
movies["release_year"] = pd.to_numeric(
    movies["release_year"], errors="coerce"
).astype("Int64")

# Remove year from title
movies["title"] = movies["title"].str.replace(
    r"\(\d{4}\)", "", regex=True
).str.strip()

# Convert genres into list format
movies["genres"] = movies["genres"].apply(lambda x: x.split("|"))

print("Movies cleaned successfully!")


movie_id_to_title = dict(zip(movies["movieId"], movies["title"]))


# ==============================
# 4️⃣ PREPARE DATA FOR SURPRISE
# ==============================

reader = Reader(rating_scale=(0.5, 5.0))

data = Dataset.load_from_df(
    ratings[["userId", "movieId", "rating"]],
    reader
)

trainset, testset = train_test_split(data, test_size=0.2)

# ==============================
# 5️⃣ TRAIN SVD MODEL
# ==============================

print("Training model...")
model = SVD(
    n_factors=100,
    n_epochs=30,
    lr_all=0.005,
    reg_all=0.02
)
model.fit(trainset)

# ==============================
# 6️⃣ EVALUATE MODEL
# ==============================

predictions = model.test(testset)

rmse = accuracy.rmse(predictions)
print("Model RMSE:", rmse)

# ==============================
# 7️⃣ RECOMMENDATION FUNCTION
# ==============================

def recommend_top_n(model, user_id, movies_df, ratings_df, n=5):

    # Cold start: new user
    if user_id not in ratings_df["userId"].unique():
        print("New user detected. Showing popular movies.")
        popular = (
            ratings_df.groupby("movieId")["rating"]
            .mean()
            .sort_values(ascending=False)
        )
        top_ids = popular.head(n).index
        return movies_df[movies_df["movieId"].isin(top_ids)]["title"].tolist()

    # Movies already rated
    rated_movies = ratings_df[ratings_df["userId"] == user_id]["movieId"].tolist()

    # Unseen movies
    all_movies = movies_df["movieId"].unique()
    unseen_movies = [m for m in all_movies if m not in rated_movies]

    predictions = [model.predict(user_id, movie_id) for movie_id in unseen_movies]
    predictions.sort(key=lambda x: x.est, reverse=True)

    top_predictions = predictions[:n]

    recommended_movies = []
    for pred in top_predictions:
        movie_title = movie_id_to_title[pred.iid]
        recommended_movies.append((movie_title, round(pred.est, 2)))

    return recommended_movies
 



 
# ==============================
# 8️⃣ TEST RECOMMENDATION
# ==============================

user_id = 1
top_movies = recommend_top_n(model, user_id, movies, ratings, n=5)

print(f"\nTop 5 recommendations for User {user_id}:\n")
for movie, score in top_movies:
    print(f"{movie} (Predicted Rating: {score})")

# ==============================
# 9️⃣ SAVE MODEL
# ==============================

os.makedirs("svd", exist_ok=True)
joblib.dump(model, "svd/svd_model.pkl")
print("\nModel saved as svd/svd_model.pkl")




def precision_at_k(predictions, k=5, threshold=3.5):

    from collections import defaultdict

    user_est_true = defaultdict(list)

    # Map predictions to each user
    for uid, iid, true_r, est, _ in predictions:
        user_est_true[uid].append((est, true_r))

    precisions = {}

    for uid, user_ratings in user_est_true.items():

        # Sort by predicted rating
        user_ratings.sort(key=lambda x: x[0], reverse=True)

        # Top K predictions
        top_k = user_ratings[:k]

        # Count relevant items
        n_rel = sum((true_r >= threshold) for (_, true_r) in top_k)

        precisions[uid] = n_rel / k

    return sum(precisions.values()) / len(precisions)



prec_k = precision_at_k(predictions, k=5)
print("Precision@5:", round(prec_k, 4))





import torch
import numpy as np
import os

os.makedirs("svd", exist_ok=True)

# Extract embeddings
user_factors = model.pu      # shape: (num_users, n_factors)
item_factors = model.qi      # shape: (num_items, n_factors)

# Save as tensors
torch.save(torch.tensor(user_factors), "svd/user_svd_embeddings.pt")
torch.save(torch.tensor(item_factors), "svd/movie_svd_embeddings.pt")

print("SVD embeddings exported")
