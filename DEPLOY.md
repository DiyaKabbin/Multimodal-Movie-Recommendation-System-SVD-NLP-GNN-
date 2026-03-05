# 🚀 Deployment Guide — AWS EC2 & GCP VM

---
 
## Prerequisites (both platforms)

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt-get install -y docker-compose-plugin
docker compose version
```

---

## 1. AWS EC2

### 1a. Launch Instance
- AMI: **Ubuntu 22.04 LTS**
- Instance type: **t3.large** (2 vCPU, 8 GB RAM — minimum for FAISS + torch)
- Storage: **30 GB** gp3
- Security Group — open these ports:
  | Port | Purpose |
  |------|---------|
  | 22   | SSH     |
  | 8000 | API     |
  | 80   | HTTP (optional, if you add nginx) |

### 1b. Connect & Deploy

```bash
# SSH in
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Install Docker (see Prerequisites above)

# Upload your project (from your local machine)
scp -i your-key.pem -r ~/MovieReccSystem ubuntu@<EC2_PUBLIC_IP>:~/MovieReccSystem

# On the EC2 instance
cd ~/MovieReccSystem
docker compose up -d --build

# Check everything is running
docker compose ps
docker compose logs -f api
```

### 1c. Test
```bash
curl -X POST http://<EC2_PUBLIC_IP>:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": 0}'
```

### 1d. Auto-restart on reboot
```bash
# Already handled by restart: unless-stopped in docker-compose.yml
# Optionally enable Docker to start on boot:
sudo systemctl enable docker
```

---

## 2. GCP VM (Compute Engine)

### 2a. Create Instance
```bash
# Via gcloud CLI
gcloud compute instances create movierecc-vm \
  --zone=us-central1-a \
  --machine-type=e2-standard-2 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=30GB \
  --tags=movierecc-api
```

### 2b. Open Firewall
```bash
gcloud compute firewall-rules create allow-movierecc-api \
  --allow tcp:8000 \
  --target-tags=movierecc-api \
  --description="Allow Movie Recc API"
```

### 2c. Connect & Deploy
```bash
# SSH in
gcloud compute ssh movierecc-vm --zone=us-central1-a

# Install Docker (see Prerequisites above)

# Upload project (from your local machine)
gcloud compute scp --recurse ~/MovieReccSystem \
  movierecc-vm:~/MovieReccSystem --zone=us-central1-a

# On the VM
cd ~/MovieReccSystem
docker compose up -d --build

# Check logs
docker compose logs -f api
```

### 2d. Test
```bash
# Get external IP
gcloud compute instances describe movierecc-vm \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'

curl -X POST http://<EXTERNAL_IP>:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": 0}'
```

---

## Common Commands (both platforms)

```bash
# Start all services
docker compose up -d

# Rebuild after code changes
docker compose up -d --build

# View logs
docker compose logs -f api
docker compose logs -f postgres

# Stop everything
docker compose down

# Stop and wipe volumes (careful — deletes DB data)
docker compose down -v

# Shell into the API container for debugging
docker compose exec api bash

# Check Redis cache
docker compose exec redis redis-cli ping
docker compose exec redis redis-cli keys "*"
```

---

## Environment Variables

Create a `.env` file in the project root (never commit this):

```env
DATABASE_URL=postgresql://movieuser:moviepass@postgres:5432/moviedb
REDIS_URL=redis://redis:6379/0
ENV=production
```

Then reference it in `docker-compose.yml`:
```yaml
env_file:
  - .env
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Cannot connect to port 8000` | Check security group / firewall rule allows TCP 8000 |
| `Out of memory` | Upgrade to t3.large (AWS) or e2-standard-4 (GCP) |
| `Model files not found` | Ensure volume mounts in docker-compose.yml match your paths |
| `postgres not ready` | The `depends_on: condition: service_healthy` waits automatically |
| `permission denied` | Run `sudo usermod -aG docker $USER && newgrp docker` |
