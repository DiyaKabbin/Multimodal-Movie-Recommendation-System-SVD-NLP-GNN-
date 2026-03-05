import torch
import pandas as pd
import numpy as np

class HybridDataset(torch.utils.data.Dataset):

    def __init__(self):

        # Load embeddings
        self.gnn_embeddings = torch.load("graph/gnn_embeddings.pt")
        self.movie_bert = np.load("embeddings/movie_embeddings.npy")

        self.user_svd = torch.load("svd/user_svd_embeddings.pt")
        self.movie_svd = torch.load("svd/movie_svd_embeddings.pt")

        print("SVD embeddings loaded")
        print("User SVD shape:", self.user_svd.shape)
        print("Movie SVD shape:", self.movie_svd.shape)

        # Load ratings
        self.ratings = pd.read_csv("data/ml-latest-small/ratings.csv")
        self.num_users = self.ratings['userId'].nunique()


        # Unique users and movies
        unique_users = sorted(self.ratings['userId'].unique())
        unique_movies = sorted(self.ratings['movieId'].unique())

        # Create mapping
        self.user2idx = {uid: i for i, uid in enumerate(unique_users)}
        self.movie2idx = {mid: i for i, mid in enumerate(unique_movies)}

        self.num_users = len(unique_users)

        print("Max user idx:", max(self.user2idx.values()))
        print("Max movie idx:", max(self.movie2idx.values()))
        print("GNN size:", self.gnn_embeddings.shape)






    def __len__(self):
        return len(self.ratings)

    def __getitem__(self, idx):

        row = self.ratings.iloc[idx]

        # Convert to 0-based index
        user = self.user2idx[row['userId']]
        movie = self.movie2idx[row['movieId']]

        rating = row['rating']

        # Labels
        click = 1 if rating >= 3 else 0
        watch = 1 if rating >= 4 else 0

        # -------- Embeddings --------

        # GNN
        user_gnn = self.gnn_embeddings[user]
        movie_gnn = self.gnn_embeddings[self.num_users + movie]

        # BERT
        # BERT (safe lookup)
        if movie < len(self.movie_bert):
            movie_bert = torch.tensor(self.movie_bert[movie], dtype=torch.float32)
        else:
            movie_bert = torch.zeros(self.movie_bert.shape[1])

        # SVD embeddings
        if user < len(self.user_svd):
            user_vec = self.user_svd[user]
        else:
            user_vec = torch.zeros(self.user_svd.shape[1])
            
        # SVD movie (safe lookup)
        if movie < len(self.movie_svd):
            movie_vec = self.movie_svd[movie]
        else:
            movie_vec = torch.zeros(self.movie_svd.shape[1])

        # -------- Concatenate --------

        features = torch.cat([
            user_gnn,
            movie_gnn,
            movie_bert,
            user_vec,
            movie_vec
        ], dim=0)

        label = torch.tensor([click, watch], dtype=torch.float32)

        return features.float(), label



