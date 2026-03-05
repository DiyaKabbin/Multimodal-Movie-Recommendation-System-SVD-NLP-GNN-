import { useState, useEffect } from "react";

const API_URL = "http://localhost:8000";

const SAMPLE_POSTERS = [
  "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=300&q=80",
  "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=300&q=80",
  "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=300&q=80",
  "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=300&q=80",
  "https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=300&q=80",
  "https://images.unsplash.com/photo-1518676590629-3dcbd9c5a5c9?w=300&q=80",
  "https://images.unsplash.com/photo-1598899134739-24c46f58b8c0?w=300&q=80",
  "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=300&q=80",
  "https://images.unsplash.com/photo-1512070679279-8988d32161be?w=300&q=80",
  "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=300&q=80",
];

const GENRES = ["Thriller", "Drama", "Sci-Fi", "Comedy", "Action", "Romance", "Horror", "Mystery"];

function FilmGrain() {
  return (
    <svg style={{ position: "fixed", top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none", opacity: 0.04, zIndex: 9999 }}>
      <filter id="grain">
        <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch" />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter="url(#grain)" />
    </svg>
  );
}

function MovieCard({ title, index, visible }) {
  const genre = GENRES[index % GENRES.length];
  const rating = (7.2 + (index * 0.3) % 2.6).toFixed(1);
  const year = 2018 + (index % 6);
  const poster = SAMPLE_POSTERS[index % SAMPLE_POSTERS.length];

  return (
    <div style={{
      opacity: visible ? 1 : 0,
      transform: visible ? "translateY(0)" : "translateY(24px)",
      transition: `all 0.5s cubic-bezier(0.22, 1, 0.36, 1) ${index * 60}ms`,
      background: "rgba(255,255,255,0.03)",
      border: "1px solid rgba(255,255,255,0.07)",
      borderRadius: "4px",
      overflow: "hidden",
      cursor: "pointer",
      position: "relative",
    }}
      onMouseEnter={e => {
        e.currentTarget.style.background = "rgba(255,255,255,0.06)";
        e.currentTarget.style.borderColor = "rgba(220,180,100,0.3)";
        e.currentTarget.style.transform = "translateY(-4px)";
      }}
      onMouseLeave={e => {
        e.currentTarget.style.background = "rgba(255,255,255,0.03)";
        e.currentTarget.style.borderColor = "rgba(255,255,255,0.07)";
        e.currentTarget.style.transform = "translateY(0)";
      }}
    >
      {/* Poster */}
      <div style={{ height: "180px", overflow: "hidden", position: "relative" }}>
        <img src={poster} alt={title}
          style={{ width: "100%", height: "100%", objectFit: "cover", filter: "brightness(0.75) saturate(0.8)" }} />
        <div style={{
          position: "absolute", inset: 0,
          background: "linear-gradient(to top, rgba(8,8,12,0.95) 0%, transparent 50%)"
        }} />
        {/* Rating badge */}
        <div style={{
          position: "absolute", top: "10px", right: "10px",
          background: "rgba(220,180,100,0.9)", color: "#0a0a0e",
          fontSize: "11px", fontWeight: "700", padding: "3px 7px",
          borderRadius: "2px", fontFamily: "'Courier New', monospace",
          letterSpacing: "0.05em"
        }}>
          ★ {rating}
        </div>
      </div>

      {/* Info */}
      <div style={{ padding: "14px 16px 16px" }}>
        <div style={{
          fontSize: "11px", color: "rgba(220,180,100,0.7)",
          fontFamily: "'Courier New', monospace",
          letterSpacing: "0.15em", textTransform: "uppercase",
          marginBottom: "6px"
        }}>
          {genre} · {year}
        </div>
        <div style={{
          fontSize: "14px", fontWeight: "600", color: "rgba(255,255,255,0.9)",
          fontFamily: "'Georgia', serif", lineHeight: "1.3",
          letterSpacing: "0.01em"
        }}>
          {title}
        </div>
      </div>

      {/* Rank number */}
      <div style={{
        position: "absolute", top: "10px", left: "10px",
        fontSize: "11px", fontFamily: "'Courier New', monospace",
        color: "rgba(255,255,255,0.4)", fontWeight: "700",
        letterSpacing: "0.1em"
      }}>
        #{String(index + 1).padStart(2, "0")}
      </div>
    </div>
  );
}

function LoadingReel() {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "20px", padding: "60px 0" }}>
      <div style={{ display: "flex", gap: "8px" }}>
        {[0,1,2,3,4].map(i => (
          <div key={i} style={{
            width: "10px", height: "10px",
            borderRadius: "50%",
            background: "rgba(220,180,100,0.8)",
            animation: `pulse 1.2s ease-in-out ${i * 0.15}s infinite`,
          }} />
        ))}
      </div>
      <div style={{
        fontFamily: "'Courier New', monospace",
        fontSize: "12px", letterSpacing: "0.2em",
        color: "rgba(255,255,255,0.3)", textTransform: "uppercase"
      }}>
        Running recommendation engine
      </div>
      <style>{`
        @keyframes pulse {
          0%, 80%, 100% { transform: scale(0.6); opacity: 0.3; }
          40% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </div>
  );
}

export default function App() {
  const [userId, setUserId] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [cardsVisible, setCardsVisible] = useState(false);
  const [headerVisible, setHeaderVisible] = useState(false);

  useEffect(() => {
    setTimeout(() => setHeaderVisible(true), 100);
  }, []);

  const handleSubmit = async () => {
    const id = parseInt(userId);
    if (isNaN(id) || id < 0) {
      setError("Enter a valid user ID (0–609)");
      return;
    }

    setError("");
    setLoading(true);
    setRecommendations([]);
    setCardsVisible(false);

    try {
      const res = await fetch(`${API_URL}/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: id }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Something went wrong");
      } else {
        setRecommendations(data.recommendations);
        setTimeout(() => setCardsVisible(true), 100);
      }
    } catch (e) {
      setError("Cannot connect to API. Is the server running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#08080c",
      color: "white",
      fontFamily: "'Georgia', serif",
    }}>
      <FilmGrain />

      {/* Ambient background glow */}
      <div style={{
        position: "fixed", top: "-20%", left: "50%", transform: "translateX(-50%)",
        width: "600px", height: "400px",
        background: "radial-gradient(ellipse, rgba(180,120,40,0.08) 0%, transparent 70%)",
        pointerEvents: "none",
      }} />

      <div style={{ maxWidth: "1100px", margin: "0 auto", padding: "0 32px" }}>

        {/* Header */}
        <header style={{
          padding: "64px 0 48px",
          opacity: headerVisible ? 1 : 0,
          transform: headerVisible ? "translateY(0)" : "translateY(-16px)",
          transition: "all 0.8s cubic-bezier(0.22, 1, 0.36, 1)",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          marginBottom: "56px",
          display: "flex", alignItems: "flex-end", justifyContent: "space-between",
          flexWrap: "wrap", gap: "24px"
        }}>
          <div>
            <div style={{
              fontFamily: "'Courier New', monospace",
              fontSize: "10px", letterSpacing: "0.4em",
              color: "rgba(220,180,100,0.6)", textTransform: "uppercase",
              marginBottom: "12px"
            }}>
              ◆ Hybrid Neural Recommendation Engine
            </div>
            <h1 style={{
              fontSize: "clamp(36px, 6vw, 64px)",
              fontWeight: "400", margin: 0,
              letterSpacing: "-0.02em", lineHeight: "1",
              color: "rgba(255,255,255,0.95)"
            }}>
              CINEMATCH
            </h1>
            <div style={{
              fontSize: "13px", color: "rgba(255,255,255,0.3)",
              marginTop: "10px", fontFamily: "'Courier New', monospace",
              letterSpacing: "0.05em"
            }}>
              GNN · SVD · BERT · FAISS
            </div>
          </div>

          {/* Status indicator */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div style={{
              width: "6px", height: "6px", borderRadius: "50%",
              background: "#4ade80",
              boxShadow: "0 0 8px #4ade80",
              animation: "breathe 2s ease-in-out infinite"
            }} />
            <span style={{
              fontFamily: "'Courier New', monospace",
              fontSize: "11px", color: "rgba(255,255,255,0.35)",
              letterSpacing: "0.1em"
            }}>
              API ONLINE
            </span>
          </div>
        </header>

        {/* Search */}
        <div style={{
          opacity: headerVisible ? 1 : 0,
          transform: headerVisible ? "translateY(0)" : "translateY(16px)",
          transition: "all 0.8s cubic-bezier(0.22, 1, 0.36, 1) 0.15s",
          marginBottom: "64px",
        }}>
          <div style={{
            fontSize: "11px", fontFamily: "'Courier New', monospace",
            letterSpacing: "0.2em", color: "rgba(255,255,255,0.3)",
            textTransform: "uppercase", marginBottom: "16px"
          }}>
            User Identification
          </div>

          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
            <div style={{ position: "relative", flex: "1", minWidth: "240px", maxWidth: "360px" }}>
              <input
                type="number"
                placeholder="Enter user ID  (0 – 609)"
                value={userId}
                onChange={e => { setUserId(e.target.value); setError(""); }}
                onKeyDown={e => e.key === "Enter" && handleSubmit()}
                style={{
                  width: "100%", padding: "14px 18px",
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "3px", color: "rgba(255,255,255,0.85)",
                  fontSize: "14px", outline: "none",
                  fontFamily: "'Courier New', monospace",
                  letterSpacing: "0.05em", boxSizing: "border-box",
                  transition: "border-color 0.2s",
                }}
                onFocus={e => e.target.style.borderColor = "rgba(220,180,100,0.4)"}
                onBlur={e => e.target.style.borderColor = "rgba(255,255,255,0.1)"}
              />
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading}
              style={{
                padding: "14px 32px",
                background: loading ? "rgba(220,180,100,0.2)" : "rgba(220,180,100,0.9)",
                border: "none", borderRadius: "3px",
                color: loading ? "rgba(220,180,100,0.5)" : "#0a0a0e",
                fontSize: "12px", fontWeight: "700",
                fontFamily: "'Courier New', monospace",
                letterSpacing: "0.2em", textTransform: "uppercase",
                cursor: loading ? "not-allowed" : "pointer",
                transition: "all 0.2s",
                whiteSpace: "nowrap",
              }}
              onMouseEnter={e => { if (!loading) e.target.style.background = "rgba(220,180,100,1)"; }}
              onMouseLeave={e => { if (!loading) e.target.style.background = "rgba(220,180,100,0.9)"; }}
            >
              {loading ? "Searching..." : "Get Recommendations →"}
            </button>
          </div>

          {error && (
            <div style={{
              marginTop: "12px", fontSize: "12px",
              color: "rgba(255,100,100,0.8)",
              fontFamily: "'Courier New', monospace",
              letterSpacing: "0.05em"
            }}>
              ✗ {error}
            </div>
          )}
        </div>

        {/* Results */}
        {loading && <LoadingReel />}

        {!loading && recommendations.length > 0 && (
          <div>
            <div style={{
              display: "flex", alignItems: "baseline",
              justifyContent: "space-between", marginBottom: "28px",
              flexWrap: "wrap", gap: "8px"
            }}>
              <div style={{
                fontSize: "11px", fontFamily: "'Courier New', monospace",
                letterSpacing: "0.2em", color: "rgba(255,255,255,0.3)",
                textTransform: "uppercase"
              }}>
                Recommended for User #{userId}
              </div>
              <div style={{
                fontSize: "11px", fontFamily: "'Courier New', monospace",
                color: "rgba(220,180,100,0.5)", letterSpacing: "0.1em"
              }}>
                {recommendations.length} titles selected
              </div>
            </div>

            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
              gap: "16px",
            }}>
              {recommendations.map((title, i) => (
                <MovieCard key={i} title={title} index={i} visible={cardsVisible} />
              ))}
            </div>

            <div style={{
              marginTop: "48px", paddingTop: "24px",
              borderTop: "1px solid rgba(255,255,255,0.05)",
              display: "flex", justifyContent: "space-between",
              flexWrap: "wrap", gap: "8px"
            }}>
              <span style={{
                fontFamily: "'Courier New', monospace",
                fontSize: "10px", color: "rgba(255,255,255,0.2)",
                letterSpacing: "0.15em"
              }}>
                CINEMATCH · HYBRID NEURAL ENGINE
              </span>
              <span style={{
                fontFamily: "'Courier New', monospace",
                fontSize: "10px", color: "rgba(255,255,255,0.2)",
                letterSpacing: "0.1em"
              }}>
                TMDB · ML-LATEST-SMALL DATASET
              </span>
            </div>
          </div>
        )}

        {!loading && recommendations.length === 0 && !error && (
          <div style={{
            textAlign: "center", padding: "80px 0",
            color: "rgba(255,255,255,0.12)",
          }}>
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>◈</div>
            <div style={{
              fontFamily: "'Courier New', monospace",
              fontSize: "12px", letterSpacing: "0.3em",
              textTransform: "uppercase"
            }}>
              Enter a user ID to begin
            </div>
          </div>
        )}
      </div>

      <style>{`
        * { box-sizing: border-box; }
        body { margin: 0; }
        input[type=number]::-webkit-inner-spin-button { -webkit-appearance: none; }
        @keyframes breathe {
          0%, 100% { opacity: 0.6; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.3); }
        }
      `}</style>
    </div>
  );
}