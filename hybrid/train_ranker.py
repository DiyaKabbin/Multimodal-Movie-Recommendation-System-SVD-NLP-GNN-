import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from hybrid.dataset import HybridDataset
from hybrid.model import HybridRanker

dataset = HybridDataset()
loader = DataLoader(dataset, batch_size=256, shuffle=True)

sample_input, _ = dataset[0]
input_dim = sample_input.shape[0]

model = HybridRanker(input_dim)
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.BCELoss()

epochs = 5

for epoch in range(epochs):
    total_loss = 0

    for features, labels in loader:
        optimizer.zero_grad()

        outputs = model(features)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}, Loss: {total_loss}")

torch.save(model.state_dict(), "hybrid/hybrid_ranker.pt")
print("Hybrid model trained and saved.")




if __name__ == "__main__": 
    train()