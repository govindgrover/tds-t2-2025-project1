"""
Sole reason of existance of this file is to test the API endpoints easily. :)
"""

import base64
import requests
import json

# Replace with your actual image path
# Optional: remove or set to None if no image
image_path = None

# Prepare the base64 image
encoded_image = None
if image_path:
	with open(image_path, "rb") as img_file:
		encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

# Your question here
# question = input("Enter Question: ")
question = 'cat vs dog?'

# Prepare the payload
payload = {
	"question": question,
	"image": encoded_image
}

# Send the POST request
response = requests.post(
	"http://127.0.0.1:8000/api/ask/",
	headers={"Content-Type": "application/json"},
	data=json.dumps(payload)
)

# For not formatting json everytime by copying-pasting
with open('./resp.json', 'w') as f:
	json.dump(response.json(), f, indent=4)
print('View: resp.json')


# curl "https://tds.govindgrover.com/api/ask/" -H "Content-Type: application/json" -d "{\"question\": \"cat vs dog\"}"

