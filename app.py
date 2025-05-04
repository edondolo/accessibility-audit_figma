from flask import Flask, request, jsonify
import openai
import base64
import os

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Accessibility Audit API is running."

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        image_data = data.get("image_base64", "")

        if not image_data:
            return jsonify({"error": "Missing image_base64"}), 400

        # Prepare base64 image for GPT-4 Vision
        image = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image_data}",
                "detail": "high"
            },
        }

        # Accessibility-focused prompt
        prompt = (
            "You are a senior accessibility expert. Analyze this UI screenshot for accessibility issues using WCAG 2.2 guidelines. "
            "Return a list of grouped findings with: issue type (e.g., color contrast, target size), severity, layer name (if mentioned), and fix recommendation. "
            "Use a JSON format structured like: [{layer, issue, wcag, details, fix}]."
        )

        # Send request to GPT-4 Vision
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    image
                ]}
            ],
            max_tokens=1000
        )

        raw = response.choices[0].message.content
        return jsonify({"raw": raw})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🟢 Required for Render to bind the correct port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
