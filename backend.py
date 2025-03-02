from flask import Flask, jsonify, render_template, request
import os
import requests
import json

app = Flask(__name__)

# Hugging Face API setup
HUGGINGFACE_API_KEY = "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"  # Replace with your actual Hugging Face API key
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/gpt2"  # GPT-2 model API

DATASETS = {
    'food': 'C:\\Users\\Prashanth\\Downloads\\free_meal_sites.geojson',
    'mental_health': 'C:\\Users\\Prashanth\\Downloads\\DOH_CommunityMentalHealthCenters202106.geojson',
    'esl': 'C:\\Users\\Prashanth\\Downloads\\esl_class_locations.geojson'
}

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/get_resources', methods=['POST'])
def get_resources():
    user_needs = request.json.get('needs', [])
    print(f"User needs: {user_needs}")

    # Step 1: Filter datasets based on selected needs
    selected_datasets = [key for key in DATASETS.keys() if key in user_needs]
    print(f"Selected datasets: {selected_datasets}")

    if not selected_datasets:
        return jsonify({"error": "No valid resources selected"}), 400

    resources = {"type": "FeatureCollection", "features": []}

    try:
        for key in selected_datasets:
            dataset_path = DATASETS[key]
            if os.path.exists(dataset_path):
                with open(dataset_path, 'r') as file:
                    data = json.load(file)
                    print(f"Loaded data for {key}: {data}")

                for item in data.get('features', [])[:10]:  # Limit results for efficiency
                    properties = item.get("properties", {})
                    geometry = item.get("geometry", {})

                    if key == "food":
                        name = properties.get('site_name', 'Unknown')
                        description = properties.get('category', 'No description available')
                        lat = geometry.get('coordinates', [])[1]
                        lon = geometry.get('coordinates', [])[0]
                    else:
                        name = properties.get('provider', 'Unknown')
                        description = properties.get('description', 'No description available')
                        lat = properties.get('lat')
                        lon = properties.get('lon')

                    if lat == 0 or lon == 0:
                        print(f"Warning: Missing or invalid coordinates for {name}")
                    else:
                        resources["features"].append({
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [lon, lat]
                            },
                            "properties": {
                                "name": name,
                                "description": description
                            }
                        })
            else:
                print(f"Dataset not found: {dataset_path}")
                return jsonify({"error": f"Dataset not found: {dataset_path}"}), 500

        return jsonify(resources)  # Successfully return the GeoJSON response

    except Exception as e:
        print(f"Error processing resources: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
