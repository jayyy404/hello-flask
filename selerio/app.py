from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

# Get the directory where the script is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "diseases.json")

# Load the disease data from the JSON file
try:
    with open(JSON_FILE, "r") as file:
        diseases = json.load(file)
except FileNotFoundError:
    diseases = []  # If file is missing, start with an empty list

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diseases Information</title>
    <script>
        function searchDisease() {
            let query = document.getElementById("search").value.toLowerCase();
            fetch(`/search?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    let resultsDiv = document.getElementById("results");
                    resultsDiv.innerHTML = "";
                    if (data.length === 0) {
                        resultsDiv.innerHTML = "<p>No results found.</p>";
                    } else {
                        data.forEach(disease => {
                            let infoLink = disease.info_link_data.length ? `<a href="${disease.info_link_data[0][0]}" target="_blank">${disease.info_link_data[0][1]}</a>` : 'No Link Available';
                            resultsDiv.innerHTML += `<p><strong>${disease.primary_name}</strong> - ${infoLink}</p>`;
                        });
                    }
                });
        }
    </script>
</head>
<body>
    <h1>Diseases Information</h1>
    <input type="text" id="search" placeholder="Search for a disease..." onkeyup="searchDisease()">
    <div id="results"></div>
    
    <h2>All Diseases</h2>
    <ul>
        {% for disease in diseases %}
            <li><strong>{{ disease.primary_name }}</strong> - 
                <a href="{{ disease.info_link_data[0][0] if disease.info_link_data else '#' }}" target="_blank">
                {{ disease.info_link_data[0][1] if disease.info_link_data else 'No Link Available' }}
                </a>
            </li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, diseases=diseases)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    results = []

    for d in diseases:
        # Check if the query matches primary name, synonyms, or ICD codes
        if (query in d['primary_name'].lower() or
            any(query in syn.lower() for syn in d.get('synonyms', [])) or
            any(query in code['code'].lower() for code in d.get('icd10cm', []))):
            results.append(d)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
