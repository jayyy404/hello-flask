from flask import Flask, render_template, request, jsonify
import json
import os
from dotenv import load_dotenv, dotenv_values
import google.generativeai as genai

from pydantic import BaseModel


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Diagnosis(BaseModel):
    
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str
    synonyms: str
    info_link_data: list[list[str]]


load_dotenv()
config = dotenv_values(".env")

genai.configure(api_key=config['GEMINI_API_KEY'])


app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "sapasap/frontend"))


json_path = os.path.join(BASE_DIR, "sapasap/diseases.json")
with open(json_path, encoding="utf-8") as f:
    diseases_data = json.load(f)


def generate_diagnosis(symptoms):
    model = genai.GenerativeModel("gemini-2.0-flash")

    response = model.generate_content(f"""
        This is the existing data in JSON format: {json.dumps(diseases_data)}
        Match the closest disease with the following symptoms: {symptoms}
        Include the info_link_data in the response.
        Return the top three matching items in JSON format.
    """)

    # Ensure the response is valid JSON
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"error": "Response is not valid JSON", "raw_response": response.text}



@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        symptom = request.form.get("symptom").lower()
        matches = generate_diagnosis(symptom)
        return render_template("results.html", matches=matches, symptom=symptom)
    return render_template("index.html")


@app.route("/disease/<disease_id>")
def disease_details(disease_id):
    disease = next((d for d in diseases_data if d["key_id"] == disease_id), None)
    return render_template("disease.html", disease=disease) if disease else "Not Found"


@app.route('/diagnosis', methods=['GET'])
def get_diagnosis():
    symptoms = request.args.get('symptoms', '').lower()
    matches = generate_diagnosis(symptoms)
    return jsonify(matches)


@app.route("/ai_solution", methods=["GET"])
def ai_solution():
    disease_name = request.args.get("disease_name", "")

    if not disease_name:
        return jsonify({"solution": "No disease name provided."})

    model = genai.GenerativeModel("gemini-2.0-flash")

    response = model.generate_content(
        f"Provide a simple treatment or solution for {disease_name}. Keep it clear and concise for a general audience."
    )

    return jsonify({"solution": response.text})



if __name__ == "__main__":
    app.run(debug=True)
    