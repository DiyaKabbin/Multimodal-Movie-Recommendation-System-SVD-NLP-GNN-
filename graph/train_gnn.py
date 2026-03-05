import torch
import torch.optim as optim
from torch_geometric.nn import LightGCN

# Load graph
checkpoint = torch.load("/home/diya_kabbin/MovieReccSystem/graph/graph_data.pt")

edge_index = checkpoint["edge_index"]
num_users = checkpoint["num_users"]
num_movies = checkpoint["num_movies"]
num_nodes = checkpoint["num_nodes"]

embedding_dim = 128

model = LightGCN(
    num_nodes=num_nodes,
    embedding_dim=embedding_dim,
    num_layers=2
)

optimizer = optim.Adam(model.parameters(), lr=0.005)

def bpr_loss(user_emb, pos_emb, neg_emb):
    pos_score = (user_emb * pos_emb).sum(dim=1)
    neg_score = (user_emb * neg_emb).sum(dim=1)
    return -torch.mean(torch.log(torch.sigmoid(pos_score - neg_score)))

epochs = 50

for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()

    # ✅ Correct method
    embeddings = model.get_embedding(edge_index)

    users = torch.randint(0, num_users, (1024,))
    pos_movies = torch.randint(num_users, num_nodes, (1024,))
    neg_movies = torch.randint(num_users, num_nodes, (1024,))

    user_emb = embeddings[users]
    pos_emb = embeddings[pos_movies]
    neg_emb = embeddings[neg_movies]

    loss = bpr_loss(user_emb, pos_emb, neg_emb)

    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch+1}: Loss {loss.item()}")

# Save model
torch.save(model.state_dict(), "graph/gnn_model.pt")

# Save final embeddings
model.eval()
final_embeddings = model.get_embedding(edge_index).detach()
torch.save(final_embeddings, "graph/gnn_embeddings.pt")

print("GNN training complete")