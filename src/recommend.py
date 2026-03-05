import torch
import faiss
import numpy as np
from hybrid.model import HybridRanker

# ==============================
# Device
# ==============================
device = torch.device("cpu")

# ==============================
# Load Hybrid Model (840-dim)
# ==============================
INPUT_DIM = 840

hybrid_model = HybridRanker(INPUT_DIM)
hybrid_model.load_state_dict(
    torch.load("hybrid/hybrid_ranker.pt", map_location=device)
)
hybrid_model.eval()
print("Hybrid model loaded.")

# ==============================
# Load FAISS Index (384-dim)
# ==============================
faiss_index = faiss.read_index("ir/movie_faiss.index")
print("FAISS index loaded.")
print("Index dimension:", faiss_index.d)

# ==============================
# Load Required Embeddings
# ==============================

# Movie BERT embeddings (384)
movie_bert_embeddings = np.load("embeddings/movie_embeddings.npy")

# User liked movies dictionary
user_liked_movies = torch.load("data/user_movie_dict.pt")

# User SVD embeddings (100)
user_svd_embeddings = torch.load(
    "svd/user_svd_embeddings.pt", map_location=device
)

# Movie SVD embeddings (100)
movie_svd_embeddings = torch.load(
    "svd/movie_svd_embeddings.pt", map_location=device
)

# GNN embeddings (128)
gnn_embeddings = torch.load(
    "gnn/gnn_embeddings.pt", map_location=device
)

# Movie metadata (title list aligned with FAISS index)
import pandas as pd
movies_df = pd.read_csv("data/TMDB_5000_MovieDataset/processed_movies.csv")
movies_df = movies_df.dropna(subset=["text"]).reset_index(drop=True)

print("All embeddings loaded.")
print("Total movies in index:", len(movies_df))


# ==============================
# Recommend Function
# ==============================

def recommend(movie_name: str, user_id: int = None, top_k: int = 10) -> list:
    """
    Given a movie name (and optionally a user_id), return top_k recommendations.

    Steps:
      1. Find the query movie in the dataframe by title match.
      2. Use its BERT embedding to retrieve top candidates via FAISS.
      3. If user_id is provided, re-rank candidates using the Hybrid model.
      4. Return a list of recommended movie titles.
    """

    # ── Step 1: Find query movie ──────────────────────────────────────────────
    title_col = "title" if "title" in movies_df.columns else movies_df.columns[0]

    match = movies_df[
        movies_df[title_col].str.lower() == movie_name.lower()
    ]

    if match.empty:
        # Fuzzy fallback: contains
        match = movies_df[
            movies_df[title_col].str.lower().str.contains(movie_name.lower(), na=False)
        ]

    if match.empty:
        return []

    query_idx = match.index[0]

    # ── Step 2: FAISS retrieval ───────────────────────────────────────────────
    query_vec = movie_bert_embeddings[query_idx].astype("float32").reshape(1, -1)

    # Retrieve more candidates than needed so we can re-rank
    retrieve_k = min(top_k * 5, faiss_index.ntotal)
    distances, candidate_indices = faiss_index.search(query_vec, retrieve_k)
    candidate_indices = candidate_indices[0]

    # Remove the query movie itself
    candidate_indices = [i for i in candidate_indices if i != query_idx]

    if not candidate_indices:
        return []

    # ── Step 3: Hybrid re-ranking (if user_id provided) ──────────────────────
    if user_id is not None and user_id < len(user_svd_embeddings):
        num_users = len(user_svd_embeddings)

        scores = []
        with torch.no_grad():
            for movie_idx in candidate_indices:
                if movie_idx >= len(movie_bert_embeddings):
                    continue

                # Build 840-dim feature vector
                user_gnn = gnn_embeddings[user_id]                          # 128
                movie_gnn = gnn_embeddings[num_users + movie_idx]           # 128
                movie_bert = torch.tensor(
                    movie_bert_embeddings[movie_idx], dtype=torch.float32   # 384
                )
                user_vec = user_svd_embeddings[user_id]                     # 100
                movie_vec = movie_svd_embeddings[movie_idx]                 # 100

                features = torch.cat(
                    [user_gnn, movie_gnn, movie_bert, user_vec, movie_vec], dim=0
                ).unsqueeze(0)  # (1, 840)

                score = hybrid_model(features)
                # Use the "watch" score (index 1) for ranking
                scores.append((movie_idx, score[0][1].item()))

        # Sort by descending score
        scores.sort(key=lambda x: x[1], reverse=True)
        ranked_indices = [idx for idx, _ in scores[:top_k]]

    else:
        # No user context — use FAISS distance order (nearest first)
        ranked_indices = candidate_indices[:top_k]

    # ── Step 4: Return titles ─────────────────────────────────────────────────
    recommendations = []
    for idx in ranked_indices:
        if idx < len(movies_df):
            recommendations.append(movies_df.iloc[idx][title_col])

    return recommendations