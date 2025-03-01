from flask import Flask, request, jsonify, render_template
import openai

app = Flask(__name__)
openai.api_key = "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"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/get_resources', methods=['POST'])
def get_resources():
    data = request.json
    user_query = data.get("query")
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an assistant helping formerly incarcerated individuals find resources in Philadelphia."},
                  {"role": "user", "content": user_query}],
        max_tokens=100
    )
    
    try:
        resources = response["choices"][0]["message"]["content"]
        return jsonify({"resources": resources})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
