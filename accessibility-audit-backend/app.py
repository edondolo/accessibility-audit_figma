from flask import Flask, request, jsonify
import openai
import base64
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        image_base64 = data.get("image")

        prompt = '''
You are an expert in accessibility and WCAG 2.2 compliance.

Analyze the screenshot below for accessibility issues. Identify:
- Color contrast problems
- Text size and spacing issues
- Tap target sizing
- Alt text/image labeling problems
- General layout accessibility failures

Return findings grouped like this:
{
  "Color Contrast": [ { "issue": "...", "element": "...", "recommendation": "..." } ],
  "Alt Text": [ { "issue": "...", "element": "...", "recommendation": "..." } ],
  ...
}
Be brief, actionable, and don’t describe the whole image.
'''

        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000
        )

        result_text = response.choices[0].message.content
        return jsonify({ "result": result_text })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500
