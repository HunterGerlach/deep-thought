#!/bin/bash

# Define the namespace where the operator and CheCluster will be deployed
NAMESPACE="openshift-operators"

# Path to the YAML files
SUBSCRIPTION_FILE="overlays/stable.yaml"
CHECLUSTER_FILE="checluster.yaml"

# Apply the Subscription for Dev Spaces Operator
echo "Applying Subscription for Dev Spaces Operator..."
oc apply -k ${SUBSCRIPTION_FILE}

# Wait for the Operator to be installed
echo "Waiting for Operator installation to complete..."
while true; do
  if [[ $(oc get csv -n ${NAMESPACE} -o jsonpath='{.items[?(@.spec.displayName=="Red Hat CodeReady Workspaces")].status.phase}') == "Succeeded" ]]; then
    echo "Operator installed successfully."
    break
  else
    echo "Waiting for operator to be ready..."
    sleep 10
  fi
done

# Apply the CheCluster resource
echo "Creating a CheCluster instance..."
oc apply -f ${CHECLUSTER_FILE}

echo "Waiting for CheCluster to be ready..."
while true; do
  if [[ $(oc get checluster -n ${NAMESPACE} -o jsonpath='{.items[?(@.metadata.name=="checluster")].status.phase}') == "Running" ]]; then
    echo "CheCluster is ready."
    break
  else
    echo "Waiting for CheCluster to be ready..."
    sleep 10
  fi
done

CHE_ROUTE=$(oc get route -n ${NAMESPACE} -o jsonpath='{.items[?(@.metadata.name=="checluster")].spec.host}')
CHE_URL="https://${CHE_ROUTE}"
echo "CheCluster is ready at ${CHE_URL}"

echo "Installation script completed."
