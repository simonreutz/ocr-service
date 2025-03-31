from flask import Flask, request, jsonify
from flask_cors import CORS
from paddleocr import PaddleOCR
from PIL import Image
import io

app = Flask(__name__)
CORS(app)
ocr = PaddleOCR(use_angle_cls=True, lang='en')

@app.route('/ocr', methods=['POST'])
def parse_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    image_file = request.files['image']
    image = Image.open(image_file.stream).convert("RGB")
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    result = ocr.ocr(img_bytes, cls=True)
    texts = [line[1][0] for block in result for line in block]
    session_data = {
        'distance_km': extract_value(texts, ['km']),
        'duration_min': extract_value(texts, ['min']),
        'avg_pace': extract_pace(texts),
        'type': extract_type(texts),
    }
    return jsonify(session_data)

def extract_value(texts, keywords):
    for t in texts:
        for k in keywords:
            if k in t:
                try:
                    return float(t.split(k)[0].strip())
                except:
                    continue
    return None

def extract_pace(texts):
    for t in texts:
        if ':' in t and 'min/km' in t:
            return t.strip()
    return None

def extract_type(texts):
    types = ['Easy', 'Interval', 'Long', 'Tempo', 'Recovery']
    for t in texts:
        for tp in types:
            if tp.lower() in t.lower():
                return tp + ' Run'
    return 'Easy Run'

if __name__ == '__main__':
    app.run()
