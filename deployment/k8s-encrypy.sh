#!/bin/bash

# Function to encode with base64 depending on platform
encode_base64() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -n "$1" | base64 -b0
  else
    echo -n "$1" | base64 -w0
  fi
}

# Main function to process and encode secret file
encode_secret_file() {
  local input_file=$1
  local output_file=$2
  local in_data_section=false

  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^data:$ ]]; then
      in_data_section=true
      echo "$line"
      continue
    fi

    if $in_data_section; then
      if [[ "$line" =~ ^[[:space:]] ]]; then
        key=$(echo "$line" | awk -F': ' '{print $1}')
        value=$(echo "$line" | awk -F': ' '{print $2}')
        encoded_value=$(encode_base64 "$value")
        echo "  $key: $encoded_value"
      else
        in_data_section=false
      fi
    fi

    if ! $in_data_section; then
      echo "$line"
    fi
  done < "$input_file" > "$output_file"
}

# Display usage instructions
usage() {
  echo "Usage: $0 [-h] <input_file> <output_file>"
  echo
  echo "Converts a Kubernetes Secret YAML file to a version with base64 encoded values."
  echo
  echo "Arguments:"
  echo "  input_file    Path to the input Kubernetes Secret YAML file"
  echo "  output_file   Path to save the encoded output file"
  echo
  echo "Options:"
  echo "  -h            Display this help and exit"
}

# Check for help option
if [[ "$1" == "-h" ]]; then
  usage
  exit 0
fi

# Check number of arguments
if [ "$#" -ne 2 ]; then
  usage
  exit 1
fi

# Run the encoding function with the provided files
encode_secret_file "$1" "$2"
echo "Encoded secret saved to $2"
