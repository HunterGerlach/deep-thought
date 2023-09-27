#!/bin/bash

# Check if environment variables are set
if [[ -z "$PROJECT_NAME" ]]; then
  echo "PROJECT_NAME is not set. Exiting."
  exit 1
fi

# Function to check command status
check_status() {
  if [[ $? != 0 ]]; then
    echo "Error executing command $1, exiting."
    exit 1
  fi
}

# Create new project
oc new-project $PROJECT_NAME
check_status "oc new-project"

# Apply ConfigMap
oc apply -f configmap.yaml
check_status "oc apply -f configmap.yaml"

# Apply Secrets
oc apply -f secrets.yaml -n $PROJECT_NAME
check_status "oc apply -f secrets.yaml"

# Apply Deployment
oc apply -f deployment.yaml -n $PROJECT_NAME
check_status "oc apply -f deployment.yaml"

# Apply Service
oc apply -f service.yaml -n $PROJECT_NAME
check_status "oc apply -f service.yaml"

# Apply Route
oc apply -f route.yaml -n $PROJECT_NAME
check_status "oc apply -f route.yaml"
