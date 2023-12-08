#!/usr/bin/env bash

# Function to encode with base64 depending on platform
encode_base64() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -n "$1" | base64 -b0
  else
    echo -n "$1" | base64 -w0
  fi
}

# Process a line and add to the appropriate Kubernetes object
process_line() {
  local key=$1
  local value=$2
  local type=$3

  if [ "$type" == "secret" ]; then
    local encoded_value=$(encode_base64 "$value")
    echo "  $key: $encoded_value"
  elif [ "$type" == "config" ]; then
    echo "  $key: \"$value\""
  fi
}

# Main function to process files
process_file() {
  local file=$1
  local name=$2
  local type=$3

  local kind
  if [ "$type" == "secret" ]; then
    kind="Secret"
  elif [ "$type" == "config" ]; then
    kind="ConfigMap"
  fi

  # Output file name
  local output_file="${name}.yaml"

  # Redirect all output to file
  exec > "$output_file"

  echo "apiVersion: v1"
  echo "kind: $kind"
  echo "metadata:"
  echo "  name: $name"
  echo "type: Opaque"
  echo "data:"

  # Read each line and process
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" || "$line" =~ ^\# ]] && continue
    local key=$(echo "$line" | cut -d '=' -f 1)
    local value=$(echo "$line" | cut -d '=' -f 2-)
    process_line "$key" "$value" "$type"
  done < "$file"

  echo "$kind written to $output_file"
}

# Display usage instructions
usage() {
  echo "Usage: $0 <file_path> <k8s_object_name> <secret|config>"
  echo
  echo "Converts a .env file to a Kubernetes Secret or ConfigMap."
  echo
  echo "Arguments:"
  echo "  file_path        Path to the .env file"
  echo "  k8s_object_name  Name for the Kubernetes object (omit the filetype)"
  echo "  type             Type of Kubernetes object (secret|config)"
  echo
  echo "Options:"
  echo "  -h               Display this help and exit"
}

# Check for help option
if [[ "$1" == "-h" ]]; then
  usage
  exit 0
fi

# Check number of arguments
if [ "$#" -ne 3 ]; then
  usage
  exit 1
fi

# Process the provided file
process_file "$1" "$2" "$3"
