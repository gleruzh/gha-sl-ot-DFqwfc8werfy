#!/bin/bash

# Set env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the Flask application in the background
python app.py &

# Give the server a second to start up
sleep 1

# Test the /deployments endpoint for different environments
for env in qa dev stage prod
do
  echo "Testing environment: $env"
  curl -sq "http://localhost:5000/deployments?env=$env"
  # echo -e "\n"
done

# Kill the Flask application
kill $!
deactivate