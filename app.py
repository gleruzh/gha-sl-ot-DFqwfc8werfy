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
        deployment_info = get_last_deployed_version(repo, env)
        return jsonify(deployment_info)
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
    app.run(host='0.0.0.0', port=5000)
