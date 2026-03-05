from flask import Flask, request, jsonify
from src.recommend import recommend

# ==============================
# Initialize Flask
# ==============================
app = Flask(__name__)

# ==============================
# Flask endpoint
# ==============================
@app.route("/recommend", methods=["POST"])
def recommend_movie():
    data = request.json

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    movie_name = data.get("movie")
    user_id = data.get("user_id", None)   # optional
    top_k = int(data.get("top_k", 10))

    if not movie_name:
        return jsonify({"error": "Please provide a 'movie' field"}), 400

    try:
        recommendations = recommend(
            movie_name=movie_name,
            user_id=user_id,
            top_k=top_k
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if not recommendations:
        return jsonify({
            "movie": movie_name,
            "recommendations": [],
            "message": "No matching movie found or no recommendations available."
        }), 404

    return jsonify({
        "movie": movie_name,
        "user_id": user_id,
        "recommendations": recommendations
    })


# ==============================
# Run Flask
# ==============================
if __name__ == "__main__":
    app.run(debug=True)