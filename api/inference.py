import torch
import faiss
import numpy as np
import pandas as pd

# -----------------------------------
# Load FAISS (384-dim movie index)
# -----------------------------------
faiss_index = faiss.read_index("ir/movie_faiss.index")
print("FAISS index dimension:", faiss_index.d)

# -----------------------------------
# Load movie BERT embeddings (384-dim)
# -----------------------------------
movie_bert_embeddings = np.load("embeddings/movie_embeddings.npy")

# -----------------------------------
# Load user SVD embeddings (100-dim)
# -----------------------------------
user_svd_embeddings = torch.load(
    "svd/user_svd_embeddings.pt",
    map_location="cpu"
)

# -----------------------------------
# Load movie SVD embeddings (100-dim)
# -----------------------------------
movie_svd_embeddings = torch.load(
    "svd/movie_svd_embeddings.pt",
    map_location="cpu"
)

# -----------------------------------
# Load GNN embeddings (128-dim each,
# first num_users rows = users,
# remaining rows = movies)
# -----------------------------------
gnn_embeddings = torch.load(
    "graph/gnn_embeddings.pt",
    map_location="cpu"
)
num_users = user_svd_embeddings.shape[0]

# -----------------------------------
# Load user → liked movies dict
# (used to pick a seed movie for FAISS)
# -----------------------------------
user_liked_movies = torch.load("data/user_movie_dict.pt")

# -----------------------------------
# Load movie titles
# -----------------------------------
movies_df = pd.read_csv(
    "data/TMDB_5000_MovieDataset/processed_movies.csv"
).dropna(subset=["text"]).reset_index(drop=True)

title_col = "title" if "title" in movies_df.columns else movies_df.columns[0]

# -----------------------------------
# Load Hybrid model (840-dim input)
# 840 = 128 user_gnn + 128 movie_gnn
#     + 384 movie_bert
#     + 100 user_svd + 100 movie_svd
# -----------------------------------
from hybrid.model import HybridRanker

INPUT_DIM = 840
hybrid_model = HybridRanker(INPUT_DIM)
hybrid_model.load_state_dict(
    torch.load("hybrid/hybrid_ranker.pt", map_location="cpu")
)
hybrid_model.eval()

print("✅ inference.py loaded successfully.")


# -----------------------------------
# Helper: pick a seed BERT vector for
# FAISS from the user's liked movies
# -----------------------------------
def _get_user_seed_vector(user_id: int) -> np.ndarray:
    """
    Average the BERT embeddings of movies the user liked
    to create a 384-dim query vector for FAISS retrieval.
    Falls back to a zero vector if nothing is found.
    """
    liked = user_liked_movies.get(user_id, [])

    valid_vecs = []
    for mid in liked:
        if mid < len(movie_bert_embeddings):
            valid_vecs.append(movie_bert_embeddings[mid])

    if valid_vecs:
        seed = np.mean(valid_vecs, axis=0).astype("float32")
    else:
        seed = np.zeros(faiss_index.d, dtype="float32")

    return seed.reshape(1, -1)


# -----------------------------------
# Main recommendation function
# -----------------------------------
def get_top10(user_id: int):
    """
    Returns a list of 10 recommended movie titles for the given user_id.
    """

    # ── 1. Build 384-dim seed vector for FAISS ──────────────────────────────
    seed_vector = _get_user_seed_vector(user_id)   # (1, 384)

    # ── 2. FAISS retrieval — get 100 candidate movie indices ─────────────────
    _, candidate_ids = faiss_index.search(seed_vector, 100)
    candidate_ids = candidate_ids[0]               # shape (100,)

    # ── 3. Build 840-dim features and score each candidate ───────────────────
    user_gnn = gnn_embeddings[user_id]             # (128,)
    user_svd = user_svd_embeddings[user_id]        # (100,)

    scores = []

    with torch.no_grad():
        for movie_idx in candidate_ids:
            if movie_idx < 0 or movie_idx >= len(movie_bert_embeddings):
                continue

            movie_gnn  = gnn_embeddings[num_users + movie_idx]          # (128,)
            movie_bert = torch.tensor(
                movie_bert_embeddings[movie_idx], dtype=torch.float32   # (384,)
            )
            movie_svd  = movie_svd_embeddings[movie_idx]                # (100,)

            # 128 + 128 + 384 + 100 + 100 = 840 ✅
            features = torch.cat([
                user_gnn.float(),
                movie_gnn.float(),
                movie_bert.float(),
                user_svd.float(),
                movie_svd.float()
            ], dim=0).unsqueeze(0)                                      # (1, 840)

            score = hybrid_model(features)
            # score shape depends on HybridRanker output:
            # if (1, 2): use watch score (index 1)
            # if (1, 1) or scalar: use directly
            if score.ndim > 1 and score.shape[1] >= 2:
                s = score[0][1].item()
            else:
                s = score.squeeze().item()

            scores.append((movie_idx, s))

    # ── 4. Sort descending and return top-10 titles ───────────────────────────
    ranked = sorted(scores, key=lambda x: x[1], reverse=True)

    top10_titles = []
    for movie_idx, _ in ranked[:10]:
        if movie_idx < len(movies_df):
            top10_titles.append(movies_df.iloc[movie_idx][title_col])
        else:
            top10_titles.append(f"movie_{movie_idx}")

    return top10_titles