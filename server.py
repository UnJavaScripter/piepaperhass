import os
from flask import Flask, request, jsonify
from display_controller.handler import DisplayHandler
import requests
import logging
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

with open("./entities.json", "r") as json_file:
    entities = json.load(json_file)

url = "http://homeassistant.local:8123/api/states"
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
    return jsonify({'message': 'HASS queried!'}), 200

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
