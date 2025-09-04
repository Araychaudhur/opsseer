import requests
import json

# --- 1. Define the "Golden" Question-Answer Dataset ---
# These are questions and the key phrases we expect in the answer.
evaluation_set = [
    {
        "question": "What script is used for a rollback?",
        "expected_answer_fragment": "deploy-v2.ps1"
    },
    {
        "question": "How do you stop long-running queries?",
        "expected_answer_fragment": "pg_terminate_backend"
    },
    {
        "question": "What is the last known good version for the payments service?",
        "expected_answer_fragment": "v1.2.5"
    }
]

# --- 2. Run the Evaluation Loop ---
gateway_url = "http://localhost:8000/route/docqa"
correct_answers = 0

print("--- Running DocQA Evaluation ---")

for i, pair in enumerate(evaluation_set):
    question = pair["question"]
    expected = pair["expected_answer_fragment"]

    print(f"\n[{i+1}/{len(evaluation_set)}] Asking: '{question}'")

    try:
        response = requests.post(gateway_url, json={"query": question})

        if response.status_code == 200:
            result = response.json()
            actual_answer = result.get("answer", "")

            print(f"  -> AI Answer: '{actual_answer}'")

            if expected.lower() in actual_answer.lower():
                print("  -> \u2705 Correct")
                correct_answers += 1
            else:
                print(f"  -> \u274c Incorrect. Expected to find '{expected}'.")
        else:
            print(f"  -> \u274c Error: Server responded with status code {response.status_code}")

    except requests.exceptions.ConnectionError:
        print(f"  -> \u274c Error: Could not connect to the gateway.")

# --- 3. Print the Final Report ---
accuracy = (correct_answers / len(evaluation_set)) * 100
print("\n--- DocQA Evaluation Report ---")
print(f"Correct Answers: {correct_answers}/{len(evaluation_set)}")
print(f"Accuracy: {accuracy:.1f}%")
print("-----------------------------")