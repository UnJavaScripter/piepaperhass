import os
from flask import Flask, request, jsonify
import requests
import logging
import json
from dotenv import load_dotenv
import importlib

# Load environment variables from .env file
load_dotenv()

waveshare_display_name = os.environ.get("WAVESHARE_DISPLAY_NAME")

if waveshare_display_name:
    try:
        module = __import__(f'display_controller.handler_{waveshare_display_name}', fromlist=['DisplayHandler'])
        DisplayHandler = getattr(module, 'DisplayHandler')

    except ImportError as e:
        print(f"Error importing module or class: {e}")
else:
    print(f"A WAVESHARE_DISPLAY_NAME env variable needs to be set. Example: WAVESHARE_DISPLAY_NAME=epd2in7")



app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'entities.json'), 'r') as json_file:
    entities = json.load(json_file)

url = 'http://homeassistant.local:8123/api/states'
headers = {
    'Authorization': f'Bearer {os.environ.get("HASS_TOKEN")}',
    'Content-Type': 'application/json'
}

@app.route('/', methods=['GET'])
def root():
    print("get req!")

    return jsonify({'message': 'nothing here!'}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    logging.info("Webhook received!")
    data = request.json
    logging.info(f'should update {data["entity_id"]} with status: {data["state"]}')
    state = True if data["state"] == "on" else False
    dh.update_card_state(data["entity_id"], state)
    return jsonify({'message': f'HASS queried: {data["entity_id"]} = {state}'}), 200

def query_ha(entity_id):
    response = requests.get(f'{url}/{entity_id}', headers=headers)
    if response.status_code == 200:
        if response.json()["state"] == "on":
            return True
        else:
            return False
    else:
        return False
    logging.info(response.json()["state"])

for entity in entities:
    current_state = query_ha(entity["entity_id"])
    entity["state"] = current_state
    logging.info(entity["state"])

dh = DisplayHandler(entities)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
