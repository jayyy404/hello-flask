from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# Load JSON data
with open("diseases.json", "r") as file:
    diseases = json.load(file)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Disease API!"})

@app.route("/diseases", methods=["GET"])
def get_diseases():
    """Get a list of all diseases"""
    return jsonify(diseases)

@app.route("/disease/<key_id>", methods=["GET"])
def get_disease(key_id):
    """Get details of a specific disease by key_id"""
    disease = next((d for d in diseases if d["key_id"] == key_id), None)
    if disease:
        return jsonify(disease)
    return jsonify({"error": "Disease not found"}), 404

@app.route("/search", methods=["GET"])
def search_diseases():
    """Search for diseases by primary name or synonyms"""
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    results = [
        d for d in diseases
        if query in d["primary_name"].lower() or
        any(query in synonym.lower() for synonym in d.get("synonyms", []))
    ]

    return jsonify(results)

@app.route("/symptoms", methods=["GET"])
def get_symptoms():
    """Get a list of all unique symptoms and synonyms"""
    symptoms = set()

    for disease in diseases:
        if "word_synonyms" in disease and disease["word_synonyms"]:
            symptoms.update(disease["word_synonyms"].split(";"))
        if "synonyms" in disease and isinstance(disease["synonyms"], list):
            symptoms.update(disease["synonyms"])

    return jsonify(sorted(symptoms))

if __name__ == "__main__":
    app.run(debug=True)
