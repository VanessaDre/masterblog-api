from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route("/api/posts", methods=["GET"])
def get_posts():
    sort_field = request.args.get("sort")
    direction = request.args.get("direction", "asc")

    if not sort_field:
        return jsonify(POSTS), 200

    if sort_field not in ("title", "content"):
        return jsonify({"error": "Invalid sort field. Allowed: title, content."}), 400

    if direction not in ("asc", "desc"):
        return jsonify({"error": "Invalid direction. Allowed: asc, desc."}), 400

    reverse = direction == "desc"

    sorted_posts = sorted(
        POSTS,
        key=lambda p: (p.get(sort_field) or "").lower(),
        reverse=reverse
    )
    return jsonify(sorted_posts), 200


@app.route("/api/posts", methods=["POST"])
def add_post():
    data = request.get_json(force=True, silent=True) or {}

    missing = []
    if not data.get("title"):
        missing.append("title")
    if not data.get("content"):
        missing.append("content")

    if missing:
        return jsonify(
            {"error": "Missing required field(s)", "missing_fields": missing}
        ), 400

    new_id = max((p["id"] for p in POSTS), default=0) + 1
    new_post = {"id": new_id, "title": data["title"], "content": data["content"]}
    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    global POSTS

    post = next((p for p in POSTS if p["id"] == post_id), None)
    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    POSTS = [p for p in POSTS if p["id"] != post_id]
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    data = request.get_json(silent=True) or {}

    # title/content sind optional: wenn nicht vorhanden, alte Werte behalten
    if "title" in data and data["title"] is not None:
        post["title"] = data["title"]
    if "content" in data and data["content"] is not None:
        post["content"] = data["content"]

    return jsonify(post), 200


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    title_q = (request.args.get("title") or "").strip().lower()
    content_q = (request.args.get("content") or "").strip().lower()

    results = POSTS

    if title_q:
        results = [p for p in results if title_q in (p.get("title", "").lower())]

    if content_q:
        results = [p for p in results if content_q in (p.get("content", "").lower())]

    return jsonify(results), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
