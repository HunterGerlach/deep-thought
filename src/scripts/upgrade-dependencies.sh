#!/bin/bash

# Save the current virtual environment
CURRENT_ENV=$VIRTUAL_ENV

# Deactivate the current virtual environment if it exists
if [ -n "$CURRENT_ENV" ]; then
  deactivate
fi

# Backup current requirements.txt
cp requirements.txt requirements_backup.txt

# Create a virtual environment for the upgrade
python3 -m venv upgrade-env

# Activate the upgrade virtual environment
source upgrade-env/bin/activate

# Install current dependencies
if ! pip install -r requirements.txt; then
  echo "Installation failed. Restoring original requirements.txt."
  cp requirements_backup.txt requirements.txt
  exit 1
fi

# Upgrade all packages
if ! pip install --upgrade $(cat requirements.txt | cut -d = -f 1); then
  echo "Upgrade failed. Restoring original requirements.txt."
  cp requirements_backup.txt requirements.txt
  exit 1
fi

# Update requirements.txt with the new versions
pip freeze > requirements.txt

# Deactivate the upgrade virtual environment
deactivate

# Remove the upgrade virtual environment folder
rm -rf upgrade-env

# Reactivate the original virtual environment if it existed
if [ -n "$CURRENT_ENV" ]; then
  source $CURRENT_ENV/bin/activate
fi

# Optionally delete the backup
read -p "Upgrade complete. Delete backup (y/n)? " choice
if [ "$choice" == "y" ]; then
  rm requirements_backup.txt
  echo "Backup deleted."
else
  echo "Backup retained as requirements_backup.txt."
fi
