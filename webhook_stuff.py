import requests
import string
import random
import time
import os
import sys
import json
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = Thread(target=run)
    thread.start()

# Constants
RANDOM_STRING_LENGTH = 5
WAIT_TIME_SUCCESS = 3
WAIT_TIME_FAILURE = 25

# Load configuration from config.json
with open("config.json", "r") as file:
    config = json.load(file)
    discord_webhook_url = config["discord_webhook_url"]

# Function to generate a random string
def generate_random_string(length):
    return "s" + ''.join(random.choices(string.ascii_lowercase, k=length))

# Function to send URL to Discord webhook
def send_url_to_discord(url):
    payload = {"content": f"Sent to URL: {url}"}
    return requests.post(discord_webhook_url, json=payload)

# Start the Flask server to keep the script alive
keep_alive()

# Continuously generate and send random URLs to Discord webhook
try:
    while True:
        random_suffix = generate_random_string(RANDOM_STRING_LENGTH)
        url = f"https://prnt.sc/{random_suffix}"

        print(f"Testing {random_suffix}...")

        response = send_url_to_discord(url)

        if response.ok:
            print(f"Successfully sent to URL: {url}")
        else:
            print(f"Failed to send URL: {url}")

        time.sleep(WAIT_TIME_SUCCESS)

except KeyboardInterrupt:
    print("Script interrupted manually. Exiting...")
    sys.exit(0)
except Exception as e:
    print(f"An error occurred: {e}")
    time.sleep(WAIT_TIME_FAILURE)

    # Restart the script
    python = sys.executable
    os.execl(python, python, *sys.argv)
