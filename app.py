
import base64
import io
from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import requests
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def calculate_luminance(rgb):
    def channel_lum(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * channel_lum(r) + 0.7152 * channel_lum(g) + 0.0722 * channel_lum(b)

def contrast_ratio(color1, color2):
    lum1 = calculate_luminance(color1)
    lum2 = calculate_luminance(color2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return round((lighter + 0.05) / (darker + 0.05), 2)

@app.route("/audit", methods=["POST"])
def audit():
    data = request.json
    image_data = data.get("image_base64")

    if not image_data:
        return jsonify({"error": "No image provided"}), 400

    # Decode image
    image_bytes = base64.b64decode(image_data.split(",")[-1])
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_np = np.array(image)

    # Get dominant foreground and background colors (simplified)
    center_text_pixel = img_np[img_np.shape[0]//2, img_np.shape[1]//2]
    corner_background_pixel = img_np[10, 10]

    contrast = contrast_ratio(center_text_pixel, corner_background_pixel)
    passes = contrast >= 4.5

    findings = [{
        "category": "Color Contrast",
        "layer": "Central text area",
        "issue": "Poor color contrast" if not passes else "Passes WCAG AA",
        "contrast_ratio": contrast,
        "threshold": 4.5,
        "suggestion": "Increase text/background contrast" if not passes else "None"
    }]

    return jsonify({"findings": findings})

@app.route("/")
def index():
    return "Accessibility audit service is running."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
