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
    'medical_care': 'C:\\Users\\Prashanth\\Downloads\\Health_Centers.geojson',
    'housing': 'C:\\Users\\Prashanth\\Downloads\\HousingCounselingAgencies.geojson',
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
                    print(f"Loaded data for {key}")

                for item in data.get('features', [])[:10]:  # Limit results for efficiency
                    properties = item.get("properties", {})
                    geometry = item.get("geometry", {})

                    # Extract coordinates
                    lat = properties.get('lat')
                    lon = properties.get('lon')

                    if lat is None or lon is None:
                        if "coordinates" in geometry and len(geometry["coordinates"]) == 2:
                            lon, lat = geometry["coordinates"]

                    # Ensure valid coordinates
                    if lat is None or lon is None or lat == 0 or lon == 0:
                        print(f"Warning: Missing or invalid coordinates for {properties.get('AGENCY', 'Unknown')}")
                        continue

                    # Handle specific datasets (food, housing, medical_care, ESL)
                    if key == "food":
                    # Food-specific fields
                        name = properties.get('site_name', 'Unknown Food Site')
                        address = properties.get('address', 'No address available')
                        phone = properties.get('phone_number', 'No phone number available')
                        website = properties.get('website', 'No website available')

                    elif key == "housing":
                    # Housing-specific fields
                        name = properties.get('AGENCY', 'Unknown Housing Agency')
                        address = properties.get('STREET_ADDRESS', 'No address available')
                        phone = properties.get('PHONE_NUMBER', 'No phone number available')
                        website = properties.get('WEBSITE_URL', 'No website available')

                    elif key == "medical_care":
                        # Medical care-specific fields
                        name = properties.get('NAME', 'Unknown Medical Care Center')
                        address = properties.get('FULL_ADDRESS', 'No address available')
                        phone = properties.get('PHONE', 'No phone number available')
                        website = properties.get('WEBSITE', 'No website available')

                    elif key == "esl":
                        # ESL-specific fields
                        name = properties.get('provider', 'Unknown ESL Provider')
                        address = properties.get('address_1', 'No address available')
                        phone = properties.get('No phone number available')
                        website = properties.get('website', 'No website available')

                    else:
                        # Default extraction for other datasets (if any)
                        name = properties.get('name', 'Unknown')
                        website = properties.get('website', 'No website available')

                    if website not in ['No website available', '', None]:
                        if not website.startswith('http'):
                            website = 'https://' + website

                    description = (
                        f"Address: {address}<br>"
                        f"Phone: {phone}<br>"
                        f"Website: <a href='{website}' target='_blank'>{website}</a>"
                    )

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

        return jsonify(resources)

    except Exception as e:
        print(f"Error processing resources: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
