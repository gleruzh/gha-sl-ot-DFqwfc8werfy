#!/bin/bash

# Run docker compose 
docker compose up -d

# Give the server a second to start up
sleep 1

# Test the /deployments endpoint for different environments
for env in qa dev stage prod
do
  echo "Testing environment: $env"
  curl -sq "http://localhost:8000/deployments?env=$env"
  # echo -e "\n"
done

# down compose
docker compose down