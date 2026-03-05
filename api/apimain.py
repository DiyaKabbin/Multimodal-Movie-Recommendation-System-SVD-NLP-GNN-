from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import time
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app

from api.inference import get_top10

app = FastAPI(title="Movie Recommendation API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

REQUEST_COUNT = Counter("movierecc_requests_total", "Total requests", ["endpoint", "status"])
REQUEST_LATENCY = Histogram("movierecc_request_latency_seconds", "Latency", ["endpoint"])
ACTIVE_USERS = Gauge("movierecc_active_users_total", "Users in memory")

device = torch.device("cpu")
try:
    user_embeddings = torch.load("svd/user_svd_embeddings.pt", map_location=device)
    num_users = user_embeddings.shape[0]
    ACTIVE_USERS.set(num_users)
    print("✅ Server started successfully.")
    print("Total users:", num_users)
except Exception as e:
    print("❌ Failed to load user embeddings:", e)
    num_users = 0

class RecommendRequest(BaseModel):
    user_id: int

@app.post("/recommend")
def recommend(req: RecommendRequest):
    start = time.time()
    if req.user_id < 0 or req.user_id >= num_users:
        REQUEST_COUNT.labels(endpoint="/recommend", status="400").inc()
        raise HTTPException(status_code=400, detail=f"user_id must be between 0 and {num_users - 1}")
    try:
        top10 = get_top10(req.user_id)
        REQUEST_COUNT.labels(endpoint="/recommend", status="200").inc()
        REQUEST_LATENCY.labels(endpoint="/recommend").observe(time.time() - start)
        return {"user_id": req.user_id, "recommendations": top10}
    except Exception as e:
        REQUEST_COUNT.labels(endpoint="/recommend", status="500").inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health():
    return {"status": "running", "total_users": num_users}
