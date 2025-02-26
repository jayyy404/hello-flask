from flask import Flask, render_template, request, jsonify
import json
import os
from dotenv import load_dotenv, dotenv_values
import google.generativeai as genai
from pydantic import BaseModel

class Diagnosis(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: list[str]
    synonyms: list[list[str]]

load_dotenv()

config = dotenv_values(".env")
client = genai.Client(api_key=config["GEMINI_API_KEY"])

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
json_path = os.path.join(BASE_DIR, "hallares", "diseases.json")

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "frontend"))

with open(json_path, encoding="utf-8") as f:
    app.diseases_data = json.load(f)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        symptom = request.form.get("symptom").lower()
        matches = [
            disease for disease in app.diseases_data
            if symptom in disease.get("word_synonyms", "").lower() or
               any(symptom in syn.lower() for syn in disease.get("synonyms", []))
        ]
        return render_template("results.html", matches=matches, symptom=symptom)
    return render_template("index.html")

@app.route("/disease/<disease_id>")
def disease_details(disease_id):
    disease = next((d for d in app.diseases_data if d["key_id"] == disease_id), None)
    return render_template("disease.html", disease=disease) if disease else "Not Found"

@app.route("/diagnosis", methods=["GET"])
def get_diagnosis():
    symptom = request.args.get("symptom", "").lower()  # Fix: Use 'request.args' for GET requests
    matches = [
        disease for disease in app.diseases_data
        if symptom in disease.get("word_synonyms", "").lower() or
           any(symptom in syn.lower() for syn in disease.get("synonyms", []))
    ]

    # Create the contents data to send to the Gemini API
    contents = {
        "content": "This is the existing data in JSON format " + json.dumps(matches)
    }

    # Correct the API call by passing the 'contents' variable properly
    response = client.models.generate_content(
        model="gemini:2.0-flash",
        **contents  # Unpack the contents dictionary
    )

    # Return a JSON response with the content from the model
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
