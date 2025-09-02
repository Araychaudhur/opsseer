import requests
import json

# Define the GATEWAY endpoint for the docqa service
url = "http://localhost:8000/route/docqa"
question = "What are the rollback steps for a bad deployment?"

# Send the request THROUGH THE GATEWAY
print(f"Sending question THROUGH THE GATEWAY to DocQA service: '{question}'")
try:
    response = requests.post(url, json={"query": question})

    if response.status_code == 200:
        print("Success! Response from server:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: Server responded with status code {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: Could not connect to the gateway at {url}.")
    print("Please ensure the 'ai-gateway' and 'docqa' containers are running.")