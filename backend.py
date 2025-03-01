from flask import Flask, jsonify, render_template, request
import os
from openai import OpenAI
import requests

app = Flask(__name__)
client = OpenAI(api_key="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")

DATASETS = {
    'food': 'C:\\Users\\Prashanth\\Downloads\\free_meal_sites.geojson',
    # 'housing': 'https://data.opendataphilly.org/resource/pha-housing-sites.json', 
    'mental_health': 'C:\\Users\\Prashanth\\Downloads\\DOH_CommunityMentalHealthCenters202106.geojson',
    # 'child_care': 'https://data.opendataphilly.org/resource/child-care-search.json',
    # 'medical_care': 'https://opendataphilly.org/datasets/dvrpcs-equity-through-access-map-toolkit.json',
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
    
    # Step 1: Use AI to determine relevant datasets
    dataset_list = ", ".join(DATASETS.keys())
    prompt = f"""
    A user in Philadelphia needs resources for {', '.join(user_needs)}. 
    Which datasets from the following list should be used? Only return relevant dataset keys:
    {dataset_list}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    relevant_keys = response.choices[0].message.content.strip().split(', ')

    # Step 2: Fetch relevant dataset data
    resources = []
    for key in relevant_keys:
        if key in DATASETS:
            dataset_url = DATASETS[key]
            dataset_response = requests.get(dataset_url)
            if dataset_response.status_code == 200:
                data = dataset_response.json()
                for item in data[:10]:  # Limit results for efficiency
                    resources.append({
                        "name": item.get("name", "Unknown"),
                        "lat": float(item.get("latitude", 0)),
                        "lng": float(item.get("longitude", 0)),
                        "description": item.get("description", "No description available"),
                        "category": key
                    })
    
    # Step 3: AI-powered summarization of resources
    summary_prompt = f"Summarize these resources for a user: {resources}"
    summary_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Summarize these resources for a user."},
            {"role": "user", "content": summary_prompt}],
        max_tokens=200
    )
    summary_text = summary_response.choices[0].message.content.strip()

    return jsonify({"resources": resources, "summary": summary_text})

if __name__ == '__main__':
    app.run(debug=True)