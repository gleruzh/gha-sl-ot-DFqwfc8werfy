from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/deployments', methods=['GET'])
def get_deployments():
    env = request.args.get('env')
    if env:
        repo = os.getenv('REPO_NAME')
        last_deployed_version = get_last_deployed_version(repo, env)
        return jsonify({
            "environment": env,
            "last_deployed_version": last_deployed_version
        })
    else:
        return jsonify({"error": "Please provide an environment"}), 400

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
        return 'Invalid JSON response from GitHub API'
    
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
                return deployment.get('sha', 'SHA not found')
    
    return 'No successful deployment found for this environment'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
