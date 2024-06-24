from flask import Flask, request, jsonify
from slack_bolt import App as SlackApp
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to test Slack bot token by posting a message to a channel
def test_bot_token(token, channel_id):
    client = WebClient(token=token)
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text="Testing Slack bot token"
        )
        print(f"Message posted successfully: {response['ts']}")
        return True
    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")
        return False

# Example usage
if __name__ == '__main__':
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
    SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")  # Replace with your Slack channel ID

    if not test_bot_token(SLACK_BOT_TOKEN, SLACK_CHANNEL_ID):
        print("Invalid Slack bot token or other error.")
    else:
        print("Slack bot token is valid and message was posted.")

# Initialize a Slack Bolt app
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

slack_app = SlackApp(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

# Initialize Flask app
app = Flask(__name__)
handler = SlackRequestHandler(slack_app)

@app.route('/slack/events', methods=['POST'])
def slack_events():
    # Add debug logging to ensure endpoint is hit
    print("Received Slack event")
    return handler.handle(request)

@app.route('/deployments', methods=['GET'])
def get_deployments():
    env = request.args.get('env')
    if not env:
        return jsonify({"error": "Please provide an environment"}), 400

    repo = os.getenv('REPO_NAME')
    deployment_info = get_last_deployed_version(repo, env)
    return jsonify(deployment_info)

@slack_app.command("/deployments")
def handle_deployments(ack, respond, command):
    ack()
    env = command['text'].strip()
    repo = os.getenv('REPO_NAME')

    if env == 'all':
        environments = ['dev', 'qa', 'stage', 'prod']  # Add all your environments here
        all_deployments = {}
        for environment in environments:
            deployment_info = get_last_deployed_version(repo, environment)
            all_deployments[environment] = deployment_info

        message = "\n".join([
            f"Environment: {env_info['environment']}\nSHA: {env_info['sha']}\nRef: {env_info['ref']}\nRef Type: {env_info['ref_type']}\n"
            for env_info in all_deployments.values()
        ])
        respond({"text": message})
    else:
        if not env:
            respond({"text": "Please provide an environment"})
            return

        deployment_info = get_last_deployed_version(repo, env)
        if "error" in deployment_info:
            respond({"text": deployment_info["error"]})
        else:
            message = (f"Environment: {deployment_info['environment']}\n"
                       f"SHA: {deployment_info['sha']}\n"
                       f"Ref: {deployment_info['ref']}\n"
                       f"Ref Type: {deployment_info['ref_type']}")
            respond({"text": message})

def get_last_deployed_version(repo, env):
    # Fetch all deployments for the repository
    deployments_url = f"https://api.github.com/repos/{os.getenv('USERNAME')}/{repo}/deployments"
    headers = {
        'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'
    }
    response = requests.get(deployments_url, headers=headers)

    # Ensure the response is valid JSON
    try:
        deployments = response.json()
    except ValueError:
        return {'error': 'Invalid JSON response from GitHub API'}

    # Filter deployments by environment and fetch statuses for each deployment
    for deployment in deployments:
        if deployment.get('environment') == env:
            deployment_id = deployment['id']
            statuses_url = f"https://api.github.com/repos/{os.getenv('USERNAME')}/{repo}/deployments/{deployment_id}/statuses"
            statuses_response = requests.get(statuses_url, headers=headers)

            try:
                statuses = statuses_response.json()
            except ValueError:
                continue

            # Check if the last status is 'success'
            if statuses and statuses[0]['state'] == 'success':
                ref = deployment.get('ref')
                sha = deployment.get('sha', 'SHA not found')

                # Determine if the ref is a tag or branch
                ref_type = 'branch'
                if ref.startswith('refs/tags/'):
                    ref_type = 'tag'
                    ref = ref[len('refs/tags/'):]
                elif ref.startswith('refs/heads/'):
                    ref = ref[len('refs/heads/'):]

                return {
                    'environment': env,
                    'sha': sha,
                    'ref': ref,
                    'ref_type': ref_type
                }

    return {'error': 'No successful deployment found for this environment'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
