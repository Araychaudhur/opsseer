import os
import httpx
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# --- Configuration ---
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
AI_GATEWAY_URL = "http://ai-gateway:8000"

# Initialize the Slack Bolt App
app = App(token=SLACK_BOT_TOKEN)

@app.event("app_mention")
def handle_app_mention_events(body, say):
    """
    Handles events where the bot is @mentioned.
    Example: @OpsSeerBot what are the rollback steps?
    """
    user_query = body["event"]["text"].split(">", 1)[-1].strip()
    user = body["event"]["user"]

    say(f"Hello <@{user}>! I've received your query: '{user_query}'.\n\nContacting the AI Gateway, please wait a moment...")

    try:
        # Forward the query to the DocQA service via the gateway
        response = httpx.post(
            f"{AI_GATEWAY_URL}/route/docqa",
            json={"query": user_query},
            timeout=60.0
        )

        if response.status_code == 200:
            qa_result = response.json()
            answer = qa_result.get('answer', 'No answer found.')
            source = qa_result.get('source', 'Unknown source')

            say(
                text=f"Here's what I found:",
                blocks=[
                    {
                        "type": "section",
                        "text": { "type": "mrkdwn", "text": f"*Your Question*: {user_query}" }
                    },
                    {
                        "type": "section",
                        "text": { "type": "mrkdwn", "text": f"*AI Answer*:\n>{answer}\n\n*Source*: `{source}`" }
                    }
                ]
            )
        else:
            say(f"Sorry, I encountered an error trying to reach the DocQA service. It responded with status code {response.status_code}.")

    except httpx.RequestError:
        say("Sorry, I was unable to connect to the AI Gateway.")


def main():
    print("--- Starting Interactive Slack Bot ---")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()

if __name__ == "__main__":
    main()