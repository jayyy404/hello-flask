from flask import Flask, jsonify, request, render_template
import json

app = Flask(__name__)

# Load data from JSON
with open("diseases.json") as f:
    diseases_data = json.load(f)

# Get list of all symptoms
@app.route('/symptoms', methods=['GET'])
def get_symptoms():
    symptoms = set()
    for disease in diseases_data:
        symptoms.update(disease["symptoms"])
    return jsonify(sorted(symptoms))

# Predict disease based on symptoms
@app.route('/predict', methods=['POST'])
def predict_disease():
    data = request.get_json()
    symptoms = set(data.get("symptoms", []))

    for disease in diseases_data:
        if symptoms.issubset(set(disease["symptoms"])):
            return jsonify({"disease": disease["name"]})

    return jsonify({"disease": None})

# Serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
