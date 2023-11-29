#!/bin/bash

# Function to encode with base64 depending on platform
encode_base64() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -n "$1" | base64 -b0
  else
    echo -n "$1" | base64 -w0
  fi
}

# Function to update the key-value in the YAML data section
update_yaml() {
  local file=$1
  local key=$2
  local new_value=$3
  local type=$4
  local temp_file=$5

  if [ "$type" == "secret" ]; then
    # Check if value is already base64 encoded
    read -p "Is the value already base64 encoded? (y/n): " is_encoded
    if [ "$is_encoded" != "y" ]; then
      new_value=$(encode_base64 "$new_value")
    fi
  fi

  # Use awk to update the file
  awk -v key="$key" -v val="$new_value" -v update=0 '
    $1 == "data:" { update=1 }
    update && $1 == key ":" {
      print "  " key ": " val
      next
    }
    { print }
  ' "$file" > "$temp_file" && mv "$temp_file" "$file"
}

# Function to apply the updated file
apply_file() {
  local output_file=$1
  read -p "Do you want to apply the updated file to the cluster? (y/n): " apply_choice
  if [ "$apply_choice" == "y" ]; then
    oc apply -f "$output_file"
    echo "Applied $output_file to the cluster."
  else
    echo "Skipped applying $output_file to the cluster."
  fi
}

# Display usage instructions
usage() {
  echo "Usage: $0 [-h] <file_path> <type> <output_file>"
  echo
  echo "Updates a key-value pair in the data section of a Kubernetes YAML file (Secret or ConfigMap)."
  echo
  echo "Arguments:"
  echo "  file_path        Path to the Kubernetes YAML file"
  echo "  type             Type of the Kubernetes object (secret/config)"
  echo "  output_file      Name of the output file to save changes"
  echo
  echo "Options:"
  echo "  -h               Display this help and exit"
}

# Check for help option
if [[ "$1" == "-h" ]]; then
  usage
  exit 0
fi

# Main function
main() {
  if [ "$#" -ne 3 ]; then
    usage
    exit 1
  fi

  local file_path=$1
  local file_type=$2
  local output_file=$3

  if [[ ! -f "$file_path" ]]; then
    echo "File does not exist"
    exit 1
  fi

  # Copy original file to output file
  cp "$file_path" "$output_file"

  local continue_update="y"
  local temp_file="temp_k8s_edit.yaml"

  while [[ $continue_update == "y" ]]; do
    echo "Available keys in the data section:"
    awk '/data:/ { show=1; next } /^  [^ ]+: / && show { print }' "$output_file"  # Extract and list keys in data section

    read -p "Enter the key you want to update (in the data section): " selected_key
    read -sp "Enter the new value for $selected_key: " new_value
    echo

    update_yaml "$output_file" "$selected_key" "$new_value" "$file_type" "$temp_file"
    echo "Updated $selected_key in the data section of $output_file"

    read -p "Do you want to update another key? (y/n): " continue_update
  done

  # Apply the updated file to the cluster
  apply_file "$output_file"

  # Clean up
  [ -f "$temp_file" ] && rm "$temp_file"
}

# Run the main function with arguments
main "$@"
