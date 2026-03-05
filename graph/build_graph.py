import pandas as pd
import torch
from torch_geometric.data import Data
import os

BASE_PATH = "/home/diya_kabbin/MovieReccSystem/data/ml-latest-small"
ratings_path = os.path.join(BASE_PATH, "ratings.csv")

ratings = pd.read_csv(ratings_path)

# Unique IDs
unique_users = ratings['userId'].unique()
unique_movies = ratings['movieId'].unique()

user_id_map = {id: idx for idx, id in enumerate(unique_users)}
movie_id_map = {
    id: idx + len(unique_users)
    for idx, id in enumerate(unique_movies)
}

num_users = len(unique_users)
num_movies = len(unique_movies)
num_nodes = num_users + num_movies

edges = []

for _, row in ratings.iterrows():
    u = user_id_map[row['userId']]
    m = movie_id_map[row['movieId']]
    edges.append([u, m])
    edges.append([m, u])

edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()

data = Data(edge_index=edge_index)
data.num_nodes = num_nodes

torch.save({
    "edge_index": edge_index,
    "num_users": num_users,
    "num_movies": num_movies,
    "num_nodes": num_nodes
}, "graph/graph_data.pt")

print("Graph built successfully")