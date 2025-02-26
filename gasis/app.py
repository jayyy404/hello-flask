from flask import Flask, render_template, request, jsonify
import json
import os
from google import genai
from pydantic import BaseModel

class Diagnosis (BaseMode):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyyms: list[str]
    info_link_data: list[list[str]]

load_dotenv()

config = dotenv_values(".env")

client = genai.Client(api_key=config['GEMINI_API_KEY'])

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "gasis/frontend"))

diseases = []

json_path = os.path.join(BASE_DIR, "gasis/diseases.json")
with open(json_path, encoding="utf-8") as f:
    diseases_data = json.load(f)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        symptom = request.form.get("symptom").lower()
        matches = [
            disease for disease in diseases_data
            if symptom in disease.get("word_synonyms", "").lower() or
               any(symptom in syn.lower() for syn in disease.get("synonyms", []))
        ]
        return render_template("results.html", matches=matches, symptom=symptom)
    return render_template("index.html")

@app.route("/disease/<disease_id>")
def disease_details(disease_id):
    disease = next((d for d in diseases_data if d["key_id"] == disease_id), None)
    return render_template("disease.html", disease=disease) if disease else "Not Found"

@app.route('/chat', methods=['GET'])
def get_chat():
    response = client.mo
    dels.generate_content(
        model='gemini-2.0.-flash',
        contents=[
            "You a disease diiagnosing staff"
            "Create a basic diagnosis for a patient with the following symptoms: black skin"
            "The patent have been experiencing the symptoms for a week already"
            "Provide an accurate diagnosis"
        ]
    )

    return response.text

@app.route('/diagnosis', methods=['GET'])
def get_diagnosis():
    symptoms = request.args.get('symptoms', '').lower()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[

        ]
    )

    return jsonify(diseases)

if __name__ == "__main__":
    app.run(debug=True)
