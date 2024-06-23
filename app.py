from flask import Flask, request, jsonify
from slack_bolt import App as SlackApp
from slack_bolt.adapter.flask import SlackRequestHandler
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize a Slack Bolt app
slack_app = SlackApp(token=os.getenv("SLACK_BOT_TOKEN"))

# Initialize Flask app
app = Flask(__name__)
handler = SlackRequestHandler(slack_app)

@app.route('/slack/events', methods=['POST'])
def slack_events():
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
    if not env:
        respond({"text": "Please provide an environment"})
        return

    repo = os.getenv('REPO_NAME')
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
