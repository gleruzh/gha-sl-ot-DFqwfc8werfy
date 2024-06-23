from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/deployments', methods=['GET'])
def get_deployments():
    env = request.args.get('env')
    if env:
        repo = 'your-repo-name'  # Replace with your actual repo name
        last_deployed_version = get_last_deployed_version(repo, env)
        return jsonify({
            "environment": env,
            "last_deployed_version": last_deployed_version
        })
    else:
        return jsonify({"error": "Please provide an environment"}), 400

def get_last_deployed_version(repo, env):
    url = f"https://api.github.com/repos/your-username/{repo}/deployments"
    headers = {
        'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'
    }
    response = requests.get(url, headers=headers)
    deployments = response.json()

    for deployment in deployments:
        if deployment['environment'] == env:
            return deployment['sha']
    return 'No deployment found for this environment'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
