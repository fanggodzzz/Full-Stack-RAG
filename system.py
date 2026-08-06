from flask import Flask, jsonify, render_template, request
import rag

app = Flask(__name__, template_folder="UI", static_folder="UI")
rag.init()  # Initialize the RAG system before handling any requests

def process_query(user_query: str) -> str:
    response = rag.querying(user_query)
    model = "w2v"  # Change this to "bm25" or "hybrid" to get responses from those models
    print(f"Returning response from {model} model.")
    print(response[model]["response"].message.content)  # Print the response for debugging
    return response[model]["response"].message.content  # Return the response from the Word2Vec model


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/query", methods=["POST"])
def api_query():
    payload = request.get_json(silent=True) or {}
    user_query = (payload.get("query") or "").strip()

    if not user_query:
        return jsonify({"error": "Query text is required."}), 400

    print(f"Received query: {user_query}")
    reply = process_query(user_query)

    return jsonify({
        "status": "received",
        "query": user_query,
        "reply": reply,
    })


if __name__ == "__main__":
    rag.init() 
    app.run(debug=True)