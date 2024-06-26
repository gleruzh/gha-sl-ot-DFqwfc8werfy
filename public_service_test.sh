#!/bin/bash

deployed_app_domain=gha-slack-app-test.onrender.com

# Test the /deployments endpoint for different environments
for env in qa dev stage prod
do
  echo "Testing environment: $env"
  curl -sq "https://$deployed_app_domain/deployments?env=$env"
done
