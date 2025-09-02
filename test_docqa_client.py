import requests
import json

# Define the API endpoint and the question
url = "http://localhost:8003/ask"
question = "What are the rollback steps for a bad deployment?"

# Send the request
print(f"Sending question to DocQA service: '{question}'")
try:
    response = requests.post(url, json={"query": question})

    if response.status_code == 200:
        print("Success! Response from server:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: Server responded with status code {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: Could not connect to the service at {url}.")
    print("Please ensure the 'docqa' container is running and has finished starting up.")