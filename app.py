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
    url = f"https://api.github.com/repos/{os.getenv('USERNAME')}/{repo}/deployments"
    headers = {
        'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'
    }
    response = requests.get(url, headers=headers)
    
    # Ensure the response is valid JSON
    try:
        deployments = response.json()
    except ValueError:
        return 'Invalid JSON response from GitHub API'
    
    # Debug statement to check the structure of the response
    print(deployments)
    
    if isinstance(deployments, list):
        for deployment in deployments:
            if deployment.get('environment') == env:
                return deployment.get('sha', 'SHA not found')
        return 'No deployment found for this environment'
    else:
        return 'Unexpected response format from GitHub API'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
